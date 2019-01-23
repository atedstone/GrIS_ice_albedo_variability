"""
Plot a side-by-side comparison of sample acquisitions from S6 and UPE.

Note that images are loaded in again here, using georaster with downsampl 
functionality, in order to stop matplotlib from crashing with the high res images.

"""

import matplotlib.pyplot as plt
import xarray as xr
import matplotlib as mpl
import seaborn as sns
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec

from load_uav_data import *

sns.set_style("ticks")
sns.set_context('paper', rc={"font.size":8,"axes.titlesize":8,"axes.labelsize":8,"legend.fontsize":8})

fig = plt.figure(figsize=(6.5, 7))
gs = GridSpec(5,2, figure=fig)

## S6 Alb
ax = plt.subplot(gs[0:2,0])
s6_alb = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170721_refl_5cm_commongrid_albedo.tif_epsg32622.tif', downsampl=4)
s6_alb.r = np.where(s6_alb.r < 0, np.nan, s6_alb.r)
plt.imshow(s6_alb.r, vmin=0, vmax=1, cmap='Greys_r')
#uav_alb.Band1.sel(time='2017-07-21').squeeze().plot.imshow(vmin=0, vmax=1, cmap='Greys_r', add_colorbar=False)
plt.xticks([])
plt.yticks([])
plt.title('S6', fontdict={'fontweight':'bold'})
plt.xlabel('')
plt.ylabel('')
plt.axis('off')
ax.annotate('(a)', fontsize=8, fontweight='bold', xy=(0.2,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

## UPE Alb
ax = plt.subplot(gs[0:2,1])
upe_alb_plot = georaster.SingleBandRaster('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_refl_albedo.tif', downsampl=3)
upe_alb = xr.open_rasterio('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_refl_albedo.tif')
upe_alb.attrs['pyproj_srs'] = 'epsg:32622'
upe_alb_plot.r = np.where(upe_alb_plot.r < 0, np.nan, upe_alb_plot.r)
plt.imshow(upe_alb_plot.r, vmin=0, vmax=1, cmap='Greys_r')
#upe_alb.squeeze().plot.imshow(vmin=0, vmax=1, cmap='Greys_r', add_colorbar=False)
plt.xticks([])
plt.yticks([])
plt.title('UPE', fontdict={'fontweight':'bold'})
plt.xlabel('')
plt.ylabel('')
plt.axis('off')
ax.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.2,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

## Albedo colourbar
ax_alcb = fig.add_axes([0.41, 0.83, 0.18, 0.01])
cmap_plot = mpl.cm.Greys_r
cb1 = mpl.colorbar.ColorbarBase(ax_alcb, cmap=cmap_plot,
                                orientation='horizontal')
cb1.set_label('UAS albedo')
cb1.set_ticks(np.arange(0.0,1.1,0.2), [0,0.2,0.4,0.6,0.8,1])
sns.despine()



## S6 Class
ax = plt.subplot(gs[2:4,0])
# Create a categorical colourmap.
categories = ['Unknown', 'Water', 'Snow', 'CI', 'LA', 'HA', 'CC']
vals = [0, 1, 2, 3, 4, 5, 6]
cmap = mpl.colors.ListedColormap(['#000000','#08519C','white', '#C6DBEF', '#FDBB84', '#B30000', '#762A83'])
s6_class = georaster.SingleBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/uav_20170721_refl_5cm_commongrid_classified.tif_epsg32622.tif', downsampl=4)
s6_class.r = np.where(s6_class.r < 0, np.nan, s6_class.r)
plt.imshow(s6_class.r, cmap=cmap, vmin=0, vmax=7)
#uav_class.Band1.sel(time='2017-07-21').squeeze().plot.imshow(cmap=cmap, vmin=0, vmax=7, add_colorbar=False)
plt.xticks([])
plt.yticks([])
plt.title('')
plt.xlabel('')
plt.ylabel('')
plt.axis('off')
ax.annotate('(c)', fontsize=8, fontweight='bold', xy=(0.2,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

## UPE Class
ax = plt.subplot(gs[2:4,1])
upe_class = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_refl_class.nc',
	chunks={'x':1000, 'y':1000}) 
upe_class_plot = georaster.SingleBandRaster('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_refl_classified.tif')
upe_class.classified.attrs['pyproj_srs'] = 'epsg:32622'
#upe_class.classified.plot(cmap=cmap, vmin=0, vmax=7, add_colorbar=False)
plt.imshow(upe_class_plot.r, vmin=0, vmax=7, cmap=cmap)
plt.xticks([])
plt.yticks([])
plt.title('')
plt.xlabel('')
plt.ylabel('')
plt.axis('off')
ax.annotate('(d)', fontsize=8, fontweight='bold', xy=(0.2,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

## Classes colourbar
ax_clcb = fig.add_axes([0.41, 0.33, 0.18, 0.01])
cmap_plot = mpl.colors.ListedColormap(['white', '#C6DBEF', '#FDBB84', '#B30000'])
cmap_norm = mpl.colors.Normalize(vmin=0,vmax=4)
cb1 = mpl.colorbar.ColorbarBase(ax_clcb, cmap=cmap_plot, norm=cmap_norm,
                                orientation='horizontal')
cb1.set_ticks([0.5,1.5,2.5,3.5])
cb1.set_ticklabels(['Snow', 'CI', 'LA', 'HA'])
sns.despine()

## Middle: context map
ax_inset = fig.add_axes([0.41,0.43,0.2,0.27])

#ax_inset.set_axis_bgcolor('none')

for axis in ['top','bottom','left','right']:
	ax_inset.spines[axis].set_linewidth(0)

im = mpimg.imread('/home/at15963/Dropbox/work/papers/tedstone_uavts/gris_context.png')
ax_inset.imshow(im,interpolation='none')
ax_inset.set_xticks([])
ax_inset.set_yticks([])
ax_inset.set_facecolor('none')


## S6 alb/class histogram
ax = plt.subplot(gs[4,0])

ytick_locs = np.array([0, 5e5, 1e6, 1.5e6])
ytick_labels = (ytick_locs * (0.05**2)).astype(int) #sq m

uavha = uav_alb.Band1.sel(time='2017-07-21').salem.roi(shape=uav_poly)
uavhc = uav_class.Band1.sel(time='2017-07-21').salem.roi(shape=uav_poly)

# uavha.where(uavhc == 5) \
# 	.plot.hist(bins=50, range=(0,1), alpha=0.7, label='High Biomass', color='#B30000')
# uavha.where(uavhc == 4) \
# 	.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Low Biomass', color='#FDBB84')
# uavha.where(uavhc == 3) \
# 	.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Clean Ice', color='#4292C6')
# uavha.where(uavhc == 2) \
# 	.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Snow', color='#B9B9B9')

cmap_hist = mpl.colors.ListedColormap(['#C6DBEF','#B30000','#FDBB84','#B9B9B9'])
color_dict = {'Snow':'#B9B9B9', 'CI':'#4292C6', 'LA':'#FDBB84', 'HA':'#B30000'}

counts2, bins = np.histogram(uavha.where(uavhc == 2), bins=50, range=(0,1))
counts3, bins = np.histogram(uavha.where(uavhc == 3), bins=50, range=(0,1))
counts4, bins = np.histogram(uavha.where(uavhc == 4), bins=50, range=(0,1))
counts5, bins = np.histogram(uavha.where(uavhc == 5), bins=50, range=(0,1))
counts_all_s6 = pd.DataFrame({'Snow':counts2, 'CI':counts3, 'LA':counts4, 'HA':counts5}, index=bins[:-1])
counts_all_s6 = counts_all_s6 * (0.05**2)
ax = counts_all_s6.plot(kind='bar', stacked=True, color=[color_dict.get(x) for x in counts_all_s6.columns], width=1, ax=ax, legend=False, linewidth=0)

ax.spines['left'].set_position(('outward', 5))

plt.legend(loc=(0.7,0.2), frameon=False)

plt.xticks(np.arange(0,60,10), [0.0,0.2,0.4,0.6,0.8,1.0])

#plt.yticks(ytick_locs, ytick_labels)
plt.ylabel('Area (sq. m)')
#plt.xlim(0.1,0.9)
plt.xlabel('Albedo')
plt.title('')
plt.ylim(0,3500)
ax.tick_params(axis='x', labelrotation=0)
sns.despine()

ax.annotate('(e)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

class_counts_s6 = uavhc.groupby(uavhc).count().load().to_pandas()



## UPE alb/class histogram
ax = plt.subplot(gs[4,1])

uavha_upe = upe_alb.salem.roi(shape=uav_poly_upe)
uavhc_upe = upe_class.classified.salem.roi(shape=uav_poly_upe)
uavha_upe['x'] = uavhc_upe.x
uavha_upe['y'] = uavhc_upe.y

# uavha_upe.where(uavhc_upe == 2) \
# 	.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Snow', color='#B9B9B9')
# uavha_upe.where(uavhc_upe == 3) \
# 	.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Clean Ice', color='#4292C6')
# uavha_upe.where(uavhc_upe == 4) \
# 	.plot.hist(bins=50, range=(0,1), alpha=0.7, label='Low Biomass', color='#FDBB84')
# uavha_upe.where(uavhc_upe == 5) \
# 	.plot.hist(bins=50, range=(0,1), alpha=0.7, label='High Biomass', color='#B30000')

counts2, bins = np.histogram(uavha_upe.where(uavhc_upe == 2), bins=50, range=(0,1))
counts3, bins = np.histogram(uavha_upe.where(uavhc_upe == 3), bins=50, range=(0,1))
counts4, bins = np.histogram(uavha_upe.where(uavhc_upe == 4), bins=50, range=(0,1))
counts5, bins = np.histogram(uavha_upe.where(uavhc_upe == 5), bins=50, range=(0,1))

# counts6, bins = np.histogram(uavha_upe.where(uavhc_upe == 6), bins=50, range=(0,1))
# sum(counts6) * (0.05**2)
# counts1, bins = np.histogram(uavha_upe.where(uavhc_upe == 1), bins=50, range=(0,1))
# sum(counts1) * (0.05**2)

counts_all_upe = pd.DataFrame({'Snow':counts2, 'CI':counts3, 'LA':counts4, 'HA':counts5}, index=bins[:-1])

counts_all_upe = counts_all_upe * (0.05**2)

counts_all_upe.plot(kind='bar', stacked=True, color=[color_dict.get(x) for x in counts_all_upe.columns], width=1, ax=ax, legend=False, linewidth=0)
plt.xticks(np.arange(0,60,10), [0.0,0.2,0.4,0.6,0.8,1.0])

#plt.yticks(ytick_locs, ytick_labels)
plt.ylabel('Area (sq. m)')
plt.ylim(0,3500)
#plt.xlim(0.1,0.9)
plt.xlabel('Albedo')
plt.ylabel('')
ticks,labels = plt.yticks()
#plt.yticks(ticks,[])
plt.title('')
ax.tick_params(axis='x', labelrotation=0)
sns.despine()
ax.spines['left'].set_visible(False)
plt.yticks([])
ax.annotate('(f)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')


class_counts_upe = uavhc_upe \
		.groupby(uavhc_upe).count().load().to_pandas()


plt.subplots_adjust(hspace=0.05)

## North arrow
ax = fig.add_axes([0.85,0.85,0.1,0.1])
plt.annotate('N', (0.5,0.7), xytext=(0.5, 0), xycoords='axes fraction',
  arrowprops=dict(arrowstyle='simple', color='black'), horizontalalignment='center')
for axis in ['top','bottom','left','right']:
  ax.spines[axis].set_linewidth(0)
plt.yticks([])
plt.xticks([])

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission1/figures/s6_upe_comparison.png', dpi=300)
"""
To do:

Add sampled total area for each location - within specified polygon.
Add scale bars
Add location map context.
Mark dominant slope direction on the two top plots. 
Add some boxing or something to illustrate main supraglacial stream on S6 plot.

"""