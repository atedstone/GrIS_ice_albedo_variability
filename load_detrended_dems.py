# load_detrended_dems
import xarray as xr
import salem
from load_uav_data import add_srs

detrended_mean = xr.open_dataset('/scratch/UAV/uav2017_dem/dems2017_detrendedmean_commongrid_999.nc')
detrended_mean = add_srs(detrended_mean, 'epsg:32623')
# AOI defined manually from within QGIS
shpf = salem.read_shapefile('/scratch/UAV/uav2017_dem/dem2017_commonarea_999.shp')

detrended = xr.open_dataset('/scratch/UAV/uav2017_dem/dems2017_detrended_commongrid_999.nc')
detrended = add_srs(detrended, 'epsg:32623')