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
	blurred = cv2.GaussianBlur(dems.Band1.sel(time=t).values, (99,99), 0)
	tmp_store[tn,:,:] = blurred
	tn += 1

coords = {'time':dems.time, 'y':dems.y, 'x':dems.x}
blurred_xr = xr.DataArray(tmp_store, coords=coords, dims=('time','y','x') )
blurred_xr.name = 'blurred'
blurred_xr.to_netcdf('/scratch/UAV/uav2017_dem/blur_fits_99.nc')
tmp_store = None
blurred_xr = None

# Load back in with dask
blurred = xr.open_dataset('/scratch/UAV/uav2017_dem/blur_fits_99.nc', 
	chunks={'y':2000, 'x':2000})

detrended = dems.Band1 - blurred.blurred
detrended.name = 'detrended'
detrended.to_netcdf('/scratch/UAV/uav2017_dem/dems2017_detrended_commongrid_99.nc')
detrended = None
detrended = xr.open_dataset('/scratch/UAV/uav2017_dem/dems2017_detrended_commongrid_99.nc')

detrended_mean = dems.Band1 - blurred.blurred.mean(dim='time')
detrended_mean.name = 'detrended_mean'
detrended_mean.to_netcdf('/scratch/UAV/uav2017_dem/dems2017_detrendedmean_commongrid_99.nc')
detrended_mean = None
detrended_mean = xr.open_dataset('/scratch/UAV/uav2017_dem/dems2017_detrendedmean_commongrid_99.nc')

#figure(),blurred.blurred.mean(dim='time').plot(vmin=1040,vmax=1070,cmap='RdBu')
figure(),detrended_mean.detrended_mean.sel(time='2017-07-21').plot(vmin=-0.1,vmax=0.1,cmap='RdBu_r')

# Check no local slopes accidentally caught/removed by verifying no local slopes present in blurred DEM
#grads = np.gradient(blur)
#figure(),imshow(np.sqrt(grads[0]**2+grads[1]**2),vmax=10) 


# Using dask (kept here for reference only)
# Should not be parallelised as then edges between chunks appear!
# gauss_blur = lambda x,y : cv2.GaussianBlur(x, (y,y), 0)
# blurred = xr.apply_ufunc(gauss_blur, dems.Band1.sel(time='2017-07-21'), 99, dask='parallelized', output_dtypes=[float])
# filtered = dems.Band1.sel(time='2017-07-21') - blurred
# figure(),filtered.plot(vmin=-0.1, vmax=0.1)



#### OLD ANALYSIS APPROACHES BELOW ####


## Plane fit
# http://inversionlabs.com/2016/03/21/best-fit-surfaces-for-3-dimensional-data.html
"""
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
"""


## Slope, DEM, etc
# However, this approach isn't necessarily of much use when not yet detrended.
# for f in *commongrid.tif; do gdaldem slope -of NetCDF $f ${f: 0:-4}_slope.nc; done
# for f in *commongrid.tif; do gdaldem aspect -of NetCDF $f ${f: 0:-4}_aspect.nc; done

## Basic blurring approach, by using xarray to downsample then substract downsampled from original
"""
xi = np.array([zi.x.values,] * len(zi.y))
yi = np.array([zi.y.values,] * len(zi.x)).transpose()
zi = zi.where(zi > 1000)
zif = zi.interp(x=dems.x,y=dems.y)  
"""


## Binning by aspect
# However, all this might tell us is that we haven't fully corrected for BRDF issues!!
"""
asp21 = aspects.transpose('time','y','x').Band1.sel(time='2017-07-21').to_pandas()
alb21 = uav.albedo.sel(time='2017-07-21').to_pandas()
combo = pd.DataFrame({'asp':asp21.values.flatten(),'alb':alb21.values.flatten()})
combo.groupby(pd.cut(combo.asp,36))['alb'].agg(['count','mean'])
"""