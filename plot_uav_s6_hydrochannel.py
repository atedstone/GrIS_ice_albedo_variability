import matplotlib.pyplot as plt

import seaborn as sns

from load_uav_data import * 

sns.set_context('paper')
sns.set_style("ticks")

detrended = xr.open_dataset('/scratch/UAV/uav2017_dem/dems2017_detrended_commongrid_399.nc') 

plt.figure()

plt.subplot(211)
detrended.detrended.sel(time='2017-07-21', x=slice(311000, 311160), y=slice(7446610,7446670)) \
	.plot.imshow(vmin=-0.2, vmax=0.2, cmap='RdBu_r')

# this is a different projection...eugh
plt.subplot(212)
uav_class.Band1.sel(time='2017-07-21', x=slice(311000, 311160), y=slice(7446610,7446670)) \
	.plot.imshow(vmin=0,vmax=6)