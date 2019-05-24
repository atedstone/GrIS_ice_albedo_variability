""" 
MODIS comparison

Pull out albedo values for the two albedo pixels which the UAV flight area straddles.

!! Using original sinusoidal grid !!
- previously I was using a regridded (pstere) product which, although nearest neighbour,
wasn't really appropriate for this pixel-scale comparison.

"""

import xarray as xr 
import pandas as pd

modis_sinu = {
'2017-07-15': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017196.h16v02.006.2017198034212.hdf":MOD_Grid_Snow_500m:Snow_Albedo_Daily_Tile',
'2017-07-17': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017198.h16v02.006.2017200034922.hdf":MOD_Grid_Snow_500m:Snow_Albedo_Daily_Tile',
'2017-07-18': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017199.h16v02.006.2017201033701.hdf":MOD_Grid_Snow_500m:Snow_Albedo_Daily_Tile',
'2017-07-20': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017201.h16v02.006.2017203033818.hdf":MOD_Grid_Snow_500m:Snow_Albedo_Daily_Tile',
'2017-07-21': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017202.h16v02.006.2017204040517.hdf":MOD_Grid_Snow_500m:Snow_Albedo_Daily_Tile',
'2017-07-22': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017203.h16v02.006.2017205035504.hdf":MOD_Grid_Snow_500m:Snow_Albedo_Daily_Tile',
'2017-07-24': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017205.h16v02.006.2017207031143.hdf":MOD_Grid_Snow_500m:Snow_Albedo_Daily_Tile',
'2017-07-25': 'HDF4_EOS:EOS_GRID:"/scratch/L0data/MOD10A1.006.raw/MOD10A1.A2017206.h16v02.006.2017208033539.hdf":MOD_Grid_Snow_500m:Snow_Albedo_Daily_Tile',
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

modis_pd = pd.DataFrame.from_dict(store, orient='index')
modis_pd = modis_pd / 100
modis_pd.index = pd.DatetimeIndex(modis_pd.index)

modis_pd.to_csv('/home/at15963/projects/uav/outputs/MOD10A1_sinusoidal_pixel_albedos.csv')
