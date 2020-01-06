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

sns.set_context('paper', rc={"font.size":8,"axes.titlesize":8,"axes.labelsize":8,"legend.fontsize":8})
sns.set_style('ticks')

fig = plt.figure(figsize=(6,3))
gs = GridSpec(2,4, figure=fig)

## Detrended DEM
ax = fig.add_subplot(gs[0:,0:2])
# Created from .nc version using gdalwarp -of GTiff
upe_dem_plot = georaster.SingleBandRaster('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.tif')
plt.imshow(upe_dem_plot.r, cmap='RdBu_r', vmin=-0.2, vmax=0.2, extent=upe_dem_plot.extent)
plt.axis('off')
plt.yticks([])
plt.xticks([])
cb = plt.colorbar(orientation='horizontal', shrink=0.4, aspect=10, fraction=0.05, pad=0.01)
cb.set_label('Detr. elev. (m)')
cb.set_ticks([-0.2, -0.1, 0, 0.1, 0.2])
ax.annotate('(a)', fontsize=8, fontweight='bold', xy=(0.1,0.90), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Plot extent of zoom area
xx = [415970, 416025, 416025, 415970, 415970]
yy = [8.08867e06, 8.08867e06,8.08862e06 ,8.08862e06, 8.08867e06]
plt.plot(xx,yy, 'k-', zorder=100)

# Scale bar for full area
scale_bar_x = [416075, 416075+50]
scale_bar_y = [8088500,8088500]
plt.plot(scale_bar_x, scale_bar_y, linewidth=3, color='black', solid_capstyle='butt')
ax.annotate('50 m', fontsize=8, xy=(scale_bar_x[1]-25,scale_bar_y[0]-25),
           horizontalalignment='center', verticalalignment='bottom', color='black')

# Make this subplot and associated colorbar a bit bigger, manually
#new_bb = [0.28,0,0.95,0.95]
new_bb = [-0.05,0,0.55,0.95]
ax.set_position(new_bb)

new_cb_bb = [0.04,0.17,0.16,0.03] 
cb.ax.set_position(new_cb_bb)



## Zoom of detrended DEM
ax_zoom = fig.add_subplot(gs[0,2])
upe_dem_plot_zoom = georaster.SingleBandRaster('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.tif', 
	load_data=(415970,416025,8.08862e06,8.08867e06), latlon=False) #416075-->416025
plt.imshow(upe_dem_plot_zoom.r, cmap='RdBu_r', vmin=-0.2, vmax=0.2, extent=upe_dem_plot_zoom.extent)
plt.yticks([])
plt.xticks([])
ax_zoom.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Scale bar for zoom area
scale_bar_x = [416000, 416000+20]
scale_bar_y = [8.088629e06,8.088629e06]
plt.plot(scale_bar_x, scale_bar_y, linewidth=3, color='black', solid_capstyle='butt')
ax_zoom.annotate('20 m', fontsize=8, xy=(scale_bar_x[1]-10,scale_bar_y[0]-8),
           horizontalalignment='center', verticalalignment='bottom', color='black')

old_bb = ax_zoom.get_position().bounds
xstart = old_bb[0] - 0.07
new_bb = (xstart, old_bb[1]+0.01, old_bb[2], old_bb[3])
ax_zoom.set_position(new_bb)


## Albedo versus elevation
ax_alb_elev = fig.add_subplot(gs[0,3])
detrended = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.nc',
	chunks={'x':1000, 'y':1000})
classified = xr.open_dataset('/scratch/UAV/L3/uav_20180724_PM_refl_class_clf20190130_171930.nc',
	chunks={'x':1000, 'y':1000}) 
classified['x'] = detrended.x
classified['y'] = detrended.y

combined = pd.DataFrame({
	'dem':detrended.detrended.stack(dim=('x','y')).to_pandas(),
	'albedo':classified.albedo.stack(dim=('x','y')).to_pandas()
	})

combined_nonan = combined.dropna()

alb_binned = pd.cut(combined_nonan.albedo,bins=np.arange(0,1,0.05))

meds = combined_nonan.dem.groupby(alb_binned).median()
std = combined_nonan.dem.groupby(alb_binned).std()
counts = combined_nonan.dem.groupby(alb_binned).count()

stats = pd.DataFrame({
	'elev_med':meds,
	'elev_std':std,
	'npx':counts,
	'perc':(100 / counts.sum() * counts),
	'alb':np.arange(0.025,0.975, 0.05)
	}, index=np.arange(0.025,0.975, 0.05))

plt.errorbar(stats.alb, stats.elev_med, yerr=stats.elev_std, mfc='black', 
	ecolor='black', elinewidth=0.5, mec='black', color='none', marker='o', ms=3)

plt.yticks([-0.3, -0.2, -0.1, 0.0, 0.1], [-0.3, -0.2, -0.1, 0.0, 0.1])

plt.xlabel('Albedo')
plt.ylabel('Detr. Elev. (m)')

old_bb = ax_alb_elev.get_position().bounds
new_bb = (old_bb[0], old_bb[1]+0.05, old_bb[2], old_bb[3]-0.06)
ax_alb_elev.set_position(new_bb)

ax2 = ax_alb_elev.twinx()
plt.plot(stats.alb, stats.perc, 'gray')
plt.ylabel('% of study area', color='gray')

plt.xticks([0.1, 0.5, 0.9], [0.1, 0.5, 0.9])

ax2.set_position(new_bb)

ax_alb_elev.set_zorder(ax2.get_zorder()+1) # put ax in front of ax2
ax_alb_elev.patch.set_visible(False) # hide the 'canvas' 

ax_alb_elev.annotate('(c)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

sns.despine(ax=ax_alb_elev, right=False)



## Boxenplots by elevation
ax_box = fig.add_subplot(gs[1,2:])

detrended = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.nc',
	chunks={'x':1000, 'y':1000})
classified = xr.open_dataset('/scratch/UAV/L3/uav_20180724_PM_refl_class_clf20190130_171930.nc',
	chunks={'x':1000, 'y':1000}) 
classified['x'] = detrended.x
classified['y'] = detrended.y


just_class = classified.classified.stack(dim=('x','y')).to_pandas()
just_elev = detrended.detrended.stack(dim=('x','y')).to_pandas()

color_dict = {'Snow':'#B9B9B9', 'CI':'#4292C6', 'LA':'#FDBB84', 'HA':'#B30000', 'Water':'#08519C', 'CC':'#762A83'}

combo = pd.concat((just_class,just_elev), axis=1).dropna()
combo.columns = ['Surface Type', 'Detrended Elevation (m)']
combo = combo[combo['Surface Type'] > 0]
colors = colors = ['#08519C', '#B9B9B9', '#4292C6', '#FDBB84', '#B30000', '#762A83']
with sns.color_palette(colors):
	sns.boxenplot(data=combo, x='Surface Type', y='Detrended Elevation (m)', ax=ax_box)
ticks, labels = plt.xticks()
names = ['Water', 'Snow', 'CI', 'LA', 'HA', 'CC']
plt.xticks(ticks, names)
plt.xlabel('')
plt.ylabel('Detr. elev. (m)')
plt.yticks([-0.6, -0.4, -0.2, 0, 0.2], [-0.6, -0.4, -0.2, 0, 0.2])

sns.despine(ax=ax_box)

ax_box.annotate('(d)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission2/figures/upe_elevation_clf20190130_171930.png', dpi=300)