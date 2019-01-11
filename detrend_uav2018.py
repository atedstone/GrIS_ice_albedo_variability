import xarray as xr
import cv2


""" dem lineage: 
 needed to be clipped to same extent as refl:
 gdalwarp -te 415832.692 8088443.273 416181.942 8088772.973 uav_20180724_PM_dem.tif uav_20180724_PM_dem_common.tif
 then converted to netcdf as xr.open_rasterio seems to have a bug:
 gdal_translate  -of NetCDF uav_20180724_PM_dem_common.tif uav_20180724_PM_dem_common.nc
"""


# Datasets _999: a window of c. 50 m; datasets without suffix: window of 99 (c. 5 m)
# 20 m: 400 px
dem = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_common.nc')
## Gaussian low-pass approach
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
# This uses an astonishing amount of RAM ...
blurred = cv2.GaussianBlur(dem.Band1.squeeze().values, (399,399), 0)


coords = {'y':dem.y, 'x':dem.x}
blurred_xr = xr.DataArray(blurred, coords=coords, dims=('y','x') )
blurred_xr.name = 'blurred'
blurred_xr.to_netcdf('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399.nc')
blurred_xr = None

# Load back in with dask
blurred = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399.nc',
	chunks={'y':2000, 'x':2000})

detrended = dem.Band1.squeeze() - blurred.blurred
detrended.name = 'detrended'
detrended.to_netcdf('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.nc')
detrended = None
detrended = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.nc')

#figure(),blurred.blurred.mean(dim='time').plot(vmin=1040,vmax=1070,cmap='RdBu')
figure(),detrended.detrended.plot(vmin=-0.1,vmax=0.1,cmap='RdBu_r')
