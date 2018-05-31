"""
Compare ground-based reflectance measurements with RedEdge reflectance mosaics.

Calculate empirical correction coefficients for each RedEdge band.

Hard-coded for 2017 field season (ungeneralised).

Author : Andrew Tedstone (a.j.tedstone@bristol.ac.uk)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import numpy as np
import pyproj
from scipy.stats import spearmanr

import georaster
import xarray_classify

# windows: 3 = 15cm, 5=25cm, 7=35 cm
uav_window = 5
cull_sd = 0.05

# Load biological (destructive) sample locations CSV file.
samples = pd.read_csv('/home/at15963/Dropbox/work/data/field_processed_2017/uav_sb_locations.csv')

# Load ground reflectance spectra in bands corresponding to red-edge sensor
rededge = pd.read_excel('/home/at15963/Dropbox/work/black_and_bloom/multispectral-sensors-comparison.xlsx',
	sheet_name='RedEdge')
wvl_centers = rededge.central
wvls = pd.DataFrame({'low':rededge.start, 'high':rededge.end})
HCRF_file = '/scratch/field_spectra/HCRF_master.csv'
spectra = xarray_classify.load_hcrf_data(HCRF_file, wvls)

# Flights to iterate through
flights = {
'20170715':'uav_20170715_refl_5cm_commongrid.tif',
'20170720':'uav_20170720_refl_5cm_commongrid.tif',
'20170721':'uav_20170721_refl_5cm_commongrid.tif',
'20170722':'uav_20170722_refl_5cm_commongrid.tif',
'20170723':'uav_20170723_refl_5cm_commongrid.tif',
'20170724':'uav_20170724_refl_5cm_commongrid.tif'
}

store = {}

## Get destructive sites
for ix, sampl in samples.iterrows():

	if pd.notnull(sampl.spec_id):
		px = sampl.sample_x
		py = sampl.sample_y

		d = sampl.date
		dstr = str(d)

		im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/%s' %flights[dstr],
			load_data=False)

		val, wins = im.value_at_coords(px, py, window=uav_window, 
			return_window=True, reducer_function=np.nanmedian)

		im = None

		# Calculate standard deviation of window
		stds = {}
		for n in np.arange(1,6):
			stds['%s_std' %n] = np.std(wins[n])

		# Add st.devs to values to save
		val = {**val, **stds}
		# Save to store
		store[sampl.spec_id] = val


## Get temporal sites

# First convert site coordinates to UTM (only for the temporal sites, numbered 1:5)
all_gcps = pd.read_csv('/home/at15963/Dropbox/work/data/field_processed_2017/pixel_gcps_kely_formatted.csv', index_col=0)
temporal_gcps = {}
utm = pyproj.Proj('+init=epsg:32623')
for	n in np.arange(1,6):
	gcp = all_gcps.loc['GCP%s' %n]
	utmx, utmy = utm(gcp.lon, gcp.lat)
	# Approximately identify the reflectance measurement center - move towards camp
	utmx += 0.4
	utmy -= 0.4
	temporal_gcps[n] = {'x':utmx, 'y':utmy}
temporal_gcps = pd.DataFrame(temporal_gcps).T

# Now pull out values from each flight
for flight in flights:

	im = georaster.MultiBandRaster('/scratch/UAV/uav2017_commongrid_bandcorrect/%s' %flights[flight],
		load_data=False)

	for ix, gcp in temporal_gcps.iterrows():
		val, wins = im.value_at_coords(gcp.x, gcp.y, window=uav_window, 
			return_window=True, reducer_function=np.nanmedian)

		# Standard deviation in each band
		stds = {}
		for n in np.arange(1,6):
			stds['%s_std' %n] = np.std(wins[n])
		val = {**val, **stds}

		spec_id = flight[-2:] + '_7_S' + str(ix)
		store[spec_id] = val

	im = None


## Combine ASD and UAV datasets

# Convert store to a DataFrame
uav_refl = pd.DataFrame(store).T

# Join UAV reflectance with ASD reflectance
joined = uav_refl.join(spectra)
# Drop rows for which no data (this is because values pulled out for all UAV 
# flights, but temporal ground measurements not always taken)
joined = joined.dropna()
# GeoRaster returns dicts of band numbers - convert them to wavelengths
joined = joined.rename({1:'U475', 2:'U560', 3:'U668', 4:'U840', 5:'U717'}, 
	axis=1)
# Similarly for standard deviations
joined = joined.rename({'1_std':'U475_std', '2_std':'U560_std', 
	'3_std':'U668_std', '4_std':'U840_std', '5_std':'U717_std'}, 
	axis=1)

# Drop clear outliers identified in previous runs of this script
joined = joined.drop(labels=['21_7_SB3', '15_7_SB2'])


## Plotting and statistics, band-by-band
for band in wvl_centers:
	col = 'U%s_std' %band
	keep = joined[joined[col] <= cull_sd] 


	#sns.jointplot(x='R%s' %band, y='U%s' %band, data=joined, stat_func=spearmanr, xlim=(0,1), ylim=(0,1), size=4)

	X = keep['R%s' %band]
	y = keep['U%s' %band]
	X = sm.add_constant(X)
	model = sm.OLS(y, X) # or QuantReg
	#model = sm.WLS(y, X, weights=joined['U%s_std' %band]) # or QuantReg
	results = model.fit() # if QuantReg, can pass p=percentile here
	print(results.summary())

	# Plot it
	plt.figure(figsize=(4,4))
	axes = plt.axes(aspect='equal')
	keep.plot(kind='scatter', x='R%s' %band, y='U%s' %band, marker='o', yerr='U%s_std' %band, ax=axes, label='U Original')
	plt.ylim(0,1)
	plt.xlim(0,1)

	# Empirically-derived scaling factor
	difference = (keep['U%s' %band] - keep['R%s' %band])
	diff_mean = difference.mean()
	joined['U%s_corr' %band] = joined['U%s' %band] - diff_mean
	joined.plot(kind='scatter', x='R%s' %band, y='U%s_corr' %band, marker='o', color='#E31A1C', yerr='U%s_std' %band, ax=axes, label='U Corrected')
	print('Difference: ' + str(diff_mean))

	plt.title('R$^2$: %s, Difference: %s' %(np.round(results.rsquared,2), np.round(diff_mean,2)))
	plt.legend()
	plt.savefig('/scratch/UAV/uav_hcrf_comparison_bandcorrect_2017_b%s_win%s_sd%s.png' %(band,uav_window,cull_sd), dpi=300)

	## RMSE (After Tagle 2017)
	Eperc = ((keep['U%s' %band]-keep['R%s' %band]) * 100) / keep['R%s' %band]
	E = ((keep['U%s' %band]-keep['R%s' %band]))
	RMSE = np.sqrt(np.mean(E**2))
	print(RMSE)
	NRMSD = RMSE / (keep['R%s' %band].max() - keep['R%s' %band].min())
	print(NRMSD)