# Convert UAV data to espg32622

gdalwarp -t_srs EPSG:32622 uav_20170715_refl_5cm_commongrid.tif uav_20170715_refl_5cm_commongrid_epsg32622.tif


for f in *commongrid*tif; do gdalwarp -t_srs EPSG:32622 -of NetCDF $f ${f}_epsg32622.nc; done

#Have now done the step above; but will need to do yet more fudging to convert back into net cdf format (probably a new script)


# uav_20170715_dem_5cm._commongrid.nc
# uav_20170720_dem_5cm._commongrid.nc
# uav_20170721_dem_5cm._commongrid.nc or  other tif options
# uav_20170722_dem_5cm._commongrid.nc
# uav_20170723_dem_5cm._commongrid.nc



gdalwarp -t_srs EPSG:32622 -of NetCDF uav_20170715_dem_5cm._commongrid.tif uav_20170715_dem_5cm._commongrid_epsg32622.nc
gdalwarp -t_srs EPSG:32622 -of NetCDF uav_20170720_dem_5cm_v2_gcpzacc20._commongrid.tif uav_20170720_dem_5cm_v2_gcpzacc20._commongrid_epsg32622.nc
gdalwarp -t_srs EPSG:32622 -of NetCDF uav_20170721_dem_5cm_gcpzacc20._commongrid.tif uav_20170721_dem_5cm_gcpzacc20._commongrid_epsg32622.nc
gdalwarp -t_srs EPSG:32622 -of NetCDF uav_20170722_dem_5cm._commongrid.tif uav_20170722_dem_5cm._commongrid_epsg32622.nc
gdalwarp -t_srs EPSG:32622 -of NetCDF uav_20170723_dem_5cm._commongrid.tif uav_20170723_dem_5cm._commongrid_epsg32622.nc