## Analyse biovolumes

biov_msk = biovolume.salem.roi(shape=shpf)
biov_msk = biov_msk.where(biov_msk < 6e5)

import seaborn as sns
## Stats combined with DEM data
for t in biov_msk.time:
	biov_t = biov_msk.sel(time=t).to_pandas()

	detr_msk = detrended_mean.detrended_mean.sel(time=t).salem.roi(shape=shpf)
	detr_msk_pd = detr_msk.to_pandas()

	combo = pd.concat({'biovol':biov_t.stack(), 'elev':detr_msk_pd.stack()},axis=1)
	combo = combo.dropna()

	periods = pd.interval_range(start=-0.4, end=0.8, periods=12)
	elev_bins = pd.cut(combo.elev, bins=periods)

	combo['elev_bin'] = elev_bins

	# Simple approach is just to get mean ratio in each category
	combo.groupby(elev_bins)['biovol'].agg(['mean'])
	# Also check how many observations are in each category
	combo.groupby(elev_bins)['biovol'].agg(['count']) 

	# Box plot
	combo['elev_bin'] = elev_bins
	# There are a lot of ratio outliers, to hide them set fliersize to zero
	figure(), sns.boxplot(x='elev_bin', y='biovol', data=combo, fliersize=0,
		color='#E74C3C')
	# And then need to adjust y axis as it is still scaled to include fliers
	plt.ylim(5,9e4)
	ticks, labels = plt.xticks()
	new_labels = [-0.35,-0.25,-0.15,-0.05,0.05,0.15,0.25,0.35,0.45,0.55,0.65,0.75]
	plt.xticks(ticks,new_labels)
	title(t.values)