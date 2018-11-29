# analyse_slopes

from load_uav_data import *

import xarray as xr
import cv2
import numpy as np

# Datasets _999: a window of c. 50 m; datasets without suffix: window of 99 (c. 5 m)
# 20 m: 400 px

## Gaussian low-pass approach
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
# This uses an astonishing amount of RAM ...
tmp_store = np.zeros((dems.dims['time'],dems.dims['y'],dems.dims['x']))
tn = 0
for t in dems.time:
	blurred = cv2.GaussianBlur(dems.Band1.sel(time=t).values, (5,5), 0)
	tmp_store[tn,:,:] = blurred
	tn += 1

coords = {'time':dems.time, 'y':dems.y, 'x':dems.x}
blurred_xr = xr.DataArray(tmp_store, coords=coords, dims=('time','y','x') )
blurred_xr.name = 'blurred'
blurred_xr.to_netcdf('/scratch/UAV/uav2017_dem/dems_highpass5x5.nc')
tmp_store = None
blurred_xr = None

# Load back in with dask
dems_hipass = xr.open_dataset('/scratch/UAV/uav2017_dem/dems_highpass5x5.nc', 
	chunks={'y':2000, 'x':2000})
dems_hipass.blurred.attrs['pyproj_srs'] = uav.classified.attrs['pyproj_srs']




### Calculate and save slopes

import richdem as rd

tmp_store = np.zeros((dems.dims['time'],dems.dims['y'],dems.dims['x']))
tn = 0
for t in dems_hipass.time:
	data = rd.rdarray(dems_hipass.blurred.sel(time=t).values, no_data=-9999) 
	slope = rd.TerrainAttribute(data, attrib='slope_degrees')
	tmp_store[tn,:,:] = slope
	tn += 1

coords = {'time':dems.time, 'y':dems.y, 'x':dems.x}
slopes_xr = xr.DataArray(tmp_store, coords=coords, dims=('time','y','x') )
slopes_xr.name = 'slope'
slopes_xr.to_netcdf('/scratch/UAV/uav2017_dem/dems_highpass5x5_slopes.nc')
tmp_store = None
slopes_xr = None

slopes = xr.open_dataset('/scratch/UAV/uav2017_dem/dems_highpass5x5_slopes.nc')
slopes.slope.attrs['pyproj_srs'] = uav.classified.attrs['pyproj_srs']





data = rd.rdarray(dems.Band1.sel(time=t).values, no_data=-9999) 
slope = rd.TerrainAttribute(data, attrib='slope_degrees')