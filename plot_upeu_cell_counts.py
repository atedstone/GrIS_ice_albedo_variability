import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec

sns.set_context('paper', rc={"font.size":8,"axes.titlesize":8,"axes.labelsize":8,"legend.fontsize":8})
sns.set_style('ticks')

cells = pd.read_csv('~/Dropbox/paper_uavts_materials/upe_u_cell_counts.csv')

values, edges = np.histogram(cells['cells.per.ml'], range=(0,60000), bins=np.logspace(np.log10(0.1),np.log10(60000),60))
values_perc = 100 / 75 * values

plt.figure(figsize=(4,3.8))

gs = gridspec.GridSpec(4, 1)
ax = plt.subplot(gs[1:,0], xscale='log')
bar_widths = np.diff(edges) - (np.diff(edges)*0.2)
ax.bar(edges[0:-1], values_perc, width=bar_widths, color='black')
plt.ylabel('% of samples')
plt.xlim(40, 65000)
plt.xlabel('Number of cells (ml$^{-1}$)')

plt.annotate('n = 75', xy=(0.8,0.8), xycoords='axes fraction', fontstyle='italic', verticalalignment='center', fontsize=8)


ax_classes = plt.subplot(gs[0,0], xscale='log')

# JC paper classes
plt.axvspan(625-381, 625+381, ymin=0, ymax=0.4, color='#4292C6')
plt.annotate('23%', xy=(580,0.2), xycoords='data', horizontalalignment='right', verticalalignment='center', color='white', fontsize=8, fontweight='bold')
plt.axvspan(4.73e3-2.57e3, 4.73e3+2.57e3, ymin=0, ymax=0.4, color='#FDBB84')
plt.annotate('19%', xy=(4.93e3,0.2), xycoords='data', horizontalalignment='right', verticalalignment='center', color='white', fontsize=8, fontweight='bold')
plt.axvspan(2.9e4-2.01e4, 2.9e4+2.01e4, ymin=0, ymax=0.4, color='#B30000')
plt.annotate('29%', xy=(2.7e4,0.2), xycoords='data', horizontalalignment='right', verticalalignment='center', color='white', fontsize=8, fontweight='bold')


# Alternative boxing
plt.axvspan(40, 625, ymin=0.6, ymax=1, color='#4292C6')
plt.annotate('20%', xy=(150,0.8), xycoords='data', verticalalignment='center', color='white', fontsize=8, fontweight='bold')
plt.axvspan(626, 2.9e4, ymin=0.6, ymax=1, color='#FDBB84')
plt.annotate('72%', xy=(4500,0.8), xycoords='data', verticalalignment='center', color='white', fontsize=8, fontweight='bold')
plt.axvspan(2.9e4, 650000, ymin=0.6, ymax=1, color='#B30000')
plt.annotate('8%', xy=(37000,0.8), xycoords='data', verticalalignment='center', color='white', fontsize=8, fontweight='bold')


plt.annotate('Bounds', xy=(14,0.8), xycoords='data', verticalalignment='center', fontsize=8, annotation_clip=False)
plt.annotate(r'$\bar{X}\pm1\sigma$', xy=(14,0.2), xycoords='data', verticalalignment='center', fontsize=8, annotation_clip=False)

sns.despine()

plt.tick_params(axis='x', bottom=False, top=False)
plt.tick_params(axis='y', left=False)
ax_classes.spines['left'].set_visible(False)
ax_classes.spines['bottom'].set_visible(False)
plt.xlim(40, 65000)
plt.xticks([])
plt.yticks([])
plt.minorticks_off()

plt.tight_layout(rect=[0.06,0,1,1])

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission1/figures/upe_cell_counts.pdf')



