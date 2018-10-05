"""
Analyse UAV time series

Mask: save shapefile in EPSG:32623, then:
gdal_rasterize -a_srs EPSG:32623 -a id -tr 0.05 0.05 -at good_area_2017-07-24.shp good_area_2017-07-24_3.tif
gdalwarp -te 310895 7446509 311219 7446839 good_area_2017-07-24_3.tif good_area_2017-07-24_3_common.tif

For discrete colourmap information this is a good source:
https://gist.github.com/jakevdp/91077b0cae40f8f8244a

"""
import xarray as xr
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import pyproj
import numpy as np

import georaster

# 2017 UAV pixel location in polar-stereo, corresponding to MODIS pixel to read in
uav_modis_x = -190651
uav_modis_y = -2507935


## BBA values
log_sheet = pd.read_csv('/scratch/field_spectra/temporal_log_sheet.csv')
bba = pd.read_csv('/scratch/field_spectra/BBA.txt')
# Mangle BBA.txt to get date/time information out 
info = bba['RowName'].str.split('_', 3, expand=True)
info.columns = ['Day','Month','Site','fill']
info['Month'] = info['Month'].astype(float)
info['Day'] = info['Day'].astype(float)
info['Site'] = info['Site'].astype(str)
info = info.drop('fill', axis=1)
bbas = pd.concat([bba,info], axis=1)
# BBA.txt contains albedo value for every single replicate, so generate
# means from each set of replicate measurements
bbas_mean = bbas.groupby(['Day','Month','Site']).mean()
bbas_mean = bbas_mean.reset_index()
bbas_mean['spec_id'] = ['%i_%i_%s' %(r['Day'],r['Month'],r['Site']) for ix, r in bbas_mean.iterrows()]
bbas_log = bbas_mean.merge(log_sheet,on=['Day','Month','Site'])


# Calculate daily mean BBA from Fieldspec samples
# Index corresponding to temporal samples
daily_bba_asd = bbas_log.BBA_list.groupby(bbas_log.Day).mean()
ix = [pd.datetime(2017,7,13),pd.datetime(2017,7,14),pd.datetime(2017,7,15),pd.datetime(2017,7,21),pd.datetime(2017,7,22),pd.datetime(2017,7,23),pd.datetime(2017,7,24),pd.datetime(2017,7,25)]
daily_bba_asd.index = ix

# Not sure what this does...
# grouped = spectra.groupby('label').mean().drop(labels='numeric_label',axis=1).T
# grouped.index = [475,560,668,717,840]


# Read all UAV images into one multi-temporal frame.
uav_times = [dt.datetime(2017,7,15),
	dt.datetime(2017,7,20),
	dt.datetime(2017,7,21),
	dt.datetime(2017,7,22),
	dt.datetime(2017,7,23),
	dt.datetime(2017,7,24)
	]
uav = xr.open_mfdataset('/scratch/UAV/uav2017_commongrid_bandcorrect/*class.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
uav['time'] = uav_times 

uav_refl = xr.open_mfdataset('/scratch/UAV/uav2017_commongrid_bandcorrect/*commongrid.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
uav_refl['time'] = uav_times 
# Correct using ground-UAV comparisons from compare_hcrf_uav.py
uav_refl['Band1'] -= 0.17
uav_refl['Band2'] -= 0.18
uav_refl['Band3'] -= 0.15
uav_refl['Band4'] -= 0.16
uav_refl['Band5'] -= 0.1

## Create a categorical colourmap.
vals = [0, 1, 2, 3, 4, 5, 6]
cmap = mpl.colors.ListedColormap(['#000000','#08519C','#FFFFFF', '#C6DBEF', '#FDBB84', '#B30000', '#762A83'])
# Example of use: uav.classified.sel(time='2017-07-23').plot(cmap=cmap, vmin=0, vmax=7)


## Load mask to delimit 'good' area of 2017-07-24 flight.
msk = georaster.SingleBandRaster('/scratch/UAV/uav2017_common_grid_nc/good_area_2017-07-24_3_common.tif')

## Calculate total pixels available and classified
total_px = uav.classified.where(uav.classified.notnull()).count(dim=('y','x'))
total_px_msk = uav.classified.where(msk.r > 0).where(uav.classified.notnull()).count(dim=('y','x'))


## Ad sentinel-2 data!
# Check msk orientation!

## Summary statistics of surface class change through time
uav = uav.fillna(-1)
store = {}
store_msk = {}
for t in uav.time:
	values, bins, patches = uav.classified.sel(time=t).plot.hist(bins=8, range=(-1,7))
	nulls = uav.classified.sel(time=t).isnull().count()
	values_msk, bins, patches = uav.classified.sel(time=t).where(msk.r > 0).plot.hist(bins=8, range=(-1,7))
	plt.close()
	store[t.values] = values
	store_msk[t.values] = values_msk

keys = ['NaN', 'Unknown', 'Water', 'Snow', 'Clean Ice', 'Lbio', 'Hbio', 'Cryoconite']

# Whole-area statistics
valspd = pd.DataFrame.from_dict(store, orient='index')
valspd.columns = keys
valspd = valspd.sort_index()
valspd['Unknown'] = valspd['Unknown'] + valspd['NaN']
valspd = valspd.drop(labels='NaN',axis=1)

# Statistics just for masked area
valspdm = pd.DataFrame.from_dict(store_msk, orient='index')
valspdm.columns = keys
valspdm = valspdm.sort_index()
valspdm['Unknown'] = valspdm['Unknown'] + valspdm['NaN']
valspdm = valspdm.drop(labels='NaN',axis=1)


## Extract MOD10A1 Albedo for this location
mod10 = xr.open_dataset('/scratch/MOD10A1.006.SW/MOD10A1.2017.006.reproj500m.nc')
modalb = mod10.Snow_Albedo_Daily_Tile.where(mod10.Snow_Albedo_Daily_Tile < 100) \
	.sel(X=uav_modis_x, Y=uav_modis_y, method='nearest') * 0.01

## Also, b01 refl
mod09 = xr.open_dataset('/scratch/MOD09GA.006.FB/MOD09GA.2017.006.epsg3413_b1234q.nc')
mod09b01 = mod09.sur_refl_b01_1.sel(X=uav_modis_x, Y=uav_modis_y, method='nearest')


## Calculate daily mean albedo from uav	
uavalb = uav.albedo.where(uav.albedo > 0).mean(dim=('x','y'))
uavalbm = uav.albedo.where(msk.r > 0).where(uav.albedo > 0).mean(dim=('x','y'))
uavalbmstd = uav.albedo.where(msk.r > 0).where(uav.albedo > 0).std(dim=('x','y'))


##  Extract UAV albedos at each temporal ground sampling location
# First convert site coordinates to UTM (only for the temporal sites, numbered 1:5)
all_gcps = pd.read_csv('/home/at15963/Dropbox/work/data/field_processed_2017/pixel_gcps_kely_formatted.csv', index_col=0)
temporal_gcps = {}
utm = pyproj.Proj('+init=epsg:32623')
for	n in np.arange(1,6):
	gcp = all_gcps.loc['GCP%s' %n]
	utmx, utmy = utm(gcp.lon, gcp.lat)
	# Approximately identify the reflectance measurement center - move towards camp
	utmx += 0.4
	utmy -= 0.4
	temporal_gcps[n] = {'x':utmx, 'y':utmy}
temporal_gcps = pd.DataFrame(temporal_gcps).T

uav_alb_sto = {}
for ix,row in temporal_gcps.iterrows():
	# pixels are 0.05 m
	x_slice = slice(row.x-(0.05*4),row.x+(0.05*4))
	y_slice = slice(row.y-(0.05*4),row.y+(0.05*4))
	alb = uav.albedo.sel(x=x_slice, y=y_slice).load().median(dim=('x','y'))
	uav_alb_sto[ix] = alb.to_pandas()
uavalb_px = pd.DataFrame.from_dict(uav_alb_sto)
uavalb_px.loc['2017-07-24'].loc[3:5] = np.nan

# Add daily destructive sampling locations to this logic too.


## Plot time series of albedo comparison.
plt.figure()
modalb.plot(marker='o', linestyle='none', label='MODIS 500 m', alpha=0.7)
uavalbm.plot(marker='o', linestyle='none', label='UAV masked area', alpha=0.7)
uavalb_px.mean(axis=1).plot(marker='o', linestyle='none', label='UAV Temporal Sites', alpha=0.7)
daily_bba_asd.plot(marker='o', linestyle='none', label='ASD Temporal Sites', alpha=0.7)
plt.legend()
plt.xlim('2017-07-12', '2017-07-27')


## Plot time series of reflectance comparison
uavred = uav_refl.Band3.where(uav_refl.Band3 > 0).mean(dim=('x','y'))


plt.figure(figsize=(4,9))
n = 1
ytick_locs = np.array([0, 5e5, 1e6, 1.5e6, 2e6, 2.5e6])
ytick_labels = (ytick_locs * (0.05**2)).astype(int) #sq m
for scene in uav.time:
	plt.subplot(6, 1, n)
	uavh = uav.sel(time=scene)
	if pd.Timestamp(scene.values) == pd.datetime(2017, 7, 24):
		uavh_al = uavh.albedo.where(msk.r > 0)
		uavh_cl = uavh.classified.where(msk.r > 0)
	else:
		uavh_al = uavh.albedo
		uavh_cl = uavh.classified

	uavh_al.where(uavh_cl == 5) \
		.plot.hist(bins=50, range=(0,1), alpha=0.7, label='High Biomass', color='#B30000')
	uavh_al.where(uavh_cl == 4) \
		.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Low Biomass', color='#FDBB84')
	uavh_al.where(uavh_cl == 3) \
		.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Clean Ice', color='#4292C6')
	uavh_al.where(uavh_cl == 2) \
		.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Snow', color='black')
	plt.title(pd.Timestamp(scene.values).strftime('%Y-%m-%d'))
	plt.yticks(ytick_locs, ytick_labels)
	plt.ylabel('Area (sq. m)')
	plt.xlim(0.1,0.8)
	plt.xlabel('Albedo')
	n += 1
plt.tight_layout()

"""
Other logic to add:

Histograms of whole area and common area through time
	- histogram of albedo just for bare ice, low biomass, etc.
	- Might bring performance ramifications for radiometric calibration and for classification strategy.

"""



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



#### Cell counts work
import sys
sys.path.append("/home/at15963/scripts/IceSurfClassifiers") 
import xarray_classify

## RedEdge values for spectra. --- use to load in RedEdge measurements of destructive sites.
rededge = pd.read_excel('/home/at15963/Dropbox/work/black_and_bloom/multispectral-sensors-comparison.xlsx',
	sheet_name='RedEdge')
wvl_centers = rededge.central
wvls = pd.DataFrame({'low':rededge.start, 'high':rededge.end})
HCRF_file = '/scratch/field_spectra/HCRF_master.csv'
spectra = xarray_classify.load_hcrf_data(HCRF_file, wvls)

counts = pd.read_excel('/home/at15963/Dropbox/work/data/field_processed_2017/Updated_GrIS_Cell count results_250518.xlsx', sheet_name='Cells per ml')
counts = counts.dropna()
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



## Slope, DEM, etc
# for f in *commongrid.tif; do gdaldem slope -of NetCDF $f ${f: 0:-4}_slope.nc; done
# for f in *commongrid.tif; do gdaldem aspect -of NetCDF $f ${f: 0:-4}_aspect.nc; done

# Read all UAV images into one multi-temporal frame.
dem_times = [dt.datetime(2017,7,15),
	dt.datetime(2017,7,20),
	dt.datetime(2017,7,21),
	dt.datetime(2017,7,22),
	dt.datetime(2017,7,23)
	]
dems = xr.open_mfdataset('/scratch/UAV/uav2017_dem/*commongrid.nc',
	concat_dim='time')#, chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
dems['time'] = dem_times 

slopes = xr.open_mfdataset('/scratch/UAV/uav2017_dem/*slope.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
slopes['time'] = dem_times 

aspects = xr.open_mfdataset('/scratch/UAV/uav2017_dem/*aspect.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
aspects['time'] = dem_times 


## Plane fit
# http://inversionlabs.com/2016/03/21/best-fit-surfaces-for-3-dimensional-data.html
rough_x = np.linspace(dems.x[0], dems.x[-1], dems.dims['x'] / 100)
rough_y = np.linspace(dems.y[0], dems.y[-1], dems.dims['y'] / 100)
zi = dems.Band1.sel(time='2017-07-21').interp(x=rough_x, y=rough_y)
zi_zeros = zi.where(zi > 500)
zi_msk_flat = zi_zeros.values.flatten()
# figure(), zi.plot(vmin=1040, vmax=1070)
xg = np.array([zi.x.values,] * len(zi.y)).flatten()
yg = np.array([zi.y.values,] * len(zi.x)).transpose().flatten()
xg[np.isnan(zi_msk_flat)] = np.nan
yg[np.isnan(zi_msk_flat)] = np.nan
xg = xg[~np.isnan(xg)]
yg = yg[~np.isnan(yg)]
zi_msk_flat = zi_msk_flat[~np.isnan(zi_msk_flat)]

A = np.c_[xg,yg,np.ones(xg.shape[0])]
C,_,_,_ = scipy.linalg.lstsq(A, zi_msk_flat)
surfx = np.array([dems.x.values,] * len(dems.y))
surfy = np.array([dems.y.values,] * len(dems.x)).transpose()
Z = C[0] * surfx + C[1] * surfy + C[2]

detrended = dems.Band1.sel(time='2017-07-21') - Z


## Basic blurring approach, by using xarray to downsample then substract downsampled from original
xi = np.array([zi.x.values,] * len(zi.y))
yi = np.array([zi.y.values,] * len(zi.x)).transpose()
zi = zi.where(zi > 1000)
zif = zi.interp(x=dems.x,y=dems.y)  


## Gaussian low-pass approach
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
import cv2
blur = cv2.GaussianBlur(dems.Band1.sel(time='2017-07-21').values, (99,99), 0)
filtered = dems.Band1.sel(time='2017-07-21')-blur
figure(),filtered.plot(vmin=-0.1,vmax=0.1),title('cv2.Gaussian 99')
# Check no local slopes accidentally caught/removed by verifying no local slopes present in blurred DEM
grads = np.gradient(blur)
figure(),imshow(np.sqrt(grads[0]**2+grads[1]**2),vmax=10) 

# For all DEMs at once
gauss_blur = lambda x,y : cv2.GaussianBlur(x, (y,y), 0)
def gauss_blur(x,y):
	print(x.shape)
	return cv2.GaussianBlur(np.squeeze(x), (y,y), 0)
blurs = xr.apply_ufunc(gauss_blur, dems.Band1, 99, dask='parallelized', output_dtypes=[float], input_core_dims=[[],[]])
filtered = dems.Band1 - blurs

# Using dask (kept here for reference only)
# Should not be parallelised as then edges between chunks appear!
# gauss_blur = lambda x,y : cv2.GaussianBlur(x, (y,y), 0)
# blurred = xr.apply_ufunc(gauss_blur, dems.Band1.sel(time='2017-07-21'), 99, dask='parallelized', output_dtypes=[float])
# filtered = dems.Band1.sel(time='2017-07-21') - blurred
# figure(),filtered.plot(vmin=-0.1, vmax=0.1)

ratio = uav_refl.Band5.sel(time='2017-07-21') / uav_refl.Band3.sel(time='2017-07-21')


""" end of Fri 5 October 
ratio = uav_refl.Band5.sel(time='2017-07-21') / uav_refl.Band3.sel(time='2017-07-21')
figure(),ratio.plot(vmin=1,vmax=1.4)
ratio_pd = ratio.to_series()
blur = cv2.GaussianBlur(dems.Band1.sel(time='2017-07-21').values, (99,99), 0)
filtered = dems.Band1.sel(time='2017-07-21')-blur
filtered_pd = filtered.to_series()
combo = pd.concat({'ratio':ratio_pd,'elev':filtered_pd})
combo = pd.concat({'ratio':ratio_pd,'elev':filtered_pd},axis=1)
combo
figure(),combo.plot('o',alpha=0.3)
figure(),combo.scatter(x='ratio',y='elev',marker='o',alpha=0.3)
figure(),combo.plot(kind='scatter',x='ratio',y='elev',marker='o',alpha=0.3)
ylim(-1,1)
xlim(1,1.5)
%hsitory
%history
figure(),uav_refl.Band1.sel(time='2017-07-21').plot()
uav_refl.Band1.sel(time='2017-07-21')
uav_refl.Band1.sel(time='2017-07-21').values
msk = uav_refl.Band1.sel(time='2017-07-21').where(uav_refl.Band1.sel(time='2017-07-21') > 0)
combo = pd.concat({'ratio':ratio_pd,'elev':filtered_pd,'msk':msk.to_series()},axis=1)
combo.msk
combo_msk = combo.dropna()
figure(),combo_msk.plot(kind='scatter',x='ratio',y='elev',marker='o',alpha=0.3)
close('all')
len(combo_msk)
combo_msk = combo_msk[combo_msk.elev < -10]
combo_msk = combo_msk[combo_msk.elev > 10]
len(combo_msk)
combo_msk = combo.dropna()
combo_msk.elev
combo_msk[combo_msk.elev < -10]
len(combo_msk < -10]
len(combo_msk < -10)
shape(combo_msk < -10)
shape(combo_msk.elev < -10)
sum(combo_msk.elev < -10)
figure(),combo_msk.elev.plot.hist()
figure(),combo_msk.elev.plot.hist(range=(-50,50),bins=100)
figure(),combo_msk.elev.plot.hist(range=(-10,10),bins=100)
sum(combo_msk.elev > -10)
combo_msk = combo_msk[combo_msk.elev > -2]
combo_msk = combo_msk[combo_msk.elev < 2]
combo_msk
figure(),combo_msk.plot(kind='scatter',x='ratio',y='elev',marker='o',alpha=0.3)
xlim(1,1.5)
%history
"""








## Binning by aspect
# However, all this might tell us is that we haven't fully corrected for BRDF issues!!
asp21 = aspects.transpose('time','y','x').Band1.sel(time='2017-07-21').to_pandas()
alb21 = uav.albedo.sel(time='2017-07-21').to_pandas()
combo = pd.DataFrame({'asp':asp21.values.flatten(),'alb':alb21.values.flatten()})
combo.groupby(pd.cut(combo.asp,36))['alb'].agg(['count','mean'])
                      count      mean
asp                                  
(-0.36, 9.998]       331401  0.355746
(9.998, 19.997]      240294  0.355395
(19.997, 29.995]     192156  0.358363
(29.995, 39.993]     158546  0.362745
(39.993, 49.991]     132943  0.365501
(49.991, 59.99]      113766  0.372682
(59.99, 69.988]      100579  0.379343
(69.988, 79.986]      93084  0.381006
(79.986, 89.984]      85705  0.378249
(89.984, 99.983]      95874  0.378355
(99.983, 109.981]     85300  0.387210
(109.981, 119.979]   104776  0.367253
(119.979, 129.977]   109899  0.403651
(129.977, 139.976]   114203  0.394563
(139.976, 149.974]   127599  0.404502
(149.974, 159.972]   145787  0.423142
(159.972, 169.97]    173267  0.411075
(169.97, 179.969]    196561  0.421740
(179.969, 189.967]   293436  0.421146
(189.967, 199.965]   372371  0.421740
(199.965, 209.964]   524687  0.415167
(209.964, 219.962]   745829  0.416766
(219.962, 229.96]    923855  0.424208
(229.96, 239.958]   1147222  0.427509
(239.958, 249.957]  1437949  0.424014
(249.957, 259.955]  1703151  0.421941
(259.955, 269.953]  1815846  0.420382
(269.953, 279.951]  2067652  0.414429
(279.951, 289.95]   1882613  0.408613
(289.95, 299.948]   1701997  0.401603
(299.948, 309.946]  1427737  0.393765
(309.946, 319.944]  1131351  0.386911
(319.944, 329.943]   867970  0.379101
(329.943, 339.941]   665133  0.370571
(339.941, 349.939]   513513  0.361856
(349.939, 359.938]   373299  0.358165
