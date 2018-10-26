import sys
import xarray as xr
import pandas as pd
import statsmodels.api as sm

## Approx biomass loading
# From JC email 2018-05-24:
# However as per Chris, remember that BBA vs cell counts not really appropriate - should be BBA vs biovolume.
logcellsml = (-4.592 * uav.albedo.sel(time='2017-07-21') + 5.392) 
# JC relationship doesn't seem of right magnitude - x100 seems to fix it but needs checking
cellsml = xr.apply_ufunc(np.exp, logcellsml.load()) * 100
cellsdwml = cellsml * 1 #chris reckons cell dry weight is roughly 1 ng (maybe a bit less) as a ballpark estimate - 2018-06-05
cellsdwg = cellsdwml * 0.4
cells_dw_mg_g = cellsdwg * 1e-6
figure(), cells_dw_mg_g.plot.imshow(vmin=0,vmax=0.01, cmap='Reds')

## Blob detection
# import cv2
# detector = cv2.SimpleBlobDetector()
# keypoints = detector.detect(uav.classified.sel(time='2017-07-24').where(uav.classified == 5).values)

# uav.plot.hist(bins=vals)

# from skimage.feature import blob_dog, blob_log, blob_doh
# toblob = uav.classified.where(uav.classified == 5).sel(time='2017-07-24').isel(x=slice(3000,4000),y=slice(3000,4000)).values
# toblob = np.where(np.isnan(toblob),0,1)      
# #blobs_log = blob_log(toblob, max_sigma=30, num_sigma=10, threshold=.1)
# blobs_doh = blob_doh(toblob, max_sigma=30, threshold=.01)
# # Compute radii in the 3rd column.
# blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)



#### Cell counts versus broadband albedo and versus each individual band
import sys
sys.path.append("/home/at15963/scripts/IceSurfClassifiers") 
import xarray_classify

## RedEdge values for spectra. --- use to load in RedEdge measurements of destructive sites.
## This is ASD data !!
rededge = pd.read_excel('/home/at15963/Dropbox/work/black_and_bloom/multispectral-sensors-comparison.xlsx',
	sheet_name='RedEdge')
wvl_centers = rededge.central
wvls = pd.DataFrame({'low':rededge.start, 'high':rededge.end})
HCRF_file = '/scratch/field_spectra/HCRF_master.csv'
spectra = xarray_classify.load_hcrf_data(HCRF_file, wvls)

#counts = pd.read_excel('/home/at15963/Dropbox/work/data/field_processed_2017/Updated_GrIS_Cell count results_250518.xlsx', sheet_name='Cells per ml')
counts = pd.read_excel('/home/at15963/Dropbox/work/data/field_processed_2017/GrIS_2017_Cell counts_with_vols.xlsx', sheet_name='Cells per ml')
#counts = counts.dropna()
counts['Cells/ml'] = counts['Cells/ml'].astype('float')

bbas_counts = bbas_mean.merge(counts, on='spec_id')

spectra_counts = spectra.merge(counts, left_index=True, right_on='spec_id')

spectra_counts = spectra_counts.dropna()
spectra_counts = spectra_counts[spectra_counts['Cells/ml'] > 0]
for band in spectra.columns:
	figure()
	plot(np.log(spectra_counts['Cells/ml']), spectra_counts[band], 'o')
	title(band)
	ols = sm.OLS(spectra_counts[band], sm.add_constant(np.log(spectra_counts['Cells/ml'])))
	print(ols.fit().summary())
# Shows that the best bands are apparently R475, R560


estim_dw_mgg = counts['Cells/ml'] * 1 / 1e6


## ---------------------------------------------------------------------------
## Use RedEdge ratio

# Create ratios
ratio = uav_refl.Band5.sel(time='2017-07-21') / uav_refl.Band3.sel(time='2017-07-21')
ratios = uav_refl.Band5 / uav_refl.Band3
ratios.attrs['pyproj_srs'] = uav_refl.Band5.attrs['pyproj_srs']


## Stats combined with DEM data
ratio_msk = ratios.salem.roi(shape=shpf)
ratio_msk_pd = ratio_msk.to_pandas()

detr_msk = detrended_mean.detrended_mean.sel(time='2017-07-21').salem.roi(shape=shpf)
detr_msk_pd = detr_msk.to_pandas()

combo = pd.concat({'ratio':ratio_msk_pd.stack(), 'elev':detr_msk_pd.stack()},axis=1)
combo = combo.dropna()


periods = pd.interval_range(start=-0.4, end=0.8, periods=12)
elev_bins = pd.cut(combo.elev, bins=periods)

combo['elev_bin'] = elev_bins

# Simple approach is just to get mean ratio in each category
combo.groupby(elev_bins)['ratio'].agg(['mean'])
# Also check how many observations are in each category
combo.groupby(elev_bins)['ratio'].agg(['count']) 

# Box plot
combo['elev_bin'] = elev_bins
# There are a lot of ratio outliers, to hide them set fliersize to zero
figure(), sns.boxplot(x='elev_bin', y='ratio', data=combo, fliersize=0,
	color='#E74C3C')
# And then need to adjust y axis as it is still scaled to include fliers
plt.ylim(0.6,1.6)
ticks, labels = plt.xticks()
new_labels = [-0.35,-0.25,-0.15,-0.05,0.05,0.15,0.25,0.35,0.45,0.55,0.65,0.75]
plt.xticks(ticks,new_labels)


# ----------------------------------------------------------------------------
## Look at ratio values of destructive samples, versus UAV refl

# Load destructive locations
samples = geopandas_helpers.load_xyz_gpd('/home/at15963/Dropbox/work/data/field_processed_2017/uav_sb_locations_certain_only_incl20th.csv',
	x='sample_x', y='sample_y', crs={'init':'epsg:32623'})
# Create timestamp
samples['time'] = [dt.datetime.strptime(str(d), '%Y%m%d') for d in samples.date]
samples = samples[pd.notnull(samples.id)]
samples.index = samples.id

# Get rid of bad points
#samples = samples.drop(labels=['20170721_SB2']) # 'listed as GCP-SB matching uncertain'

store = {}
win = 0.1 #25 cm
for ix, sample in samples.iterrows():
	if pd.notnull(sample.geometry.x):
		#chla = ratios.sel(x=sample.geometry.x, y=sample.geometry.y, method='nearest') \
		chla = ndvi.sel(x=slice(sample.geometry.x-win,sample.geometry.x+win)) \
					 .sel(y=slice(sample.geometry.y-win,sample.geometry.y+win)) \
					 .sel(time=sample.time) \
					 .mean()
		store[sample.id] = chla.values
#storepd = pd.Series(store, name='uav_albedo')
ndvipd = pd.Series(store, name='ndvi')

# Append chla ratio value as column to samples dataframe
samples = samples.join(storepd)

samples_counts = pd.merge(left=samples, right=counts, left_on='spec_id', right_on='spec_id')
samples_counts['Cells/ml'] = pd.to_numeric(samples_counts['Cells/ml'])

figure(),plot(np.log(samples_counts['Cells/ml']), samples_counts['ratio'], 'o')
figure(),plot(samples_counts['Cells/ml'], samples_counts['ratio'], 'o')

samples_counts_cull = samples_counts[samples_counts['Cells/ml'] < 40000]
samples_counts_cull = samples_counts_cull[pd.notnull(samples_counts_cull['ratio'])]


X = pd.to_numeric(samples_counts_cull['Cells/ml'])
y = samples_counts_cull['ratio'].astype(float)
X = sm.add_constant(X)
model = sm.OLS(y, X) # or QuantReg
#model = sm.WLS(y, X, weights=joined['U%s_std' %band]) # or QuantReg
results = model.fit() # if QuantReg, can pass p=percentile here
print(results.summary())


# ----------------------------------------------------------------------------
## Look at cell counts versus ratio calculated from ground spectra...

# Spectra are already previously in this script

spectra_counts = pd.merge(left=spectra, right=counts, left_index=True, right_on='spec_id')
spectra_counts['Cells/ml'] = pd.to_numeric(spectra_counts['Cells/ml']) 
spectra_counts['asd_ratio'] = spectra_counts['R717'] / spectra_counts['R668'] 

y = spectra_counts['Cells/ml']
X = spectra_counts['asd_ratio'].astype(float)
X = sm.add_constant(X)
model = sm.OLS(y, X) # or QuantReg
results = model.fit() # if QuantReg, can pass p=percentile here
print(results.summary())
# On 22 Oct 2018, this result was good = R2=0.78
# This thus yields relationship between reflectance and biomass loading in cells/ml
uav_cells = results.params['asd_ratio'] * ratios + results.params['const']
uav_cells.attrs['pyproj_srs'] = uav_refl.Band5.attrs['pyproj_srs']

spectra_counts_uav = pd.merge(left=spectra_counts, 
	right=samples_counts_cull.filter(items=['spec_id','ratio']),
	left_on='spec_id', right_on='spec_id')
spectra_counts_uav['ratio'] = spectra_counts_uav['ratio'].astype(float)
#figure(),spectra_counts_uav.plot(kind='scatter',x='asd_ratio',y='ratio')

X = spectra_counts_uav['asd_ratio']
y = spectra_counts_uav['ratio']
X = sm.add_constant(X)
model = sm.OLS(y, X) # or QuantReg
results = model.fit() # if QuantReg, can pass p=percentile here
print(results.summary())
# On 22 Oct 2018, this is horrendous, R=0.09


# Compare with biomass
spectra_counts_reix = spectra_counts
spectra_counts_reix.index = spectra_counts_reix.spec_id
spectra_counts_cull = spectra_counts_reix.drop(labels=['15_7_SB5', '23_7_SB1', '21_7_SB3', '21_7_SB9'])
y = spectra_counts_cull['Log biovolume']
X = spectra_counts_cull['asd_ratio'].astype(float)
X = sm.add_constant(X)
model = sm.OLS(y, X) # or QuantReg
results = model.fit() # if QuantReg, can pass p=percentile here
print(results.summary())
# This thus yields relationship between reflectance and biomass loading 
uav_biovol = results.params['asd_ratio'] * ratios + results.params['const']
# No statistically significant relationship available.



## Changes in cells/ml between scenes
uav_cells_msk = uav_cells.salem.roi(shape=shpf)
meancells = uav_cells_msk.mean(dim=['y','x'])

# histogram (kinda similar to what I looked at with just refl, given linear calibration, but worth a go)

figure()
n = 1
for t in uav_cells_msk.time:
	plt.subplot(len(uav_cells_msk.time), 1, n)
	plt.yscale('log')
	uav_cells_msk.sel(time=t).plot.hist(bins=[0,1e5,2e5,3e5,4e5,5e5,6e5])
	plt.title(t.values)
	plt.ylim(1,10e8)
	n += 1

sampl_spectra_counts_bands = pd.merge(left=samples_counts, right=spectra_counts, left_on='spec_id', right_on='spec_id')
sampl_spectra_counts_bands.index = sampl_spectra_counts_bands.id
sampl_spectra_counts_bands = sampl_spectra_counts_bands.join(storepd3)
sampl_spectra_counts_bands = sampl_spectra_counts_bands.join(storepd5)







#X = np.log(samples_ratios_counts['Cells/ml'])
X = np.log(samples_ratios_counts['Cells/ml'])
y = samples_ratios_counts['ndvi'].astype(float)
X = sm.add_constant(X)
model = sm.OLS(y, X) # or QuantReg
#model = sm.WLS(y, X, weights=joined['U%s_std' %band]) # or QuantReg
results = model.fit() # if QuantReg, can pass p=percentile here
print(results.summary())






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
	#storepd = pd.Series(store, name='uav_albedo')
	valpd = pd.Series(store, name=arr.name)
	return valpd

b1 = extract_at_locs(samples, uav_refl.Band1)
b2 = extract_at_locs(samples, uav_refl.Band2)
b3 = extract_at_locs(samples, uav_refl.Band3)
b4 = extract_at_locs(samples, uav_refl.Band4)
b5 = extract_at_locs(samples, uav_refl.Band5)
ratios.name = 'uav_b5divb3'
rat = extract_at_locs(samples, ratios)

# 'Normalised difference chlorophyll index'
ndci = (uav_refl.Band5 - uav_refl.Band3) / (uav_refl.Band5 + uav_refl.Band3)
ndci.attrs['pyproj_srs'] = uav_refl.Band1.attrs['pyproj_srs']
ndci_vals = extract_at_locs(samples, ndci)
ndci_vals.name = 'ndci'

# NDVI (NIR-RED / NIR+RED)
ndvi = (uav_refl.Band4 - uav_refl.Band3) / (uav_refl.Band5 + uav_refl.Band3)
ndvi.attrs['pyproj_srs'] = uav_refl.Band1.attrs['pyproj_srs']
ndvi_vals = extract_at_locs(samples, ndvi)
ndvi_vals.name = 'ndvi'

# NDRE (NIR-RE / NIR+RE)
ndre = (uav_refl.Band4 - uav_refl.Band5) / (uav_refl.Band4 + uav_refl.Band5)
ndre.attrs['pyproj_srs'] = uav_refl.Band1.attrs['pyproj_srs']
ndre_vals = extract_at_locs(samples, ndre)
ndre_vals.name = 'ndre'

uav_bands = pd.concat([b1,b2,b3,b4,b5], axis=1)


uav_bands_counts = pd.merge(left=counts, right=uav_bands, left_on='spec_id', right_index=True)

for b in ['Band1', 'Band2', 'Band3', 'Band4', 'Band5']:
	X = np.log(uav_bands_counts['Biovolume'])
	y = uav_bands_counts['uav_b5divb3'].astype(float)
	X = sm.add_constant(X)
	model = sm.OLS(y, X) # or QuantReg
	results = model.fit() # if QuantReg, can pass p=percentile here
	print(results.summary())