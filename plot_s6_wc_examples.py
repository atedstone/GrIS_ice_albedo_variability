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

import georaster

sns.set_context('paper')
sns.set_style("ticks")

bbox = (571683.122,571725.199,7440968.506,7440998.493)
xx = [571683.122,571725.199,571725.199,571683.122,571683.122]
yy = [7440998.493,7440998.493,7440968.506,7440968.506,7440998.493]

fig = plt.figure(figsize=(6,6))
gs = GridSpec(1,2)

gs00 =  GridSpecFromSubplotSpec(19,1, subplot_spec=gs[0])
gs01 =  GridSpecFromSubplotSpec(3,1, subplot_spec=gs[1])


# Colorbar
cbax = fig.add_subplot(gs00[18,0])

# Change 20->21st
fig.add_subplot(gs00[0:9,0])
im1 = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav0721-uav0720_band4_epsg32622.tif', downsampl=4)
im1.r = np.where(im1.r < -10, np.nan, im1.r)
plt.imshow(im1.r, cmap='PuOr', vmin=-0.25, vmax=0.25, extent=im1.extent, zorder=1)
plt.plot(xx,yy,'k-',zorder=100)
#im = None
plt.xticks([])
plt.yticks([])

# Change 21st->22nd
fig.add_subplot(gs00[9:18,0])
im = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav0722-uav0721_band4_epsg32622.tif', downsampl=4)
im.r = np.where(im.r < -10, np.nan, im.r)
plt.imshow(im.r, cmap='PuOr', vmin=-0.25, vmax=0.25, extent=im.extent)
plt.plot(xx,yy,'k-',zorder=100)
im = None
plt.xticks([])
plt.yticks([])

plt.colorbar(cax=cbax, orientation='horizontal', fraction=0.3)


# RGB zoom 20th
fig.add_subplot(gs01[0,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170720_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r)
im = None
plt.xticks([])
plt.yticks([])

# RGB zoom 21st
fig.add_subplot(gs01[1,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170721_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r)
im = None
plt.xticks([])
plt.yticks([])

# RGB zoom 22nd
fig.add_subplot(gs01[2,0])
im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170722_refl_5cm_commongrid.tif_epsg32622.tif', 
	load_data=bbox, latlon=False, bands=(1,2,3))
im.r = np.moveaxis(np.array([im.r[:,:,2],im.r[:,:,1],im.r[:,:,0]]),0,2)
plt.imshow(im.r)
im = None
plt.xticks([])
plt.yticks([])
#(571672,571766,7440962,7441012)




