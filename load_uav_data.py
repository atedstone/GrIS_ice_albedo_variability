"""
Load all UAV-acquired data into xarray instances.

"""

import datetime as dt
import xarray as xr
import georaster
import pandas as pd
import pyproj
import numpy as np
import salem

def add_srs(xrds, srs, x='x'):
	for v in xrds.variables:
		if x in xrds[v].dims:
			xrds[v].attrs['pyproj_srs'] = srs
	return xrds

uav_times = [dt.datetime(2017,7,15),
	dt.datetime(2017,7,20),
	dt.datetime(2017,7,21),
	dt.datetime(2017,7,22),
	dt.datetime(2017,7,23),
	dt.datetime(2017,7,24)
	]

# UAV classified images 
pth = '/scratch/UAV/L3/uav_2017*class*clf20190130_171930.nc'
#'/scratch/UAV/uav2017_commongrid_bandcorrect/*classified*epsg32622.nc'
uav_class = xr.open_mfdataset(pth,
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
uav_class['time'] = uav_times 
uav_class = add_srs(uav_class, 'epsg:32622')

# Albedos
uav_alb = xr.open_mfdataset('/scratch/UAV/uav2017_commongrid_bandcorrect/*albedo*epsg32622.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
uav_alb['time'] = uav_times 
uav_alb = add_srs(uav_alb, 'epsg:32622')

# UAV HCRF reflectances
uav_refl = xr.open_mfdataset('/scratch/UAV/uav2017_commongrid_bandcorrect/*refl*commongrid.tif_epsg32622.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
uav_refl['time'] = uav_times 
# Correct using ground-UAV comparisons from compare_hcrf_uav.py
uav_refl['Band1'] -= 0.17
uav_refl['Band2'] -= 0.18
uav_refl['Band3'] -= 0.15
uav_refl['Band4'] -= 0.16
uav_refl['Band5'] -= 0.1
uav_refl = add_srs(uav_refl, 'epsg:32623')

# UAV DEMs
dem_times = [dt.datetime(2017,7,15),
	dt.datetime(2017,7,20),
	dt.datetime(2017,7,21),
	dt.datetime(2017,7,22),
	dt.datetime(2017,7,23)
	]
dems = xr.open_mfdataset('/scratch/UAV/uav2017_dem/*commongrid_epsg32622.nc',
	concat_dim='time')#, chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
dems['time'] = dem_times 
dems = add_srs(dems, 'epsg:32622')

dem_upe = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_common.nc')
dem_upe = add_srs(dem_upe, 'epsg:32622')


## Load mask to delimit 'good' area of 2017-07-24 flight.
msk = georaster.SingleBandRaster('/scratch/UAV/good_area_2017-07-24_3_common.tif')
# I think it is possible to load geotiffs via xarray/rasterio now?

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


## Convert destructive site coordinates to UTM



shpf = salem.read_shapefile('/scratch/UAV/uav2017_dem/dem2017_commonarea_999.shp')
uav_poly = salem.read_shapefile('/scratch/UAV/uav_2017_area.shp')
uav_poly_upe = salem.read_shapefile('/scratch/UAV/uav_2018_area.shp')