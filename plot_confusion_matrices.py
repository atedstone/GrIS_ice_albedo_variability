# Confusion matrices

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_context('paper', rc={"font.size":8,"axes.titlesize":8,"axes.labelsize":8,"legend.fontsize":8,
  "xtick.labelsize":8, "ytick.labelsize":8})
sns.set_style('ticks')


## UAV
conf_uav = np.array([[12,0,0,0,0,0,0],
 [ 0,6,0,0,1,0,0],
 [ 0,0,20,1,0,0,0],
 [ 0,0,3,14,0,0,0],
 [ 0,0,0,0,26,0,0],
 [ 0,0,0,0,1,80,0],
 [ 0,0,0,0,0,0,10]])

conf_n_uav = np.array([[0.,0.,0.,0.,0.,0.,0.],
 [0.,0.,0.,0.,0.14285714,0.,0.],
 [0.,0.,0.,0.04761905,0.,0.,0.],
 [0.,0.,0.17647059,0.,0.,0.,0.],
 [0.,0.,0.,0.,0.,0.,0.],
 [0.,0.,0.,0.,0.01234568,0.,0.],
 [0.,0.,0.,0.,0.,0.,0.]])


## Sentinel 2
conf_s2 = np.array([[ 4,0,0,0,0,0,0],
 [ 0,0,0,0,1,0,0],
 [ 0,0,8,4,0,0,0],
 [ 0,0,0,4,0,0,0],
 [ 0,0,0,0,13,2,0],
 [ 0,0,0,0,0,33,0],
 [ 1,0,0,0,0,1,4]])

conf_n_s2 = np.array([[0.,0.,0.,0.,0.,0.,0.        ],
 [0.,0.,0.,0.,1.,0.,0.        ],
 [0.,0.,0.,0.33333333,0.,0., 0.        ],
 [0.,0.,0.,0.,0.,0.,0.        ],
 [0.,0.,0.,0.,0.,0.13333333, 0.        ],
 [0.,0.,0.,0.,0.,0.,0.        ],
 [0.16666667, 0.,0.,0.,0.,0.16666667,0.        ]])

labels = ['UN', 'WA', 'SN', 'CI', 'LA', 'HA', 'CC']

conf_uav_pd = pd.DataFrame(conf_uav, index=labels, columns=labels)
conf_n_uav_pd = pd.DataFrame(conf_n_uav, index=labels, columns=labels)
conf_s2_pd = pd.DataFrame(conf_s2, index=labels, columns=labels)
conf_n_s2_pd = pd.DataFrame(conf_n_s2, index=labels, columns=labels)

plt.figure(figsize=(4,3.8))

pal = sns.color_palette("Blues") #sns.cubehelix_palette(8, start=.5, rot=-.75)

ax1 = plt.subplot(2,2,1)
sns.heatmap(conf_uav_pd, ax=ax1, cmap=pal, vmax=20, square=True, cbar_kws={'shrink':0.6})
ax1.annotate('(a)', fontsize=8, fontweight='bold', xy=(0.02,1.15), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

plt.ylabel('UAS')
plt.title('Un-normalised')


ax2 = plt.subplot(2,2,2)
sns.heatmap(conf_n_uav_pd, ax=ax2, cmap=pal, vmin=0, vmax=1, square=True, cbar_kws={'shrink':0.6})
ax2.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.02,1.15), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')
plt.title('Normalised')

ax3 = plt.subplot(2,2,3)
sns.heatmap(conf_s2_pd, ax=ax3, cmap=pal, vmax=20, square=True, cbar_kws={'shrink':0.6})
ax3.annotate('(c)', fontsize=8, fontweight='bold', xy=(0.02,1.15), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

plt.ylabel('Sentinel-2')

ax4 = plt.subplot(2,2,4)
sns.heatmap(conf_n_s2_pd, ax=ax4, cmap=pal, vmin=0, vmax=1, square=True, cbar_kws={'shrink':0.6})
ax4.annotate('(d)', fontsize=8, fontweight='bold', xy=(0.02,1.15), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

plt.tight_layout()
plt.subplots_adjust(wspace=0.34, hspace=0.20)
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission1/figures/confusion_matrices_clf20190130_171930_S2clf20190305_170648.pdf', dpi=300)