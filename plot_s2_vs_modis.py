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


## Associated melting statistics

# from run_ebmodel_albedos import *

# # I'm not convinced that this function is mathematically correct - is it doing what I think?
# def compute_avg_melt(counts):
# 	return (( (total_melt_rates*24) * counts) / np.sum(counts)).sum()

counts_20, bins = np.histogram(s2_in_modis.sel(time='2017-07-20').values, bins=100, range=(0,1))
# print('Dist 20th: ', compute_avg_melt(counts))
counts_21, bins = np.histogram(s2_in_modis.sel(time='2017-07-21').values, bins=100, range=(0,1))
# print('Dist 21st: ',compute_avg_melt(counts))

# # Average S2 albedo within MODIS pixels
# print('S2 20th: ', total_melt_rates.loc[0.38] * 24)
# print('S2 21st: ', total_melt_rates.loc[0.44] * 24)

# # MODIS pixels albedo means
# print('MODIS 20th: ', total_melt_rates.loc[0.39] * 24)
# print('MODIS 21st: ',total_melt_rates.loc[0.38] * 24)

# # Convert to volume?
# ((total_melt_rates*24 * 20**2 * counts) / 1000).sum()

# #        hourly->total  mm-->m      to S2 pixel area   = m3 of melt
# ( (total_melt_rates*24*0.001) * (counts * 20**2)).sum()

# # could compare against a normal distribution...

# # or could express as melt potential (a bit like Stefan)

# """
# Problem with this at the moment is that I'm using an instantaneous EB_AUTO 
# derived value from midday to make estimates about 24 h melting. 

# could use a 24-h average of SWD instead?

# Or even use the approach that Joe used in his paper currently in review?

# Could try relative melt rates as per Moustafa et al 2015
# """


# ## Relative melt rates c.f. Moustafa et al. (2015)

# def estimate_melt(al, swd=400):
# 	er = swd * (1 - al)
# 	M = er * (3.34e5 * 1000)**-1
# 	return M

# simple_melt = [estimate_melt(al) for al in np.arange(0,1,0.01)]
# simple_melt = pd.Series(simple_melt, np.arange(0,1,0.01))

# def estimate_melt_distribution(counts):
# 	melt_rates = []
# 	k = 0
# 	for v in np.arange(0,1,0.01):
# 		for c in np.arange(0,counts[k]):
# 			melt_rates.append(simple_melt.loc[v]) 
# 		k += 1
# 	return np.mean(melt_rates)

# print('20 July:')
# avg = estimate_melt(0.38)
# print('Average:', avg)
# dist = estimate_melt_distribution(counts_20)
# print('From dist.:', dist)
# print('%:', 100 / avg * dist)

# print('21 July:')
# avg = estimate_melt(0.44)
# print('Average:', avg)
# dist = estimate_melt_distribution(counts_21)
# print('From dist.:', dist)
# print('%:', 100 / avg * dist)

# """
# I want to do this in terms of volume in order to access the spatial part of 
# the problem, rather than just ultimately still computing an average melt rate
# for across the area

# The Moustafa method is 'instantaneous' and this thus is not applicable to
# calculation of volumes. As soon as volumes are considered, time also has to
# be considered, which means taking into account the SWD cycle.

# Could compute a generalised cycle, say for 20-24 July. 

# But then the albedo changes as a function of the solar angle so this isn't possible either...
# """

# # Just for one hour...



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