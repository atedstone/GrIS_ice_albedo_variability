"""
Script to apply correct radiance-reflectance factors to bands 4 (NIR) and 5 (red-edge)

Prior to 2018-05-28 there was a bug in the micasense_calibration repository 
which led to the rad2refl factor for NIR being applied to red-edge, and vice-
versa.

This script works of the basis of assuming that the rad2refl parameters are
time-invariant. It undoes the incorrect ones and then applies the correction.

Use for the 2017 S6 imagery.

"""

import pandas as pd
import subprocess
import time
import georaster

"""
PROOF OF CONCEPT - USING XARRAY 

uav20 = xr.open_dataset('/scratch/UAV/uav2017_common_grid_nc/uav_20170721_refl_5cm.nc',
	chunks={'x':2000, 'y':2000})

rededge_factor = 10.3
nir_factor = 8.4

#Band 5 = RedEdge, Band 4 = NIR
uav20['Band4'] = (uav20['Band4'] / rededge_factor) * nir_factor
uav20['Band5'] = (uav20['Band5'] / nir_factor) * rededge_factor

# Correct using ground-UAV comparisons from compare_hcrf_uav.py
uav20['Band1'] -= 0.17
uav20['Band2'] -= 0.18
uav20['Band3'] -= 0.15
uav20['Band4'] -= (0.2 / rededge_factor) * nir_factor
uav20['Band5'] -= (0.05 / nir_factor) * rededge_factor

albedo = 0.726*uav20['Band2'] - 0.322*uav20['Band2']**2 - 0.015*uav20['Band4'] + 0.581*uav20['Band4']
b_ix = pd.Index([1,2,3,4,5],name='b') 
concat = xr.concat([uav20.Band1, uav20.Band2, uav20.Band3, uav20.Band4, uav20.Band5], b_ix)
predicted = xarray_classify.classify_dataset(concat.sel(X=slice(310900,310981), Y=slice(7446782,7446724)), clf_RF)
"""

## Apply to geotiffs
# Flights to iterate through
flights = {
'20170715':'uav_20170715_refl_5cm._commongrid.tif',
#'20170717':'uav_20170717_refl_5cm._commongrid.tif',
'20170720':'uav_20170720_refl_5cm._commongrid.tif',
'20170721':'uav_20170721_refl_5cm._commongrid.tif',
'20170722':'uav_20170722_refl_5cm._commongrid.tif',
'20170723':'uav_20170723_refl_nolenscorr_5cm._commongrid.tif',
'20170724':'uav_20170724_refl_5cm_v2._commongrid.tif'
}

for flight in flights:

	print(flight)

	im = georaster.MultiBandRaster('/scratch/UAV/uav2017_common_grid_tif/%s' %flights[flight])

	params = pd.read_csv('/scratch/rededge_calibration/%s/rad2refl_params.csv' %flight,
		index_col='band_name')

	# Band 4 (NIR)
	# This had RedEdge scaling factor applied erroneously
	im.r[:,:,3] = (im.r[:,:,3] / params.loc['Red edge','p1']) * params.loc['NIR','p1']

	# Band 5 (RedEdge)
	# This had NIR scaling factor applied erroneously
	im.r[:,:,4] = (im.r[:,:,4] / params.loc['NIR','p1']) * params.loc['Red edge','p1']

	# Save as new GeoTIFF
	fn = '/scratch/UAV/uav2017_commongrid_bandcorrect/uav_%s_refl_5cm_commongrid.tif' %flight
	im.save_geotiff(fn)
	time.sleep(10)
	im = None

	# Generate pyramids
	subprocess.call('gdaladdo -clean %s' %fn, shell=True)
	subprocess.call('gdaladdo -r average -ro --config USE_RRD NO --config TILED YES --config GDAL_CACHEMAX 10240 %s 2 4 8 16' %fn,
		shell=True)
    
	# Export as new netcdf
	subprocess.call('gdalwarp %s %s' %(fn, fn[:-3]+'nc'),
		shell=True)


