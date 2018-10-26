# calculate_bio_loading
import pandas as pd
import statsmodels.api as sm

counts = pd.read_excel('/home/at15963/Dropbox/work/data/field_processed_2017/GrIS_2017_Cell counts_with_vols.xlsx', 
	sheet_name='Cells per ml')
counts['Cells/ml'] = counts['Cells/ml'].astype('float')
counts.index = counts.spec_id

def extract_at_locs(samples, arr, win=0.12):
	store = {}
	for ix, sample in samples.iterrows():
		if pd.notnull(sample.geometry.x):
			#chla = ratios.sel(x=sample.geometry.x, y=sample.geometry.y, method='nearest') \
			val = arr.sel(x=slice(sample.geometry.x-win,sample.geometry.x+win)) \
						 .sel(y=slice(sample.geometry.y-win,sample.geometry.y+win)) \
						 .sel(time=sample.time) \
						 .mean()
			store[sample.spec_id] = val.values
	valpd = pd.Series(store, name=arr.name)
	return valpd

# 'Normalised difference chlorophyll index'
ndci = (uav_refl.Band5 - uav_refl.Band3) / (uav_refl.Band5 + uav_refl.Band3)
ndci.attrs['pyproj_srs'] = uav_refl.Band1.attrs['pyproj_srs']
ndci_vals = extract_at_locs(samples, ndci)
ndci_vals.name = 'ndci'

ndci_counts = counts.join(ndci_vals)
ndci_counts = ndci_counts[ndci_counts['ndci'].notnull()]

X = ndci_counts['ndci'].astype(float)
y = np.log(ndci_counts['Biovolume'])
X = sm.add_constant(X)
model = sm.OLS(y, X) # or QuantReg
results = model.fit() # if QuantReg, can pass p=percentile here
print(results.summary())

biovolume_log = results.params.ndci * ndci + results.params.const
biovolume = np.exp(biovolume_log)
biovolume.attrs['pyproj_srs'] = uav_refl.Band1.attrs['pyproj_srs']


from matplotlib.colors import LogNorm
figure(),biovolume.sel(time='2017-07-21').where(biovolume > 0).plot.imshow(norm=LogNorm(vmin=0.01, vmax=1e6))

# For some reason need to export to numpy to be able to plot log-normalised
biovolume_0721 = np.where(np.isnan(biovolume_0721),0,biovolume_0721)
figure(),imshow(np.flipud(biovolume_0721), norm=LogNorm(vmin=1e4,vmax=1e5))
colorbar()

"""
Next steps = export biovolumes as new dataset
And then undertake comparison with detrended DEMs
"""