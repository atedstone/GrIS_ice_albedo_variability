"""
Indicative weathering crust presence, S6 time series

"""
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.gridspec import GridSpecFromSubplotSpec
import xarray as xr
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.patheffects as path_effects

import georaster

sns.set_context('paper')
sns.set_style("ticks")

bbox = (571683.122,571725.199,7440968.506,7440998.493)
xx = [571683.122,571725.199,571725.199,571683.122,571683.122]
yy = [7440998.493,7440998.493,7440968.506,7440968.506,7440998.493]

mag_bbox = (bbox[0] + ((bbox[1]-bbox[0])/3), bbox[0] + ((bbox[1]-bbox[0])/3*2),
                  bbox[2] + ((bbox[3]-bbox[2])/3), bbox[2] + ((bbox[3]-bbox[2])/3*2))
m_xx = [mag_bbox[0], mag_bbox[1], mag_bbox[1], mag_bbox[0], mag_bbox[0]]
m_yy = [mag_bbox[3], mag_bbox[3], mag_bbox[2], mag_bbox[2], mag_bbox[3]]

fig = plt.figure(figsize=(8,6))
gs = GridSpec(1,3)

gs00 = GridSpecFromSubplotSpec(20,1, subplot_spec=gs[0])
gs01 = GridSpecFromSubplotSpec(3,1, subplot_spec=gs[1])
gs02 = GridSpecFromSubplotSpec(3,1, subplot_spec=gs[2])

# Colorbar
cbax = fig.add_subplot(gs00[18,0])
cmap = plt.get_cmap('PuOr')
cmap.set_bad('white')

# Change 20->21st
ax = fig.add_subplot(gs00[0:9,0])
im1 = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav0721-uav0720_band4_epsg32622.tif', downsampl=4)
im_eg = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170720_refl_5cm_commongrid.tif_epsg32622.tif', downsampl=4)
im1.r = np.where(im1.r < -10, np.nan, im1.r)
im1.r = np.where(im_eg.r == 0, np.nan, im1.r)
plt.imshow(im1.r, cmap=cmap, vmin=-0.25, vmax=0.25, extent=im1.extent, zorder=1)
plt.plot(xx,yy,'k-',zorder=100)
#im = None
plt.xticks([])
plt.yticks([])
plt.axis('off')
ax.annotate('(a)', fontsize=8, fontweight='bold', xy=(0.01,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')
ax.annotate('20-21 July', fontsize=8, xy=(0.01,0.88), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Change 21st->22nd
ax = fig.add_subplot(gs00[9:18,0])
im = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav0722-uav0721_band4_epsg32622.tif', downsampl=4)
im.r = np.where(im.r < -10, np.nan, im.r)
im.r = np.where(im_eg.r == 0, np.nan, im.r)
plt.imshow(im.r, cmap=cmap, vmin=-0.25, vmax=0.25, extent=im.extent)
plt.plot(xx,yy, 'k-', zorder=100)
im = None
plt.xticks([])
plt.yticks([])
plt.axis('off')
ax.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.01,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')
ax.annotate('21-22 July', fontsize=8, xy=(0.01,0.88), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

cb = plt.colorbar(cax=cbax, orientation='horizontal')
cb.set_label('$\Delta R_{820-860nm}$')

im_eg = None

# Scale bar for change plots
scale_bar_x = [571776, 571776+50]
scale_bar_y = [7440890, 7440890]
plt.plot(scale_bar_x, scale_bar_y, linewidth=3, color='black', solid_capstyle='butt')
ax.annotate('50 m', fontsize=8, xy=(scale_bar_x[1]-25,scale_bar_y[0]-28),
           horizontalalignment='center', verticalalignment='bottom')


# RGB zoom 20th
ax = fig.add_subplot(gs01[0,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170720_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r, extent=im.extent)
plt.plot(m_xx, m_yy, color='#F5E61F', zorder=100, linewidth=0.5)
im = None
plt.xticks([])
plt.yticks([])
ax.annotate('(c)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Macro RGB zoom 20th
ax = fig.add_subplot(gs02[0,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170720_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=mag_bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r)
im = None
plt.xticks([])
plt.yticks([])
ax.annotate('(f)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')


# RGB zoom 21st
ax = fig.add_subplot(gs01[1,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170721_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r, extent=im.extent)
plt.plot(m_xx, m_yy, color='#F5E61F', zorder=100, linewidth=0.5)
im = None
plt.xticks([])
plt.yticks([])
ax.annotate('(d)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Scale bar for regular zoom plots
scale_bar_x = [571712, 571712+10]
scale_bar_y = [7440975, 7440975]
plt.plot(scale_bar_x, scale_bar_y, linewidth=2, color='black', solid_capstyle='butt')
ax.annotate('10 m', fontsize=8, xy=(scale_bar_x[1]-5,scale_bar_y[0]-4),
           horizontalalignment='center', verticalalignment='bottom', color='black')


# Macro RGB zoom 21st
ax = fig.add_subplot(gs02[1,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170721_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=mag_bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r, extent=im.extent)
im = None
plt.xticks([])
plt.yticks([])
ax.annotate('(g)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Scale bar for macro zoom plots
scale_bar_x = [571707, 571707+3]
scale_bar_y = [7440980.6, 7440980.6]
plt.plot(scale_bar_x, scale_bar_y, linewidth=2, color='black', solid_capstyle='butt')
ax.annotate('3 m', fontsize=8, xy=(scale_bar_x[1]-1.5,scale_bar_y[0]-1.3),
           horizontalalignment='center', verticalalignment='bottom', color='black')


# RGB zoom 22nd
ax = fig.add_subplot(gs01[2,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170722_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r, extent=im.extent)
plt.plot(m_xx, m_yy, color='#F5E61F', zorder=100, linewidth=0.5)
im = None
plt.xticks([])
plt.yticks([])
ax.annotate('(e)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Macro RGB zoom 22nd
ax = fig.add_subplot(gs02[2,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170722_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=mag_bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r)
im = None
plt.xticks([])
plt.yticks([])
ax.annotate('(h)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top', color='black')

# Add row labels
fig.text(0.375, 0.76, '20 July', fontsize=8, rotation=90, verticalalignment='center')
fig.text(0.375, 0.48, '21 July', fontsize=8, rotation=90, verticalalignment='center')
fig.text(0.375, 0.22, '22 July', fontsize=8, rotation=90, verticalalignment='center')

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission1/figures/weathering_crust.png', dpi=300)

