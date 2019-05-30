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
		this_pixel = uav_class.classified.sel(time=time, x=slice(x-10,x+10), y=slice(y-10,y+10))
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


## Look at only pixels which have changed
changes = uav_dists['2017-07-21']['s2_class'] - uav_dists['2017-07-20']['s2_class']

# What about albedo change? (from narrowband-broadband conversion)
s2_albs = {}
for time in s2_times:
	print(uav_dists[time][changes == -1].s2_alb.describe())
# ~7% albedo increase from 20th to 21st in the S2 pixels which changed class


# Did HA and/or LA areas get darker, hypothesis being lightening of adjacent patches due to 
# material transport?
uav_class.albedo.where(uav_class.classified == 5).mean(dim=('x','y')).load() 
# Results: [0.253331, 0.242275, 0.247606, 0.256404, 0.26454 , 0.273798]
# So no, there was actually a very slight albedo increase 20th-->21st.

# Do the same for LA
uav_class.albedo.where(uav_class.classified == 4).mean(dim=('x','y')).load()
# [0.402429, 0.345945, 0.407268, 0.414105, 0.408986, 0.324212]


# CI
uav_class.albedo.where(uav_class.classified == 3).mean(dim=('x','y')).load()
# [0.561625, 0.530416, 0.547968, 0.549942, 0.538176, 0.466762]

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
		this_pixel = uav_class.albedo.sel(time=time, x=slice(x-10,x+10), y=slice(y-10,y+10)) \
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


uav_alb_dists['2017-07-20']['s2_class'] = uav_dists_perc['2017-07-20'].s2_class 
uav_alb_dists['2017-07-21']['s2_class'] = uav_dists_perc['2017-07-21'].s2_class 
uav_alb_dists['2017-07-20']['changes'] = changes
uav_alb_dists['2017-07-21']['changes'] = changes

uav_alb_dists_c = pd.concat(uav_alb_dists) 

uav_alb_dists_c['uav_alb_bin'] = pd.cut(uav_alb_dists_c.uav_alb,np.arange(0,1.,0.01), right=False)
binned_dists = uav_alb_dists_c.binned.groupby(uav_alb_dists_c.uav_alb_bin).apply(np.mean)
binned_dists.index = np.arange(0,1,0.01)[:-1]


### Bin the UAV pixel-by-pixel changes
new_store = {}	
for ix, value in changes.iteritems():
	if value == -1:
		x,y = ix
		this_pixel21 = uav_class.albedo.sel(time='2017-07-21', x=slice(x-10,x+10), y=slice(y-10,y+10)) \
			.stack(dim=('x','y')).to_pandas()
		
		if len(this_pixel21[this_pixel21 >= 0]) < 160000:
			print('small, skipping')
			continue

		this_pixel20 = uav_class.albedo.sel(time='2017-07-20', x=slice(x-10,x+10), y=slice(y-10,y+10)) \
			.stack(dim=('x','y')).to_pandas()  #.salem.roi(shape=uav_poly)
		this_pixel_change = this_pixel21 - this_pixel20

		values, bins = np.histogram(this_pixel_change, range=(-1,1), bins=200)
		values = 100 / 160400 * values
		# I want the albedo which corresponds to the bin...
		# Its a group-by operation
		combo = pd.concat({'alb21':this_pixel21, 'change':this_pixel_change}, axis=1)
		combo['change_binned'] = pd.cut(combo['change'],np.arange(-1,1.,0.01))
		binalbs = combo.alb21.groupby(combo.change_binned).mean()
		binalbs.index = np.arange(-1,1.,0.01)[:-1]
		
		new_store[(x,y)] = dict(binned=values, alb_in_bin=binalbs.values)

uav_alb_change = pd.DataFrame.from_dict(new_store, orient='index')


uav_alb_c_mean = pd.Series(uav_alb_change.binned.mean(),index=np.arange(-100,100,1))
uav_alb_c_mean.loc[-100:-1].sum()


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

x,y = uav_poly.iloc[0].geometry.exterior.xy
upx,upy = s2_proj(x,y)
mdx,mdy = modis_proj(x,y)

s2_in_modis = s2_data.albedo.salem.roi(shape='/scratch/UAV/coincident_s6_modis_latlon.shp')
s2_in_modis_mean = s2_in_modis.mean(dim=('x','y'))
s2_in_modis_mean.to_pandas().to_csv('/home/at15963/projects/uav/outputs/s2_alb_modispx.csv')

s2_alb = s2_data.albedo.salem.roi(shape='/scratch/UAV/uav_2017_area.shp').mean(dim=('x','y'))
