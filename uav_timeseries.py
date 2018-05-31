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

# Add daily destructive sampling locations to this logic too.


## Plot time series of albedo comparison.
plt.figure()
modalb.plot(marker='o', linestyle='none', label='MODIS 500 m', alpha=0.7)
uavalb.plot(marker='o', linestyle='none', label='UAV whole area', alpha=0.7)
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



