"""
Load all UAV-acquired data into xarray instances.

"""

import datetime as dt
import xarray as xr
import georaster
import pandas as pd
import pyproj
import numpy as np

# UAV classified images and albedos
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

# UAV HCRF reflectances
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


# UAV DEMs
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


## Load mask to delimit 'good' area of 2017-07-24 flight.
msk = georaster.SingleBandRaster('/scratch/UAV/uav2017_common_grid_nc/good_area_2017-07-24_3_common.tif')


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
