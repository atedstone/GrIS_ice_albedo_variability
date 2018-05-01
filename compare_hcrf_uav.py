import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import numpy as np
import pyproj

import georaster
import xarray_classify

samples = pd.read_csv('/home/at15963/Dropbox/work/data/field_processed_2017/uav_sb_locations.csv')

all_spectra = pd.read_csv('/scratch/field_spectra/HCRF_master.csv')
all_spectra.index = all_spectra.index + 350
log_sheet = pd.read_csv('/scratch/field_spectra/temporal_log_sheet.csv')
temporal = log_sheet.join(all_spectra)
HCRF_temporal_classes = '/home/at15963/Dropbox/work/data/temporal_field_spectra_classes.csv'
classes = log_sheet.filter(items=['Spectra','Surf Type'], axis=1)
classes.columns = ['sample', 'label']
classes['numeric_label'] = 0
classes.to_csv(HCRF_temporal_classes, index=False)

# hcrf = pd.read_csv('/scratch/field_spectra/HCRF_master.csv')

# Load ground reflectance spectra corresponding to red-edge sensor
rededge = pd.read_excel('/home/at15963/Dropbox/work/black_and_bloom/multispectral-sensors-comparison.xlsx',
	sheet_name='RedEdge')
wvl_centers = rededge.central
wvls = pd.DataFrame({'low':rededge.start, 'high':rededge.end})
HCRF_file = '/scratch/field_spectra/HCRF_master.csv'
HCRF_classes = '/home/at15963/Dropbox/work/data/field_spectra_classes.csv'
spectra = xarray_classify.load_hcrf_data(HCRF_file, HCRF_classes, wvls)
temporal_spectra = xarray_classify.load_hcrf_data(HCRF_file, HCRF_temporal_classes, wvls)
spectra = pd.concat([spectra, temporal_spectra])

flights = {'20170715':'uav_20170715_refl_5cm.tif',
'20170717':'uav_20170717_refl_5cm.tif',
'20170720':'uav_20170720_refl_5cm.tif',
'20170721':'uav_20170721_refl_5cm.tif',
'20170722':'uav_20170722_refl_5cm.tif',
'20170723':'uav_20170723_refl_nolenscorr_5cm.tif',
'20170724':'uav_20170724_refl_5cm_v2.tif'}

store = {}

# windows: 3 = 15cm, 7=35 cm

## Get destructive sites
for ix, sampl in samples.iterrows():
	if pd.notnull(sampl.spec_id):
		px = sampl.sample_x
		py = sampl.sample_y

		d = sampl.date
		dstr = str(d)
		print(dstr)

		im = georaster.MultiBandRaster('/scratch/UAV/%s' %flights[dstr],
			load_data=False)

		val, wins = im.value_at_coords(px, py, window=5, return_window=True,
			reducer_function=np.nanmedian)


		stds = {}
		for n in np.arange(1,6):
			stds['%s_std' %n] = np.std(wins[n])
		val = {**val, **stds}
		store[sampl.spec_id] = val
		#print(sampl.spec_id, val)

		im = None


## Get temporal sites
# First convert site coordinates to UTM (only for the temporal sites, numbered 1:5)
all_gcps = pd.read_csv('/home/at15963/Dropbox/work/data/field_processed_2017/pixel_gcps_kely_formatted.csv', index_col=0)
temporal_gcps = {}
utm = pyproj.Proj('+init=epsg:32623')
for	n in np.arange(1,6):
	gcp = all_gcps.ix['GCP%s' %n]
	utmx, utmy = utm(gcp.lon, gcp.lat)
	# Approximately identify the reflectance measurement center - move towards camp
	utmx += 0.4
	utmy -= 0.4
	temporal_gcps[n] = {'x':utmx, 'y':utmy}
temporal_gcps = pd.DataFrame(temporal_gcps).T

# Now pull out values from each flight
for flight in flights:

	im = georaster.MultiBandRaster('/scratch/UAV/%s' %flights[flight],
		load_data=False)

	for ix, gcp in temporal_gcps.iterrows():
		val, wins = im.value_at_coords(gcp.x, gcp.y, window=5, return_window=True,
			reducer_function=np.nanmedian)

		# Standard deviation in each band
		stds = {}
		for n in np.arange(1,6):
			stds['%s_std' %n] = np.std(wins[n])
		val = {**val, **stds}

		spec_id = flight[-2:] + '_7_S' + str(ix)
		store[spec_id] = val

	im = None





uav_refl = pd.DataFrame(store).T

joined = uav_refl.join(spectra)
# Drop rows for which no data (this is because values pulled out for all UAV flights, but temporal ground measurements not always taken)
joined = joined.dropna()
joined = joined.rename({1:'U475', 2:'U560', 3:'U668', 4:'U840', 5:'U717'}, 
	axis=1)
joined = joined.rename({'1_std':'U475_std', '2_std':'U560_std', 
	'3_std':'U668_std', '4_std':'U840_std', '5_std':'U717_std'}, 
	axis=1)

joined = joined.drop(labels=['21_7_SB3', '15_7_SB2'])

#figure, axes = plt.subplots(3,2)
#axes = axes.flatten()
#n = 0
from scipy.stats import spearmanr
r2 = []
for band in wvl_centers:
	col = 'U%s_std' %band
	keep = joined[joined[col] <= 0.05] 
	#plt.subplot(axes[n])
	#plt.plot(joined['R%s' %band], joined['U%s' %band], 'o')
	#joined.plot(kind='scatter', x='R%s' %band, y='U%s' %band, marker='o', ax=axes[n])
	#joined.plot(kind='scatter', x='R%s' %band, y='U%s' %band, marker='o', ax=axes[n])
	keep.plot(kind='scatter', x='R%s' %band, y='U%s' %band, marker='o', yerr='U%s_std' %band),ylim(0,1),xlim(0,1)
	#sns.jointplot(x='R%s' %band, y='U%s' %band, data=joined, stat_func=spearmanr, xlim=(0,1), ylim=(0,1), size=4)
	#plt.subplot(axes[n])
	#plt.xlim(0,1)
	#plt.ylim(0,1)
	#plt.xticks(np.arange(0,1.1,0.1))
	#plt.yticks(np.arange(0,1.1,0.1))
	#n += 1

	X = keep['R%s' %band]
	y = keep['U%s' %band]
	X = sm.add_constant(X)
	model = sm.OLS(y, X) # or QuantReg
	#model = sm.WLS(y, X, weights=joined['U%s_std' %band]) # or QuantReg
	results = model.fit() # if QuantReg, can pass p=percentile here
	print(results.summary())
	print(results.rsquared)
	r2.append(results.rsquared)