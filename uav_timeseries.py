"""
Analyse UAV time series - albedo and reflectance

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
import numpy as np

import georaster

from load_uav_data import *

# 2017 UAV pixel location in polar-stereo, corresponding to MODIS pixel to read in
uav_modis_x = -190651
uav_modis_y = -2507935

## !! RUN IMPORT SCRIPTS HERE !!
from load_ground_data import *
from load_uav_data import *


## Create a categorical colourmap.
vals = [0, 1, 2, 3, 4, 5, 6]
cmap = mpl.colors.ListedColormap(['#000000','#08519C','#FFFFFF', '#C6DBEF', '#FDBB84', '#B30000', '#762A83'])
# Example of use: uav.classified.sel(time='2017-07-23').plot(cmap=cmap, vmin=0, vmax=7)



## Calculate total pixels available and classified
total_px = uav_class.Band1.where(uav_class.Band1.notnull()).count(dim=('y','x'))
#total_px_msk = uav_class.Band1.where(msk.r > 0).where(uav_class.Band1.notnull()).count(dim=('y','x'))


## Ad sentinel-2 data!
# Check msk orientation!


## Summary statistics of surface class change through time
uav_class = uav_class.fillna(-1)
store = {}
store_msk = {}
for t in uav_class.time:
	values, bins, patches = uav_class.Band1.sel(time=t).plot.hist(bins=8, range=(-1,7))
	nulls = uav_class.Band1.sel(time=t).isnull().count()
	#values_msk, bins, patches = uav_class.Band1.sel(time=t).where(msk.r > 0).plot.hist(bins=8, range=(-1,7))
	plt.close()
	store[t.values] = values
	#store_msk[t.values] = values_msk

keys = ['NaN', 'Unknown', 'Water', 'Snow', 'Clean Ice', 'Lbio', 'Hbio', 'Cryoconite']

# Whole-area statistics
valspd = pd.DataFrame.from_dict(store, orient='index')
valspd.columns = keys
valspd = valspd.sort_index()
valspd['Unknown'] = valspd['Unknown'] + valspd['NaN']
valspd = valspd.drop(labels='NaN',axis=1)

# Statistics just for masked area
# valspdm = pd.DataFrame.from_dict(store_msk, orient='index')
# valspdm.columns = keys
# valspdm = valspdm.sort_index()
# valspdm['Unknown'] = valspdm['Unknown'] + valspdm['NaN']
# valspdm = valspdm.drop(labels='NaN',axis=1)

## Extract MOD10A1 Albedo for this location
mod10 = xr.open_dataset('/scratch/MOD10A1.006.SW/MOD10A1.2017.006.reproj500m.nc')
modalb = mod10.Snow_Albedo_Daily_Tile.where(mod10.Snow_Albedo_Daily_Tile < 100) \
	.sel(X=uav_modis_x, Y=uav_modis_y, method='nearest') * 0.01

## Also, b01 refl
mod09 = xr.open_dataset('/scratch/MOD09GA.006.FB/MOD09GA.2017.006.epsg3413_b1234q.nc')
mod09b01 = mod09.sur_refl_b01_1.sel(X=uav_modis_x, Y=uav_modis_y, method='nearest')

## Calculate daily mean albedo from uav	
uavalb = uav_alb.Band1.where(uav_alb.Band1 > 0).salem.roi(shape=uav_poly).mean(dim=('x','y'))
# uavalbm = uav_alb.albedo.where(msk.r > 0).where(uav_alb.albedo > 0).mean(dim=('x','y'))
# uavalbmstd = uav_alb.albedo.where(msk.r > 0).where(uav_alb.albedo > 0).std(dim=('x','y'))

uav_alb_sto = {}
for ix,row in temporal_gcps.iterrows():
	# pixels are 0.05 m
	x_slice = slice(row.x-(0.05*4),row.x+(0.05*4))
	y_slice = slice(row.y-(0.05*4),row.y+(0.05*4))
	alb = uav_alb.Band1.sel(x=x_slice, y=y_slice).load().median(dim=('x','y'))
	uav_alb_sto[ix] = alb.to_pandas()
uavalb_px = pd.DataFrame.from_dict(uav_alb_sto)
uavalb_px.loc['2017-07-24'].loc[3:5] = np.nan

# Add daily destructive sampling locations to this logic too.


## Plot time series of albedo comparison.
plt.figure()
modalb.plot(marker='o', linestyle='none', label='MODIS 500 m', alpha=0.7)
#uavalbm.plot(marker='o', linestyle='none', label='UAV masked area', alpha=0.7)
uavalb_px.mean(axis=1).plot(marker='o', linestyle='none', label='UAV Temporal Sites', alpha=0.7)
daily_bba_asd.plot(marker='o', linestyle='none', label='ASD Temporal Sites', alpha=0.7)
plt.legend()
plt.xlim('2017-07-12', '2017-07-27')


combo = pd.DataFrame({'MOD10A1':modalb.to_pandas(), 'UAV':uavalb.to_pandas(), 'ASD':daily_bba_asd})
combo.to_csv('/home/at15963/projects/uav/outputs/sensor_albedos.csv')

## Plot time series of reflectance comparison
uavred = uav_refl.Band3.where(uav_refl.Band3 > 0).mean(dim=('x','y'))


plt.figure(figsize=(4,9))
n = 1
ytick_locs = np.array([0, 5e5, 1e6, 1.5e6, 2e6, 2.5e6])
ytick_labels = (ytick_locs * (0.05**2)).astype(int) #sq m
for scene in uav_class.time:
	plt.subplot(6, 1, n)
	uavha = uav_alb.Band1.sel(time=scene).salem.roi(shape=uav_poly)
	uavhc = uav_class.Band1.sel(time=scene).salem.roi(shape=uav_poly)
	if pd.Timestamp(scene.values) == pd.datetime(2017, 7, 24):
		uavh_al = uavha #.where(msk.r > 0)
		uavh_cl = uavhc #.where(msk.r > 0)
	else:
		uavh_al = uavha
		uavh_cl = uavhc

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