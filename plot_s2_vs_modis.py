"""

S2 versus MODIS

"""

import matplotlib.pyplot as plt
import seaborn as sns

from load_s2_data import *
from load_uav_data import *


sns.set_context('paper')
sns.set_style('ticks')

# Load data from across both the intersecting MODIS pixels
s2_in_modis = s2_data.albedo.salem.roi(shape='/scratch/UAV/coincident_s6_modis_latlon.shp')


s2_in_modis.mean(dim=('x','y')).load()

fig = plt.figure(figsize=(4,2))

ax = plt.subplot(121)
bins, albs, x = s2_in_modis.sel(time='2017-07-20').plot.hist(bins=50,range=(0,1), ax=ax, 
	color='black')
plt.ylim(0,350)
plt.xlim(0.2, 0.6)
plt.title('20 July')
plt.ylabel('No. S2 pixels')
plt.xlabel('Albedo')
ax.spines['left'].set_position(('outward', 10))
ax.annotate('(a)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

ax2 = plt.subplot(122)
s2_in_modis.sel(time='2017-07-21').plot.hist(bins=50,range=(0,1), ax=ax2, 
	color='black')
plt.ylim(0,350)
plt.xlim(0.2, 0.6)
plt.title('21 July')
plt.xlabel('Albedo')
plt.yticks([])
ax2.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.03,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

sns.despine()

ax2.spines['left'].set_visible(False)
plt.tick_params(axis='y', left=False)

plt.tight_layout()

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission1/figures/s6_modis_albedo_dist.pdf', dpi=300)


## Sub-MODIS coverage stats
s2_in_modis

modis_px = salem.read_shapefile('/scratch/UAV/coincident_s6_modis_latlon.shp')
for px in [0,1]:
	print(modis_px.loc[px].geometry)
	px_data = s2_data.classified.salem.roi(geometry=modis_px.loc[px].geometry, crs=modis_px.crs) 
	for t in px1.time:
		counts = px_data.sel(time=t).groupby(px_data.sel(time=t)).count().load()
		percs = 100 / counts.sum() * counts
		print(t, percs)




## Associated melting statistics


counts_20, bins = np.histogram(s2_in_modis.sel(time='2017-07-20').values, bins=100, range=(0,1))
# print('Dist 20th: ', compute_avg_melt(counts))
counts_21, bins = np.histogram(s2_in_modis.sel(time='2017-07-21').values, bins=100, range=(0,1))

# 20 July
melt_amts = []
k = 0
for v in np.arange(0,1,0.01):
	for c in np.arange(0,counts_20[k]):
#		melt_amts.append(total_melt_rates.loc[v] * 0.0001 * 20**2) 
		melt_amts.append(melt_rates['SWR_melt'].loc[v] * 0.0001 * 20**2) 
	k += 1
np.sum(melt_amts)

melt_rates['SWR_melt'].loc[0.38] * 0.0001 * 20**2 * 1078

total_melt_rates.loc[0.38] * 0.0001 * 20**2 * 1078


# 21 July
melt_amts = []
k = 0
for v in np.arange(0,1,0.01):
	for c in np.arange(0,counts_21[k]):
#		melt_amts.append(total_melt_rates.loc[v] * 0.0001 * 20**2) 
		melt_amts.append(melt_rates['SWR_melt'].loc[v] * 0.0001 * 20**2) 
	k += 1
np.sum(melt_amts)

melt_rates['SWR_melt'].loc[0.44] * 0.0001 * 20**2 * 1078

total_melt_rates.loc[0.44] * 0.0001 * 20**2 * 1078