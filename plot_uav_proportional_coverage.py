"""

Proportional coverage of each class per UAV acquisition

"""

import matplotlib.pyplot as plt 
import seaborn as sns



from load_uav_data import *

uav_class_common = uav_class.classified.salem.roi(shape=uav_poly, other=-999)

store = {}
for time in uav_class_common.time: # ['2017-07-20', '2017-07-21']:
	data_here = uav_class_common.sel(time=time)
	nulls = data_here.isnull().sum().load()
	class_counts = data_here \
		.groupby(data_here).count().load().to_pandas()
	class_counts.loc[0] += int(nulls.values)
	store[time.values] = class_counts


classed = pd.DataFrame.from_dict(store, orient='index')
classed = classed.drop(columns=-999)
classed = classed.rename({0:'Unknown', 1:'Water', 2:'Snow', 3:'CI', 4:'LA', 5:'HA', 6:'CC'}, axis='columns')
classed_perc = 100 / 16871728 * classed
classed_perc = classed_perc.drop(columns=['Unknown'])

sns.set_context('paper')
sns.set_style("ticks")

plt.figure(figsize=(4,2.5))
ax = plt.subplot()
colors = ['darkblue', '#B9B9B9', '#C6DBEF', '#FDBB84', '#B30000', '#762A83']
with sns.color_palette(colors):
	ax = classed_perc.plot(kind='bar',stacked=True, legend=False, ax=ax)

plt.ylabel('% coverage')

xticks, _ = plt.xticks()
plt.xticks(xticks, ['15 Jul', '20 Jul', '21 Jul', '22 Jul', '23 Jul', '24 Jul'])
ax.tick_params(axis='x', labelrotation=0)

plt.legend(loc=(1,0.45), frameon=False)

plt.axvline(xticks[1] - float(xticks[1]-xticks[0])/2, linestyle='--', color='grey', linewidth=0.5)


sns.despine()

plt.tight_layout()

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission1/figures/s6_uav_proportional_coverage_all_clf20190130_171930.png', dpi=300)