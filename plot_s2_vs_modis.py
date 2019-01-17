"""

S2 versus MODIS

"""

# Load data from across both the intersecting MODIS pixels
s2_in_modis = s2_data.albedo.salem.roi(shape='/scratch/UAV/coincident_s6_modis_latlon.shp')


s2_in_modis.mean(dim=('x','y')).load()

figure(),s2_in_modis.sel(time='2017-07-21').plot.hist(bins=50,range=(0,1)),ylim(0,350)