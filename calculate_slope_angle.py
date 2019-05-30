import xarray as xr
import richdem as rd

from load_uav_data import *


blur99_s6 = xr.open_dataset('/scratch/UAV/uav2017_dem/blur_fits_99_epsg32622.nc')
blur99_s6 = add_srs(blur99_s6, 'epsg:32622')


# S6 slope
demnp = np.flipud(blur99_s6.blurred.sel(time='2017-07-21').salem.roi(shape=uav_poly).values)
demnp = np.where(demnp == 0, -9999, demnp)
demnp = np.where(np.isnan(demnp), -9999, demnp)
demrd = rd.rdarray(demnp, no_data=-9999)
demrd.geotransform = (310895.0, 0.05, 0.0, 7446839.0, 0.0, -0.05)
demrd.projection = 'PROJCS["WGS 84 / UTM zone 23N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32623"]]'

slope = rd.TerrainAttribute(demrd, attrib='slope_degrees')
print('Mean Slope S6: %s' %np.nanmean(np.where(slope > 0, slope, np.nan)))

aspect = rd.TerrainAttribute(demrd, attrib='aspect')
print('Mean Aspect S6: %s' %np.nanmean(np.where(aspect > 0, aspect, np.nan)))

blur99_upe = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399.nc')
blur99_upe = add_srs(blur99_upe, 'epsg:32622')

demnp = np.flipud(blur99_upe.blurred.squeeze().salem.roi(shape=uav_poly_upe).values)
demnp = np.where(demnp == 0, -9999, demnp)
demnp = np.where(np.isnan(demnp), -9999, demnp)
demrd = rd.rdarray(demnp, no_data=-9999)
demrd.geotransform = (415832.692, 0.05, 0.0, 8088772.973, 0.0, -0.05) 
demrd.projection = 'PROJCS["WGS 84 / UTM zone 22N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-51],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32622"]]'

slope = rd.TerrainAttribute(demrd, attrib='slope_degrees')
print('Mean Slope UPE: %s' %np.nanmean(np.where(slope > 0, slope, np.nan)))

# rd_dem_upe = rd.LoadGDAL('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_common.tif')
# slope = rd.TerrainAttribute(rd_dem_upe, attrib='slope_degrees')

# rd_dem_s6 = rd.LoadGDAL('/scratch/UAV/uav2017_dem/')
# slope = rd.TerrainAttribute(rd_dem_upe, attrib='slope_degrees')