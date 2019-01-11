
detrended = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.nc',
	chunks={'x':1000, 'y':1000})
classified = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_refl_class.nc',
	chunks={'x':1000, 'y':1000}) 

cmap = 

combo = pd.concat([classified.classified.stack(dim=('x','y')).to_pandas(), detrended.detrended.stack(dim=('x','y')).to_pandas()], axis=1)


elev_by_class = detrended.groupby(classified.classified).mean()

"""
could bin the elevation data for each category first?

add args - to fix ValueError: range parameter must be finite.

"""
values = detrended.detrended.groupby(classified.classified).apply(np.histogram, range=(-1,1), bins=20)


detrended['x'] = classified['x']
detrended['y'] = classified['y']

plt.figure()
names = ['Water', 'Snow', 'CI', 'LA', 'HA', 'CC']
for classv in np.arange(1, 7, 1):
	just_class = detrended.detrended.where(classified.classified == classv) \
		.stack(dim=('x','y')).to_pandas().dropna()
	ax = plt.subplot(1, 7, classv+1)
	sns.boxenplot(data=just_class, ax=ax)
	plt.ylim(-0.75, 0.50)
	plt.title(names[classv-1])
	ax.axes.xaxis.set_ticklabels([])
	if classv > 1:
		ax.axes.yaxis.set_ticklabels([])

vals,bins,patches = classified.classified.plot.hist(bins=7,range=(0,7))
vals_perc = 100 / vals.sum() * vals
figure(),plt.bar(bins[:-1],vals_perc) 
ylabel('% coverage of image')
xlabel('Surface class')