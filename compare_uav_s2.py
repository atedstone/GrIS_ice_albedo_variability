# compare_uav_s2

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

plt.figure()
subset.plot(col='time')



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
figure(), sns.boxplot(data=uav_px, x='s2_class', y='HA')

# And the nice simple option that took quite some time to figure out...
figure(),sns.boxplot(data=uav_px)
#also try sns.boxenplot!

# Budget for sub-S2-pixel make-up for each S2 pixel classification

# Can also look at albedo distributions within this...
# Somehow. Need to think about how the aggregation would work. 




## Look at only pixels which have changed
changes = uav_dists['2017-07-21']['s2_class'] - uav_dists['2017-07-20']['s2_class']
figure(),sns.boxenplot(data=uav_dists_perc['2017-07-20'][changes == -1]) 
figure(),sns.boxenplot(data=uav_dists_perc['2017-07-21'][changes == -1])

# What about albedo change? (from narrowband-broadband conversion)
s2_albs = {}
for time in s2_times:
	print(uav_dists[time][changes == -1].s2_alb.describe())
# ~7% albedo increase from 20th to 21st in the S2 pixels which changed class

# At the UAV level, did the albedo of all classes change, or just certain classes?
figure(),sns.boxplot(data=uav_alb.Band1.sel(time='2017-07-20').salem.roi(shape=uav_poly).stack(dim=('x','y')).to_pandas().dropna()) 


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
"""


## Beta distributions
uav_alb_dists = {}
for time in s2_times:
	new_store = {}
	
	subsetstack = albs.sel(time=time) \
		.stack(dim=('x','y')) \
		.to_pandas().dropna()
	
	for ix, value in subsetstack.iteritems():
		x,y = ix
		this_pixel = uav_alb.Band1.sel(time=time, x=slice(x-10,x+10), y=slice(y-10,y+10))
		values, bins = np.histogram(this_pixel, range=(0,1), bins=100)
		values = 100 / np.sum(values) * values
		new_store[(x,y)] = values

	uav_px = pd.DataFrame.from_dict(new_store, orient='index')

	uav_alb_dists[time] = uav_px

g = sns.FacetGrid(uav_alb_dists['2017-07-20'], row="coordinate", aspect=15, height=.5)
# !TO-DO! Think more about this tomorrow.



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
