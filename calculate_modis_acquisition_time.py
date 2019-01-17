
#fn = '/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017201.h16v02.006.2017203033818.hdf'
fn = '/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017202.h16v02.006.2017204040517.hdf'

modis_gdal = gdal.Open(fn)
meta = modis_gdal.GetMetadata()

ninputs = int(meta['NUMBEROFINPUTGRANULES'])

timings = pd.DataFrame({
	'pointer': [int(x) for x in meta['GRANULEPOINTERARRAY'].split(', ')][0:ninputs],
	'begin': [x for x in meta['GRANULEBEGINNINGDATETIMEARRAY'].split(', ')],
	'end':[x for x in meta['GRANULEENDINGDATETIMEARRAY'].split(', ')],
	'orbit':[x for x in meta['ORBITNUMBERARRAY'].split(', ')][0:ninputs]
})

modis_gdal = None



## Block below copied from examine_modis_sinusoidal.py --->

modis_sinu = {
'2017-07-20': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017201.h16v02.006.2017203033818.hdf":MOD_Grid_Snow_500m:granule_pnt',
'2017-07-21': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017202.h16v02.006.2017204040517.hdf":MOD_Grid_Snow_500m:granule_pnt',
}

store = {}
for ix in modis_sinu:
	modis = xr.open_rasterio(modis_sinu[ix]) 

	# These values are plucked 'manually' using coordinate capture in QGIS on 
	# 
	left_px = float(modis.sel(x=-2137458, y=7458751, method='nearest').values)
	right_px = float(modis.sel(x=-2137085, y=7458698, method='nearest').values)

	store[ix] = dict(left=left_px, right=right_px)

	modis = None

granules = pd.DataFrame.from_dict(store, orient='index')


"""

Now use the values in the granules DataFrame (1 value per pixel for each day)
to look up the timings DataFrame against the pointer column, this will tell you
the granule that was used to acquire the observation. Granules are 5-mins long.

overpass times in UTC at S6:
07-20: 14:20 --> 12:20 LT
07-21: 15:05 --> 13:05 LT

"""