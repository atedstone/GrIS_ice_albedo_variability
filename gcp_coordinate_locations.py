import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

import georaster


def gpd_from_csv(filename, crs, xfield='lon', yfield='lat', **kwargs):
	""" Return a GeoPandas DataFrame representation of a CSV file. """
	df = pd.read_csv(filename, **kwargs)
	geometry = [Point(xy) for xy in zip(df[xfield], df[yfield])]
	gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
	return gdf	


gcps = gpd_from_csv('/home/at15963/Dropbox/work/data/field_processed_2017/pixel_gcps_kely_formatted.csv',
	{'init':'epsg:4326'},
	index_col=0)

joe_im = georaster.MultiBandRaster('/scratch/UAV/uav_20170723_refl_nolenscorr_5cm.tif', load_data=False)
common_im = georaster.MultiBandRaster('/scratch/UAV/uav_20170723_refl_nolenscorr_5cm._commongrid.tif', load_data=False)

for key, gcp in gcps.iterrows():
	jpx, jpy = joe_im.coord_to_px(gcp.lon, gcp.lat, latlon=True)
	cpx, cpy = common_im.coord_to_px(gcp.lon, gcp.lat, latlon=True)
	print('%s: 20170723: %s,%s; Common: %s, %s' %(key,jpx,jpy,cpx,cpy))


joe_im = None
common_im = None