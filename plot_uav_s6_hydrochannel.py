import matplotlib.pyplot as plt

import seaborn as sns

from load_uav_data import * 

sns.set_context('paper')
sns.set_style("ticks")

detrended = xr.open_dataset('/scratch/UAV/uav2017_dem/dems2017_detrended_commongrid_399_epsg32622.nc') 

plt.figure()

plt.subplot(211)
detrended.detrended.sel(time='2017-07-21', x=slice(571633, 571795), y=slice(7440960,7441025)) \
	.plot.imshow(vmin=-0.2, vmax=0.2, cmap='RdBu_r')

# this is a different projection...eugh
plt.subplot(212)
uav_class.Band1.sel(time='2017-07-21', x=slice(571633, 571795), y=slice(7440960,7441025)) \
	.plot.imshow(vmin=0,vmax=6)

	571633.010,7440960.123
	571795.149,7441025.279

	demnp = np.flipud(dems.Band1.sel(time='2017-07-21').values)
	demnp = np.flipud(dem18.Band1.squeeze().values)
	demnp = np.where(demnp == 0, -9999, demnp)
	demrd = rd.rdarray(demnp, no_data=-9999)
	demrd.geotransform = (310895.0, 0.05, 0.0, 7446839.0, 0.0, -0.05)
	demrd.projection = 'PROJCS["WGS 84 / UTM zone 23N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32623"]]'

	demrd_fill = rd.FillDepressions(demrd, in_place=False)
	accum = rd.FlowAccumulation(demrd_fill, method='D8')
