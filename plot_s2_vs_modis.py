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
s2_in_modis.sel(time='2017-07-20').plot.hist(bins=50,range=(0,1), ax=ax, 
	color='black')
plt.ylim(0,350)
plt.xlim(0.2, 0.6)
plt.title('20 July')
plt.ylabel('No. S2 pixels')
plt.xlabel('Albedo')
ax.spines['left'].set_position(('outward', 10))

ax2 = plt.subplot(122)
s2_in_modis.sel(time='2017-07-21').plot.hist(bins=50,range=(0,1), ax=ax2, 
	color='black')
plt.ylim(0,350)
plt.xlim(0.2, 0.6)
plt.title('21 July')
plt.xlabel('Albedo')
plt.yticks([])

sns.despine()

ax2.spines['left'].set_visible(False)
plt.tick_params(axis='y', left=False)

plt.tight_layout()