# analyse_uav_dems.py

detrended_mean.
figure(),detrended_mean.detrended_mean.sel(time='2017-07-21').plot(vmin=-0.1,vmax=0.1,cmap='RdBu') 


import salem
rcParams['grid.linewidth'] = 0

# Shouldn't really visualise with diverging colourmap as the zero is to an arbitrary datum.
figure(),roi.salem.quick_map(vmin=-0.2,vmax=0.2,cmap='RdBu_r')

# Elevation change over time
# simple histograms




## All analysis below uses this ROI
detr_msk_all = detrended_mean.detrended_mean.salem.roi(shape=shpf)

detr_msk_all = detrended.detrended.salem.roi(shape=shpf)

# Daily histogram of detrended DEM
figure()
n = 1
for t in detr_msk_all.time:
	plt.subplot(len(detr_msk_all.time), 1, n)
	#plt.yscale('log')
	detr_msk_all.sel(time=t).plot.hist(bins=[-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5],width=0.08)
	plt.title(t.values)
	plt.ylim(1,9e6)
	n += 1
tight_layout()

detrind_msk_all = detrended.detrended.sel(time=slice('2017-07-15','2017-07-22')).salem.roi(shape=shpf)
rawdem_msk_all = dems.Band1.sel(time=slice('2017-07-15','2017-07-22')).salem.roi(shape=shpf)
# Check for temporal trends
vals = rawdem_msk_all.values
dates = rawdem_msk_all['time.day'].values

vals2 = vals.reshape(len(dates), -1)
regressions, residuals, _, _, _ = np.polyfit(dates, vals2, 1, full=True)
trends = regressions[0,:].reshape(vals.shape[1], vals.shape[2])
trends = np.flipud(trends)
residuals = np.flipud(residuals.reshape(vals.shape[1], vals.shape[2]))
figure(),imshow(trends,cmap='RdBu',vmin=-0.03,vmax=0.03),colorbar()


# Check daily DEM Z values for GCPs
import geopandas_helpers
gcps = geopandas_helpers.load_xyz_gpd('/home/at15963/Dropbox/work/data/field_processed_2017/pixel_gcps_kely_formatted.csv')  
gcps_utm = gcps.to_crs({'init':'epsg:32623'})

store = {}
for ix, gcp in gcps_utm.iterrows():
	val = dems.Band1.sel(x=gcp.geometry.x, y=gcp.geometry.y, method='nearest').load()
	store[gcp.Id] = val.to_pandas()

gcpdemz = pd.DataFrame(store)


"""
gcpdemz.describe()                                                                        
Out[252]: 
              GCP1        GCP10        GCP11     ...              GCP7         GCP8         GCP9
count     5.000000     5.000000     5.000000     ...          5.000000     5.000000     5.000000
mean   1063.132080  1057.952393  1055.279053     ...       1065.815674  1063.988037  1060.866455
std       0.043730     0.030773     0.039006     ...          0.017619     0.021821     0.021123
min    1063.056641  1057.921631  1055.231323     ...       1065.793091  1063.950195  1060.838867
25%    1063.133179  1057.927734  1055.262329     ...       1065.813110  1063.989990  1060.857910
50%    1063.147339  1057.942383  1055.266968     ...       1065.813721  1063.997192  1060.861328
75%    1063.159424  1057.984375  1055.302490     ...       1065.815430  1063.997681  1060.881592
max    1063.163330  1057.985718  1055.332275     ...       1065.842529  1064.005127  1060.892822
"""