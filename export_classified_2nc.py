"""
Temporary script that has guts of IceSurfClassifiers/predict_msrefedge.py, 
in order to export tifs to netcdf - as netcdf saving from predict_msredeege,py 
was accidentally disabled and it was going to take longer to re-run the classifer
script than to bodge this new one.
"""
import pandas as pd
import xarray as xr
import joblib
from osgeo import gdal, osr
import numpy as np
import georaster

fn_path = '/scratch/UAV/uav2017_commongrid_bandcorrect/'
flights = {
'20170715':'uav_20170715_refl_5cm_commongrid.nc',
'20170720':'uav_20170720_refl_5cm_commongrid.nc',
'20170721':'uav_20170721_refl_5cm_commongrid.nc',
'20170722':'uav_20170722_refl_5cm_commongrid.nc',
'20170723':'uav_20170723_refl_5cm_commongrid.nc',
'20170724':'uav_20170724_refl_5cm_commongrid.nc'
}

setup = False



for flight in flights:

	print(flight)

	if not setup:
		# Define projection
		srs = osr.SpatialReference()
		srs.ImportFromProj4('+init=epsg:32623')
		crs = xr.DataArray(0, encoding={'dtype':np.dtype('int8')})
		crs.attrs['projected_crs_name'] = srs.GetAttrValue('projcs')
		crs.attrs['grid_mapping_name'] = 'universal_transverse_mercator'
		crs.attrs['scale_factor_at_central_origin'] = srs.GetProjParm('scale_factor')
		crs.attrs['standard_parallel'] = srs.GetProjParm('latitude_of_origin')
		crs.attrs['straight_vertical_longitude_from_pole'] = srs.GetProjParm('central_meridian')
		crs.attrs['false_easting'] = srs.GetProjParm('false_easting')
		crs.attrs['false_northing'] = srs.GetProjParm('false_northing')
		crs.attrs['latitude_of_projection_origin'] = srs.GetProjParm('latitude_of_origin')

		## Create associated lat/lon coordinates DataArrays
		uav_gr = georaster.SingleBandRaster('NETCDF:"%s%s":Band1' %(fn_path, flights[flight]),
			load_data=False)
		grid_lon, grid_lat = uav_gr.coordinates(latlon=True)
		uav = xr.open_dataset(fn_path + flights[flight],chunks={'x':1000,'y':1000}) 
		coords_geo = {'y': uav['y'], 'x': uav['x']}
		uav = None

		lon_da = xr.DataArray(grid_lon, coords=coords_geo, dims=['y', 'x'], 
			encoding={'_FillValue': -9999., 'dtype':'int16', 'scale_factor':0.000000001})
		lon_da.attrs['grid_mapping'] = 'universal_transverse_mercator'
		lon_da.attrs['units'] = 'degrees'
		lon_da.attrs['standard_name'] = 'longitude'

		lat_da = xr.DataArray(grid_lat, coords=coords_geo, dims=['y', 'x'], 
			encoding={'_FillValue': -9999., 'dtype':'int16', 'scale_factor':0.000000001})
		lat_da.attrs['grid_mapping'] = 'universal_transverse_mercator'
		lat_da.attrs['units'] = 'degrees'
		lat_da.attrs['standard_name'] = 'latitude'

		setup = True
	
	classified = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/%s' %(flights[flight][:-3] + '_classified.tif'))
	albedo_gr = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/%s' %(flights[flight][:-3] + '_albedo.tif'))

	predicted = xr.DataArray(np.flipud(classified.r), dims=('y','x'), coords=coords_geo)
	predicted.encoding = {'dtype':'int16', 'zlib':True, '_FillValue':-9999}
	predicted.name = 'Surface Class'
	predicted.attrs['long_name'] = 'Surface classification using Random Forests 6-class classifier'
	predicted.attrs['units'] = 'None'
	predicted.attrs['key'] = 'Unknown:0; Water:1; Snow:2; Clean Ice:3; Light Algae on Ice:4; Heavy Algae on Ice:5; Cryoconite:6' ## FIX !!
	predicted.attrs['grid_mapping'] = 'universal_transverse_mercator'

	albedo = xr.DataArray(np.flipud(albedo_gr.r), dims=('y','x'), coords=coords_geo)
	albedo.encoding = {'dtype':'int16', 'scale_factor':0.01, 'zlib':True, '_FillValue':-9999}
	albedo.name = 'Surface albedo computed after Knap et al. (1999) narrowband-to-broadband conversion'
	albedo.attrs['units'] = 'dimensionless'
	albedo.attrs['grid_mapping'] = 'universal_transverse_mercator'


	ds = xr.Dataset({'classified':predicted,
		'albedo':albedo,
		'universal_transverse_mercator':crs,
		'lon':lon_da,
		'lat':lat_da})

	ds = ds.transpose('y','x')

	# Main metadata
	ds.attrs['Conventions'] = 'CF-1.4'
	#ds.attrs['history'] = ''
	ds.attrs['institution'] = 'University of Bristol (Andrew Tedstone)'
	ds.attrs['title'] = 'Greenland ice sheet UAV (MicaSense RedEdge) imagery converted to classification and albedo maps'

	# Additional geo-referencing
	ds.attrs['nx'] = len(ds.x)
	ds.attrs['ny'] = len(ds.y)
	ds.attrs['xmin'] = float(ds.x.min())
	ds.attrs['ymax'] = float(ds.y.max())
	ds.attrs['spacing'] = 0.05

	# NC conventions metadata for dimensions variables
	ds.x.attrs['units'] = 'meters'
	ds.x.attrs['standard_name'] = 'projection_x_coordinate'
	ds.x.attrs['point_spacing'] = 'even'
	ds.x.attrs['axis'] = 'x'

	ds.y.attrs['units'] = 'meters'
	ds.y.attrs['standard_name'] = 'projection_y_coordinate'
	ds.y.attrs['point_spacing'] = 'even'
	ds.y.attrs['axis'] = 'y'

	save_fn = flights[flight][:-3] + '_class.nc'
	ds.to_netcdf('%s%s' %(fn_path, save_fn), format='NetCDF4')

	ds = None
	albedo = None
	classified = None