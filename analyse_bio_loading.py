import sys
import xarray_classify
import xarray as xr
import pandas as pd
import statsmodels.api as sm

## Approx biomass loading
# From JC email 2018-05-24:
# However as per Chris, remember that BBA vs cell counts not really appropriate - should be BBA vs biovolume.

logcellsml = (-4.592 * uav.albedo.sel(time='2017-07-21') + 5.392) 
# JC relationship doesn't seem of right magnitude - x100 seems to fix it but needs checking
cellsml = xr.apply_ufunc(np.exp, logcellsml.load()) * 100
cellsdwml = cellsml * 1 #chris reckons cell dry weight is roughly 1 ng (maybe a bit less) as a ballpark estimate - 2018-06-05
cellsdwg = cellsdwml * 0.4
cells_dw_mg_g = cellsdwg * 1e-6
figure(), cells_dw_mg_g.plot.imshow(vmin=0,vmax=0.01, cmap='Reds')

## Blob detection
# import cv2
# detector = cv2.SimpleBlobDetector()
# keypoints = detector.detect(uav.classified.sel(time='2017-07-24').where(uav.classified == 5).values)

# uav.plot.hist(bins=vals)

# from skimage.feature import blob_dog, blob_log, blob_doh
# toblob = uav.classified.where(uav.classified == 5).sel(time='2017-07-24').isel(x=slice(3000,4000),y=slice(3000,4000)).values
# toblob = np.where(np.isnan(toblob),0,1)      
# #blobs_log = blob_log(toblob, max_sigma=30, num_sigma=10, threshold=.1)
# blobs_doh = blob_doh(toblob, max_sigma=30, threshold=.01)
# # Compute radii in the 3rd column.
# blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)



#### Cell counts work
import sys
sys.path.append("/home/at15963/scripts/IceSurfClassifiers") 
import xarray_classify

## RedEdge values for spectra. --- use to load in RedEdge measurements of destructive sites.
rededge = pd.read_excel('/home/at15963/Dropbox/work/black_and_bloom/multispectral-sensors-comparison.xlsx',
	sheet_name='RedEdge')
wvl_centers = rededge.central
wvls = pd.DataFrame({'low':rededge.start, 'high':rededge.end})
HCRF_file = '/scratch/field_spectra/HCRF_master.csv'
spectra = xarray_classify.load_hcrf_data(HCRF_file, wvls)

counts = pd.read_excel('/home/at15963/Dropbox/work/data/field_processed_2017/Updated_GrIS_Cell count results_250518.xlsx', sheet_name='Cells per ml')
counts = counts.dropna()
counts['Cells/ml'] = counts['Cells/ml'].astype('float')

bbas_counts = bbas_mean.merge(counts, on='spec_id')

spectra_counts = spectra.merge(counts, left_index=True, right_on='spec_id')

spectra_counts = spectra_counts.dropna()
spectra_counts = spectra_counts[spectra_counts['Cells/ml'] > 0]
for band in spectra.columns:
	figure()
	plot(np.log(spectra_counts['Cells/ml']), spectra_counts[band], 'o')
	title(band)
	ols = sm.OLS(spectra_counts[band], sm.add_constant(np.log(spectra_counts['Cells/ml'])))
	print(ols.fit().summary())
# Shows that the best bands are apparently R475, R560


estim_dw_mgg = counts['Cells/ml'] * 1 / 1e6

ratio = uav_refl.Band5.sel(time='2017-07-21') / uav_refl.Band3.sel(time='2017-07-21')