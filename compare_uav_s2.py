# compare_uav_s2
import statsmodels.api as sm
import matplotlib as mpl
import pandas as pd
import xarray as xr
import numpy as np
import pyproj

from load_uav_data import *
from load_s2_data import *

# Create a categorical colourmap.
categories = ['Unknown', 'Water', 'Snow', 'CI', 'LA', 'HA', 'CC']
vals = [0, 1, 2, 3, 4, 5, 6]
cmap = mpl.colors.ListedColormap(['#000000','#08519C','#FFFFFF', '#C6DBEF', '#FDBB84', '#B30000', '#762A83'])
# Example of colormap use: uav.classified.sel(time='2017-07-23').plot(cmap=cmap, vmin=0, vmax=7)

# Pull-out UAV area from Sentinel-2 data
# Coordinates are taken from min(), max() of x and y dimensions of uav_refl
subset_x = slice(571523.766952,571877.884462)
subset_y = slice(7441194.212972,7440834.747463)
s2_times = ['2017-07-20', '2017-07-21']

subset = s2_data.classified.sel(x=subset_x,	y=subset_y)
albs = s2_data.albedo.sel(x=subset_x, y=subset_y).salem.roi(shape=uav_poly)

# plt.figure()
# subset.plot(col='time')



## Extract sub-pixel characteristics - 'UAV distributions'
uav_dists = {}
uav_dists_perc = {}
for time in s2_times:
	new_store = {}
	
	subsetstack = subset.sel(time=time).salem.roi(shape=uav_poly) \
		.stack(dim=('x','y')) \
		.to_pandas().dropna()
	
	for ix, value in subsetstack.iteritems():
		x,y = ix
		this_pixel = uav_class.Band1.sel(time=time, x=slice(x-10,x+10), y=slice(y-10,y+10))
		values, bins = np.histogram(this_pixel, range=(0,7), bins=7)
		new_store[(x,y)] = values

	uav_px = pd.DataFrame.from_dict(new_store, orient='index', 
		columns=categories)

	uav_px['s2_class'] = subsetstack
	uav_px['s2_class_cat'] = uav_px['s2_class'].astype('category')

	albs_stk = albs.sel(time=time).stack(dim=('x','y')).to_pandas().dropna()
	uav_px['s2_alb'] = albs_stk
	
	uav_dists[time] = uav_px

	# Convert numbers to % of S2 pixel coverage
	tot_px = uav_px.filter(items=categories).sum(axis=1)
	perc_px = uav_px.filter(items=categories).apply(lambda x: (100. /tot_px) * x)
	perc_px['s2_class'] = uav_px['s2_class']
	uav_dists_perc[time] = perc_px



# Look at the distribution of heavy algae within the overall S2 classification
#figure(), sns.boxplot(data=uav_px, x='s2_class', y='HA')

# And the nice simple option that took quite some time to figure out...
#figure(),sns.boxplot(data=uav_px)
#also try sns.boxenplot!

# Budget for sub-S2-pixel make-up for each S2 pixel classification

# Can also look at albedo distributions within this...
# Somehow. Need to think about how the aggregation would work. 




## Look at only pixels which have changed
changes = uav_dists['2017-07-21']['s2_class'] - uav_dists['2017-07-20']['s2_class']
#figure(),sns.boxenplot(data=uav_dists_perc['2017-07-20'][changes == -1]) 
#figure(),sns.boxenplot(data=uav_dists_perc['2017-07-21'][changes == -1])

# What about albedo change? (from narrowband-broadband conversion)
s2_albs = {}
for time in s2_times:
	print(uav_dists[time][changes == -1].s2_alb.describe())
# ~7% albedo increase from 20th to 21st in the S2 pixels which changed class

# At the UAV level, did the albedo of all classes change, or just certain classes?
#figure(),sns.boxplot(data=uav_alb.Band1.sel(time='2017-07-20').salem.roi(shape=uav_poly).stack(dim=('x','y')).to_pandas().dropna()) 


# Did HA and/or LA areas get darker, hypothesis being lightening of adjacent patches due to 
# material transport?
uav_alb.Band1.where(uav_class.Band1 == 5).mean(dim=('x','y')).load() 
# Results: [0.253331, 0.242275, 0.247606, 0.256404, 0.26454 , 0.273798]
# So no, there was actually a very slight albedo increase 20th-->21st.

# Do the same for LA
uav_alb.Band1.where(uav_class.Band1 == 4).mean(dim=('x','y')).load()
# [0.402429, 0.345945, 0.407268, 0.414105, 0.408986, 0.324212]
# Much larger change (5%) than in HA case.
"""
So HA seems to be somewhat more persistent habitat --> perhaps it is so dark
that it absorbs so much SW energy that no WC can develop there, unlike in CI/LA
locations.

Probably assists with the argument that the change observed 20th-21st is due 
to WC growth.
"""

# CI
uav_alb.Band1.where(uav_class.Band1 == 3).mean(dim=('x','y')).load()
# [0.561625, 0.530416, 0.547968, 0.549942, 0.538176, 0.466762]
# No systematic change over the whole area - so shift is in LA only really.
# Perhaps this isn't a surprise? - it's the 'middle' category.


# Something that is a bit puzzling is a small increase in the number of pixels
# tagged as snow on the 21st compared to the 20th - but the CI/snow boundary
# is a bit blurred really.


"""
the fact that the direction of change is only HA->LA indicates that WC processes
almost certainly exert a very important control on albedo
--> can look at coincident albedo changes
--> what is it about the pixels which changed that made them change?
    (e.g. aspect, slope...)

I think that this...
Illustrates the problem with uniquely detecting ice algae: even with a machine
learning approach (rather than just red edge) we can't reliably identify changes
due purely to changes in ice algae population. 

Do we have any other evidence that we can use to assess this?

More interesting questions...
The training dataset does not discrminate between weathering crust presence/
thickness, this is an innate property of the dataset. I suspect that LA 
corresponds to a thinner WC than CI for example. 
But it raises the Q of whether, on the 20th which was an end-member in terms
of ASD-spectra that we were able to acquire, those pixels which have been labelled
as LA were actually clean but were being pushed to 'LA' due to the absence of a WC
and therefore looking at highly anisotropic blue ice, without much/any algae actually
present?

--> the albedo dataset from the UAV is not affected by the classifier and so
can be used to assess these issues independently of the labels.
--> is there any diagnostic for WC thickness that we can invent / should hold 
in theory?

--> what do the beta distributions of albedo per s2 pixel look like?
--> there are ~100 pixels total.
--> is sub-s2-pixel albedo evenly distributed?
	--> and is impact on melt linear?
	--> e.g. do we model a different quantity of meltwater generation when we use granular
	    UAV albedo data versus when we use single S2 value for the pixel?
	    ----> would need to correct/align S2 and UAV albedos as they do not currently match.
	          decide which one is more accurate?
	          probably cannot use field spectra for this?
"""

# test for normality

## Beta distributions
uav_alb_dists = {}
for time in s2_times:
	new_store = {}
	
	subsetstack = albs.sel(time=time) \
		.stack(dim=('x','y')) \
		.to_pandas().dropna()
	
	for ix, value in subsetstack.iteritems():
		x,y = ix
		this_pixel = uav_alb.Band1.sel(time=time, x=slice(x-10,x+10), y=slice(y-10,y+10)) \
			.stack(dim=('x','y')).to_pandas()

		px_alb = this_pixel.mean()
		kurtosis = this_pixel.kurtosis()
		skewness = this_pixel.skew()

		# jb,jbpv,skew,kurtosis = sm.stats.stattools.jarque_bera(this_pixel)
		# new_store[(x,y)] = dict(jb=jb, jbpv=jbpv)
		values, bins = np.histogram(this_pixel, range=(0,1), bins=100)
		values = 100 / np.sum(values) * values
		new_store[(x,y)] = dict(binned=values, uav_alb=px_alb, kurtosis=kurtosis, skewness=skewness)

	uav_px = pd.DataFrame.from_dict(new_store, orient='index')

	uav_alb_dists[time] = uav_px

uav_alb_dists['2017-07-20']['s2_alb'] = albs.sel(time='2017-07-20').stack(dim=('x','y')).to_pandas().dropna()	
uav_alb_dists['2017-07-21']['s2_alb'] = albs.sel(time='2017-07-21').stack(dim=('x','y')).to_pandas().dropna()	

# Check degree of fit between UAV and S2 pixel albedos
# plt.figure()
# ax = plt.subplot(111)
# uav_alb_dists['2017-07-20'].plot(kind='scatter',y='uav_alb',x='s2_alb',marker='o',ax=ax)
# uav_alb_dists['2017-07-21'].plot(kind='scatter',y='uav_alb',x='s2_alb',marker='o',ax=ax)
# plt.plot((0,1),(0,1)) 

import statsmodels.api as sm
check_pd = pd.concat([ uav_alb_dists['2017-07-20'].filter(items=['s2_alb', 'uav_alb']), 
	uav_alb_dists['2017-07-20'].filter(items=['s2_alb', 'uav_alb']) ], axis=0)
X = check_pd.s2_alb
X = sm.add_constant(X)
y = check_pd.uav_alb
model = sm.OLS(y,X)
fit = model.fit()
#print(fit.summary())

xx = np.arange(0.15, 0.60, 0.1)
yy = fit.params.s2_alb * xx + fit.params.const
#plt.plot(xx,yy, '--')

# for comparison purposes, add fit.params.const to uav_alb in order to up-adjust to 'match' s2.

#g = sns.FacetGrid(uav_alb_dists['2017-07-20'], row="coordinate", aspect=15, height=.5)
# !TO-DO! Think more about this tomorrow.

# def myfunc(data,color):
# 	print(data.values)
# 	plt.plot(np.arange(0,100,1), data.values[0])
# 	plt.title('')

# g.map(myfunc, 'binned')

uav_alb_dists['2017-07-20']['s2_class'] = uav_dists_perc['2017-07-20'].s2_class 
uav_alb_dists['2017-07-21']['s2_class'] = uav_dists_perc['2017-07-21'].s2_class 
uav_alb_dists['2017-07-20']['changes'] = changes
uav_alb_dists['2017-07-21']['changes'] = changes
# plt.figure()
# ax = plt.subplot(111)
# for ix, row in uav_alb_dists['2017-07-21'].iterrows():
# 	#if row.s2_class == 3:
# 	if row.changes == -1:
# 		#plt.plot(np.arange(0,100,1), row.binned, alpha=0.5)
# 		this_px_diff = row.binned - uav_alb_dists['2017-07-20'].loc[ix].binned
# 		plt.plot(np.arange(0,100,1), this_px_diff, alpha=0.5)
# plt.ylabel('% coverage of S2 pixel')
# #plot(np.arange(0,100,1),uav_alb_dists['2017-07-21'][uav_alb_dists['2017-07-21']['s2_class'] == 3].binned.mean(),linewidth=3,alpha=1,color='black')
# plt.ylim(0,7)

# Look at all data regardless of change or not:
# plt.figure()
# ax = plt.subplot(111)
# for ix, row in uav_alb_dists['2017-07-21'].iterrows():
# 	plt.plot(np.arange(0,100,1), row.binned, alpha=0.5)


uav_alb_dists_c = pd.concat(uav_alb_dists) 
#figure(),uav_alb_dists_c.plot(kind='scatter',x='uav_alb',y='kurtosis') 

uav_alb_dists_c['uav_alb_bin'] = pd.cut(uav_alb_dists_c.uav_alb,np.arange(0,1,0.01))
binned_dists = uav_alb_dists_c.binned.groupby(uav_alb_dists_c.uav_alb_bin).apply(np.mean)
binned_dists.index = np.arange(0,0.99,0.01)

# plt.figure()
# for ix, row in binned_dists.iteritems():
# 	if type(row) is np.ndarray:
# 		plt.plot(np.arange(0,1,0.01), row)
# Apply to analysis above to just the changed pixels - look at distribution change



### Bin the UAV pixel-by-pixel changes
new_store = {}	
for ix, value in changes.iteritems():
	if value == -1:
		x,y = ix
		this_pixel21 = uav_alb.Band1.sel(time='2017-07-21', x=slice(x-10,x+10), y=slice(y-10,y+10)) \
			.stack(dim=('x','y')).to_pandas()
		this_pixel20 = uav_alb.Band1.sel(time='2017-07-20', x=slice(x-10,x+10), y=slice(y-10,y+10)) \
			.stack(dim=('x','y')).to_pandas()
		this_pixel_change = this_pixel21 - this_pixel20

		values, bins = np.histogram(this_pixel_change, range=(-1,1), bins=200)
		values = 100 / np.sum(values) * values
		# I want the albedo which corresponds to the bin...
		# Its a group-by operation
		combo = pd.concat({'alb21':this_pixel21, 'change':this_pixel_change}, axis=1)
		combo['change_binned'] = pd.cut(combo['change'],np.arange(-1,1.01,0.01))
		binalbs = combo.alb21.groupby(combo.change_binned).mean()
		binalbs.index = np.arange(-1,1.,0.01)
		
		new_store[(x,y)] = dict(binned=values, alb_in_bin=binalbs.values)

uav_alb_change = pd.DataFrame.from_dict(new_store, orient='index')

# plt.figure()
# ax = plt.subplot(111)
# for ix,row in uav_alb_change.iterrows():
# 	#plt.plot(np.arange(-100,100,1),row.binned, alpha=0.6)
# 	row.alb_in_bin[pd.isnull(row.alb_in_bin)] = 0
# 	alb_colors = row.alb_in_bin
# 	alb_colors[alb_colors < -0.5] = -0.5
# 	alb_colors[alb_colors >  0.5] =  0.5
# 	alb_colors = alb_colors + 0.5
# 	plt.scatter(np.arange(-100,100,1),row.binned, alpha=0.6, c=cm.YlGnBu_r(row.alb_in_bin), edgecolor='none')
# 	#(row.alb_in_bin + 1) / 2
# plt.plot(np.arange(-100,100,1), uav_alb_change.binned.mean(), linewidth=3, color='black')

uav_alb_c_mean = pd.Series(uav_alb_change.binned.mean(),index=np.arange(-100,100,1))
uav_alb_c_mean.loc[-100:-1].sum()

# Those UAV pixels which got darker - what class were they/did they change class?
# - i.e were they algae-laden?

"""
within the bounded area - shpf variable

for each sentinel pixel - enumerate number of pixels of each class from UAV imagery

sentinel xarray coordinates are for middle of each box.
so can s

consider t-tests

"""

"""
* classify sentinel 2 images
* could also compare albedos afterwards as well
* look at sub-pixel albedo distribution
	beta distribution??

"""


#####
# S2 - MODIS intercomparison
#####


# Convert MODIS coordinates
modis_x = -190651
modis_y = -2507935
modis_proj = pyproj.Proj('+init=epsg:3413')
s2_proj = pyproj.Proj('+init=epsg:32622')
modis_lon, modis_lat = modis_proj(modis_x, modis_y, inverse=True)
modis_x_utm, modis_y_utm = s2_proj(modis_lon, modis_lat)
modis_px_x = slice(modis_x_utm-250, modis_x_utm+250)
modis_px_y = slice(modis_y_utm+250, modis_y_utm-250)
s2alb_in_modis = s2_data.albedo.sel(x=modis_px_x, y=modis_px_y)
s2cla_in_modis = s2_data.classified.sel(x=modis_px_x, y=modis_px_y)

# figure()
# ax = plt.subplot(111)
# s2cla_in_modis.sel(time='2017-07-21').plot(ax=ax)

x,y = uav_poly.iloc[0].geometry.exterior.xy
upx,upy = s2_proj(x,y)
mdx,mdy = modis_proj(x,y)
# plot(upx, upy)


s2_in_modis = s2_data.albedo.salem.roi(shape='/scratch/UAV/coincident_s6_modis_latlon.shp')
#s2alb_in_modis.mean(dim=('x','y')).load()
s2_in_modis_mean = s2_in_modis.mean(dim=('x','y'))
s2_in_modis_mean.to_pandas().to_csv('/home/at15963/projects/uav/outputs/s2_alb_modispx.csv')

s2_alb = s2_data.albedo.salem.roi(shape='/scratch/UAV/uav_2017_area.shp').mean(dim=('x','y'))
#s2_alb.to_pandas().to_csv('/home/at15963/projects/uav/outputs/s2_alb_uavpx.csv')
# Result: array([0.394256, 0.45744 ])
# Sentinel clearly shows a pretty major area-averaged albedo increase over the MODIS pixel extent.
# What time periods of the day are we covering / is there a problem with some atmospheric correction somewhere?


## b01 refl
mod09 = xr.open_dataset('/scratch/MOD09GA.006.FB/MOD09GA.2017.006.epsg3413_b1234q.nc')
mod09b01 = mod09.sur_refl_b01_1.sel(X=modis_x, Y=modis_y, method='nearest')


# Check Sentinel 2 red band reflectance
fn_path = '/home/at15963/projects/uav/data/S2/'
im_path = 'S2B_MSIL2A_20170721T151909_N0205_R068_T22WEV_20170721T152003.SAFE_20m/S2B_MSIL2A_20170721T151909_N0205_R068_T22WEV_20170721T152003_20m.data/'
s2_red = xr.open_rasterio(fn_path+im_path+'B4.img', chunks={'x':1000, 'y':1000})

