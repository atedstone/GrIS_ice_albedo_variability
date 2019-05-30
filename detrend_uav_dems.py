import xarray as xr
import cv2
import numpy as np

from load_uav_data import * 
# Datasets _999: a window of c. 50 m; datasets without suffix: window of 99 (c. 5 m)
# 20 m: 400 px

## Gaussian low-pass approach
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
# This uses an astonishing amount of RAM ...
tmp_store = np.zeros((dems.dims['time'],dems.dims['y'],dems.dims['x']))
tn = 0
for t in dems.time:
	blurred = cv2.GaussianBlur(dems.Band1.sel(time=t).values, (399,399), 0)
	tmp_store[tn,:,:] = blurred
	tn += 1

coords = {'time':dems.time, 'y':dems.y, 'x':dems.x}
blurred_xr = xr.DataArray(tmp_store, coords=coords, dims=('time','y','x') )
blurred_xr.name = 'blurred'
blurred_xr.to_netcdf('/scratch/UAV/uav2017_dem/blur_fits_399_epsg32622.nc')
tmp_store = None
blurred_xr = None

# Load back in with dask
blurred = xr.open_dataset('/scratch/UAV/uav2017_dem/blur_fits_399_epsg32622.nc', 
	chunks={'y':2000, 'x':2000})

detrended = dems.Band1 - blurred.blurred
detrended.name = 'detrended'
detrended.to_netcdf('/scratch/UAV/uav2017_dem/dems2017_detrended_commongrid_399_epsg32622.nc')
detrended = None
detrended = xr.open_dataset('/scratch/UAV/uav2017_dem/dems2017_detrended_commongrid_399_epsg32622.nc')

detrended_mean = dems.Band1 - blurred.blurred.mean(dim='time')
detrended_mean.name = 'detrended_mean'
detrended_mean.to_netcdf('/scratch/UAV/uav2017_dem/dems2017_detrendedmean_commongrid_399_epsg32622.nc')
detrended_mean = None
detrended_mean = xr.open_dataset('/scratch/UAV/uav2017_dem/dems2017_detrendedmean_commongrid_399_epsg32622.nc')

#figure(),blurred.blurred.mean(dim='time').plot(vmin=1040,vmax=1070,cmap='RdBu')
#figure(),detrended_mean.detrended_mean.sel(time='2017-07-21').plot(vmin=-0.1,vmax=0.1,cmap='RdBu_r')

