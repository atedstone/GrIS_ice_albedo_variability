"""
Analyse UAV time series

Mask: save shapefile in EPSG:32623, then:
gdal_rasterize -a_srs EPSG:32623 -a id -tr 0.05 0.05 -at good_area_2017-07-24.shp good_area_2017-07-24_3.tif
gdalwarp -te 310895 7446509 311219 7446839 good_area_2017-07-24_3.tif good_area_2017-07-24_3_common.tif

"""
import xarray as xr
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl

import georaster

# 2017 UAV pixel location in polar-stereo, corresponding to MODIS pixel to read in
uav_modis_x = -190651
uav_modis_y = -2507935


## BBA values
# Run ~/projects/weathering_crust/analyse_field_spectra.py first!
# Index corresponding to temporal samples
daily_bba_asd = bbas_log.BBA_list.groupby(bbas_log.Day).mean()
ix = [pd.datetime(2017,7,13),pd.datetime(2017,7,14),pd.datetime(2017,7,15),pd.datetime(2017,7,21),pd.datetime(2017,7,22),pd.datetime(2017,7,23),pd.datetime(2017,7,24),pd.datetime(2017,7,25)]
daily_bba_asd.index = ix



def discrete_cmap(N, base_cmap=None):
    """Create an N-bin discrete colormap from the specified input map"""

    # https://gist.github.com/jakevdp/91077b0cae40f8f8244a

    # Note that if base_cmap is a string or None, you can simply do
    #    return plt.cm.get_cmap(base_cmap, N)
    # The following works for string, None, or a colormap instance:

    base = plt.cm.get_cmap(base_cmap)
    color_list = base(np.linspace(0, 1, N))
    cmap_name = base.name + str(N)
    return base.from_list(cmap_name, color_list, N)


# grouped = spectra.groupby('label').mean().drop(labels='numeric_label',axis=1).T
# grouped.index = [475,560,668,717,840]

uav = xr.open_mfdataset('/scratch/UAV/uav2017_common_grid_nc/*class.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})

uav['time'] = [dt.datetime(2017,7,15),
	dt.datetime(2017,7,17),
	dt.datetime(2017,7,20),
	dt.datetime(2017,7,21),
	dt.datetime(2017,7,22),
	dt.datetime(2017,7,23),
	dt.datetime(2017,7,24)
	]

# Drop snowy mosaic
uav = uav.drop(labels=(pd.datetime(2017, 7, 17)), dim='time')

vals = [0, 1, 2, 3, 4, 5, 6]
cmap = mpl.colors.ListedColormap(['#000000','#08519C','#FFFFFF', '#C6DBEF', '#FDBB84', '#B30000', '#762A83'])
norm = mpl.colors.BoundaryNorm(vals, cmap.N)

uav.classified.sel(time='2017-07-23').plot(cmap=cmap, vmin=0, vmax=7)
# cb = mpl.colorbar.ColorbarBase(ax, cmap=cmap,
#                                 norm=norm,
#                                 spacing='uniform',
#                                 orientation='horizontal',
#                                 extend='neither',
#                                 ticks=vals)


total_px = uav.classified.where(uav.classified.notnull()).count(dim=('y','x'))


# Mask to delimit 'good' area of 2017-07-24 flight.
msk = georaster.SingleBandRaster('/scratch/UAV/uav2017_common_grid_nc/good_area_2017-07-24_3_common.tif')

# Compare distribution within mask area for each image, to see if statistically representative
# Essentially, the mask area is flight number 1 - it's flight number 2 that failed.


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
valspd = pd.DataFrame.from_dict(store, orient='index')
valspd.columns = keys
valspdm = pd.DataFrame.from_dict(store_msk, orient='index')
valspdm.columns = keys
valspdm = valspdm.sort_index()
valspdm['Unknown'] = valspdm['Unknown'] + valspdm['NaN']
valspdm = valspdm.drop(labels='NaN',axis=1)


## Albedo
mod10 = xr.open_dataset('/scratch/MOD10A1.006.SW/MOD10A1.2017.006.reproj500m.nc')
modalb = mod10.Snow_Albedo_Daily_Tile.where(mod10.Snow_Albedo_Daily_Tile < 100) \
	.sel(X=-190804,Y=-2508152,method='nearest') * 0.01
uavalb = uav.albedo.where(uav.albedo > 0).mean(dim=('x','y'))


uav_alb_sto = {}
for ix,row in temporal_gcps.iterrows():
	# pixels are 0.05 m
	x_slice = slice(row.x-(0.05*4),row.x+(0.05*4))
	y_slice = slice(row.y-(0.05*4),row.y+(0.05*4))
	alb = albedo.sel(x=x_slice, y=y_slice).load().median(dim=('x','y'))
	uav_alb_sto[ix] = alb.to_pandas()
uavalb_px_new = pd.DataFrame.from_dict(uav_alb_sto)

plt.figure()
modalb.plot(marker='o', linestyle='none', label='MODIS 500 m', alpha=0.7)
uavalb.plot(marker='o', linestyle='none', label='UAV whole area', alpha=0.7)
uavalb_px.mean(axis=1).plot(marker='o', linestyle='none', label='UAV Temporal Sites', alpha=0.7)
daily_bba_asd.plot(marker='o', linestyle='none', label='ASD Temporal Sites', alpha=0.7)
plt.legend()
plt.xlim('2017-07-12', '2017-07-27')


flights = {
'20170715':'uav_20170715_refl_5cm_albedo.tif',
'20170717':'uav_20170717_refl_5cm_albedo.tif',
'20170720':'uav_20170720_refl_5cm_albedo.tif',
'20170721':'uav_20170721_refl_5cm_albedo.tif',
'20170722':'uav_20170722_refl_5cm_albedo.tif',
'20170723':'uav_20170723_refl_nolenscorr_5cm_albedo.tif',
'20170724':'uav_20170724_refl_5cm_v2_albedo.tif'
}
# Now pull out values from each flight
alb_store = {}
uav_window = 9
for flight in flights:

	im = georaster.SingleBandRaster('/scratch/UAV/uav2017_common_grid_nc/%s' %flights[flight],
		load_data=False)

	for ix, gcp in temporal_gcps.iterrows():
		val, win = im.value_at_coords(gcp.x, gcp.y, window=uav_window, 
			return_window=True, reducer_function=np.nanmedian)

		# Standard deviation in each band
		std = np.std(win)

		spec_id = flight[-2:] + '_7_S' + str(ix)
		alb_store[spec_id] = {'med':val, 'std':std}

	im = None


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