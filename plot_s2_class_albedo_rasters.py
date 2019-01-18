"""

Plot Sentinel 2 classification and albedo across MODIS pixels area

"""

import matplotlib.pyplot as plt

import seaborn as sns

import cartopy as cp

from matplotlib.gridspec import GridSpec
#import geopandas as gpd

sns.set_context('paper')
sns.set_style('ticks')

#from load_s2_data import *
from compare_uav_s2 import *

# In epsg:32622
modis_area_x = slice(571103, 572464)
modis_area_y = slice(7441243, 7440595)

#modis_boxes = gpd.read_file('/scratch/UAV/coincident_s6_modis_latlon.shp')

### Rasters
def add_common_features(ax):
	ax.add_geometries(cp.io.shapereader.Reader('/scratch/UAV/coincident_s6_modis_latlon.shp').geometries(),
                  cp.crs.PlateCarree(),
                  facecolor='none', color='white')

	ax.add_geometries(cp.io.shapereader.Reader('/scratch/UAV/uav_2017_area.shp').geometries(),
                  cp.crs.PlateCarree(),
                  facecolor='none', color='black')

	ax.set_title('')

plt.figure()

#map_proj = cp.crs.Stereographic(central_latitude=71, central_longitude=-40)
map_proj = cp.crs.UTM(zone=22)

# 20 July class
ax = plt.subplot(221, projection=map_proj)
s2_data.classified.sel(x=modis_area_x, y=modis_area_y, time='2017-07-20').plot(ax=ax, cmap=cmap, vmin=0, vmax=6, add_colorbar=False)
add_common_features(ax)

# 21 July class
ax = plt.subplot(222, projection=map_proj)
s2_data.classified.sel(x=modis_area_x, y=modis_area_y, time='2017-07-21').plot(ax=ax, cmap=cmap, vmin=0, vmax=6)
add_common_features(ax)

# 20 July albedo
ax = plt.subplot(223, projection=map_proj)
s2_data.albedo.sel(x=modis_area_x, y=modis_area_y, time='2017-07-20').plot(ax=ax, vmin=0.2, vmax=0.8, cmap='Greys_r', add_colorbar=False)
add_common_features(ax)

# 21 July class
ax = plt.subplot(224, projection=map_proj)
s2_data.albedo.sel(x=modis_area_x, y=modis_area_y, time='2017-07-21').plot(ax=ax, vmin=0.2, vmax=0.8, cmap='Greys_r')
add_common_features(ax)


### Associated statistics...

# Calculate percentage coverage of each surface type as measured by Sentinel-2 in the UAV area
for t in subset.time:
	counts = subset.sel(time=t).groupby(subset.sel(time=t)).count().load()
	percs = 100 / counts.sum() * counts
	print(t, percs)

# Surface type distributions
changed_20 = uav_alb_dists['2017-07-20'][uav_alb_dists['2017-07-20']['changes'] == -1]
changed_21 = uav_alb_dists['2017-07-21'][uav_alb_dists['2017-07-21']['changes'] == -1]

print('20th LA no change: ', uav_dists_perc['2017-07-20'][(changes == 0) & (uav_dists_perc['2017-07-20']['s2_class'] == 4)].mean())
print('20th changed px:', uav_dists_perc['2017-07-20'][changes == -1].mean())
print('21st LA no change: ', uav_dists_perc['2017-07-21'][changes == 0 & (uav_dists_perc['2017-07-21']['s2_class'] == 4)].mean())
print('21st changed px:', uav_dists_perc['2017-07-21'][changes == -1].mean())




### Sub-S2-pixel albedo distributions
fig = plt.figure(figsize=(4,6))
gs = GridSpec(4,2, figure=fig)

# Boxenplots
ax = fig.add_subplot(gs[0,0])



xvals = np.arange(0,1,0.01)

## 07-20 CI
ax = fig.add_subplot(gs[1,0])
for ix, row in uav_alb_dists['2017-07-20'].iterrows():
	if row.s2_class == 3:
		plt.plot(xvals, row.binned, alpha=0.5, color='#C6DBEF')
dist = uav_alb_dists['2017-07-20'][uav_alb_dists['2017-07-20'].s2_class == 3].binned.mean()
plt.plot(xvals, dist, 'k')
plt.title('20 July')
plt.ylim(0,8.5)
plt.tick_params(axis='x', bottom='off', top='off')
plt.ylabel('CI % of S2 pixel')

## 07-20 LA
ax = fig.add_subplot(gs[2,0])
for ix, row in uav_alb_dists['2017-07-20'].iterrows():
	if row.s2_class == 4:
		plt.plot(xvals, row.binned, alpha=0.5, color='#FDBB84')
dist = uav_alb_dists['2017-07-20'][uav_alb_dists['2017-07-20'].s2_class == 4].binned.mean()
plt.plot(xvals, dist, 'k')
plt.ylim(0,8.5)
plt.tick_params(axis='x', top='off')
plt.ylabel('LA % of S2 pixel')

## 07-21 CI
ax = fig.add_subplot(gs[1,1])
for ix, row in uav_alb_dists['2017-07-21'].iterrows():
	if row.s2_class == 3:
		plt.plot(xvals, row.binned, alpha=0.5, color='#C6DBEF')
dist = uav_alb_dists['2017-07-20'][uav_alb_dists['2017-07-21'].s2_class == 3].binned.mean()
plt.plot(xvals, dist, 'k')
plt.title('21 July')
plt.ylim(0,8.5)
plt.tick_params(axis='x', bottom='off', top='off')

## 07-21 LA
ax = fig.add_subplot(gs[2,1])
for ix, row in uav_alb_dists['2017-07-21'].iterrows():
	if row.s2_class == 4:
		plt.plot(xvals, row.binned, alpha=0.5, color='#FDBB84')
dist = uav_alb_dists['2017-07-20'][uav_alb_dists['2017-07-21'].s2_class == 4].binned.mean()
plt.plot(xvals, dist, 'k')
plt.ylim(0,8.5)
plt.tick_params(axis='x', top='off')

## Changed pixels change in albedo distribution
ax = fig.add_subplot(gs[3,:])

norm = mpl.colors.Normalize(vmin=0.2,vmax=0.6)
# One curve per S2-pixel
for ix,row in uav_alb_change.iterrows():
	row.alb_in_bin[pd.isnull(row.alb_in_bin)] = 0
	alb_colors = row.alb_in_bin
	#alb_colors[alb_colors < -0.5] = -0.5
	#alb_colors[alb_colors >  0.5] =  0.5
	#alb_colors = alb_colors + 0.5
	bins_here = np.where(row.binned > 0, row.binned, np.nan)
	#plt.scatter(np.arange(-100,100,1),row.binned, alpha=0.4, c=cm.YlGnBu_r(row.alb_in_bin), edgecolor='none')
	plt.scatter(np.arange(-1,1,0.01),row.binned, alpha=0.4, c=row.alb_in_bin, cmap='YlGnBu_r', norm=norm,edgecolor='none')
	#(row.alb_in_bin + 1) / 2

plt.plot(np.arange(-1,1,0.01), uav_alb_change.binned.mean(), linewidth=1, color='black')
plt.xlim(-0.2,0.3)
plt.xlabel('Albedo change')
plt.tick_params(axis='x', top='off')

plt.subplots_adjust(bottom=0.19)

# Add colorbar corresponding to albedo scatter colours in above plot
# [left, bottom, width, height] in fractions of figure width and height
ax = fig.add_axes([0.2, 0.09, 0.6, 0.02])
cmap_plot = mpl.cm.YlGnBu_r
cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap_plot,
                                norm=norm,
                                orientation='horizontal')
cb1.set_label('Mean UAV albedo')
cb1.set_ticks(np.arange(0.2,0.7,0.1))

sns.despine()