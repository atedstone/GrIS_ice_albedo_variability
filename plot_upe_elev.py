"""
The elevation story at Upernavik site

"""

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import xarray as xr
import numpy as np
import seaborn as sns
import pandas as pd

import georaster

fig = plt.figure(figsize=(6,3))
gs = GridSpec(2,2, figure=fig)

## Detrended DEM
ax = fig.add_subplot(gs[0:,0])
# Created from .nc version using gdalwarp -of GTiff
upe_dem_plot = georaster.SingleBandRaster('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.tif')
plt.imshow(upe_dem_plot.r, cmap='RdBu_r', vmin=-0.2, vmax=0.2, extent=upe_dem_plot.extent)
plt.title('DEM')
plt.colorbar()

# Scale bar

## Zoom of detrended DEM
ax_zoom = fig.add_subplot(gs[0,1])
upe_dem_plot_zoom = georaster.SingleBandRaster('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.tif', 
	load_data=(415970,416075,8.08862e06,8.08867e06), latlon=False)
#upe_dem_plot_zoom = upe_dem_plot
plt.imshow(upe_dem_plot_zoom.r, cmap='RdBu_r', vmin=-0.2, vmax=0.2, extent=upe_dem_plot_zoom.extent)
xx = [415970, 416075, 416075, 415970, 415970]
yy = [8.08867e06, 8.08867e06,8.08862e06 ,8.08862e06, 8.08867e06]
plt.plot(xx,yy, 'k-', zorder=100)

# Scale bar


## Boxenplots by elevation
ax = fig.add_subplot(gs[1,1])

detrended = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.nc',
	chunks={'x':1000, 'y':1000})
classified = xr.open_dataset('/scratch/UAV/L3/uav_20180724_PM_refl_class_clf20190130_171930.nc',
	chunks={'x':1000, 'y':1000}) 
classified['x'] = detrended.x
classified['y'] = detrended.y


just_class = classified.classified.stack(dim=('x','y')).to_pandas()
just_elev = detrended.detrended.stack(dim=('x','y')).to_pandas()

combo = pd.concat((just_class,just_elev), axis=1).dropna()
combo.columns = ['Surface Type', 'Detrended Elevation (m)']
combo = combo[combo['Surface Type'] > 0]
sns.boxenplot(data=combo, x='Surface Type', y='Detrended Elevation (m)', ax=ax) 
ticks, labels = plt.xticks()
names = ['Water', 'Snow', 'CI', 'LA', 'HA', 'CC']
plt.xticks(ticks, names)