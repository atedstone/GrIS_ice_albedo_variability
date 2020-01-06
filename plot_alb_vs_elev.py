import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import seaborn as sns
import pandas as pd

sns.set_context('paper', rc={"font.size":8,"axes.titlesize":8,"axes.labelsize":8,"legend.fontsize":8})
sns.set_style('ticks')

detrended = xr.open_dataset('/scratch/UAV/photoscan_outputs_2018/uav_20180724_PM_dem_blur399_detr.nc',
	chunks={'x':1000, 'y':1000})
classified = xr.open_dataset('/scratch/UAV/L3/uav_20180724_PM_refl_class_clf20190130_171930.nc',
	chunks={'x':1000, 'y':1000}) 
classified['x'] = detrended.x
classified['y'] = detrended.y

combined = pd.DataFrame({
	'dem':detrended.detrended.stack(dim=('x','y')).to_pandas(),
	'albedo':classified.albedo.stack(dim=('x','y')).to_pandas()
	})

combined_nonan = combined.dropna()

alb_binned = pd.cut(combined_nonan.albedo,bins=np.arange(0,1,0.02))

meds = combined_nonan.dem.groupby(alb_binned).median()
std = combined_nonan.dem.groupby(alb_binned).std()
counts = combined_nonan.dem.groupby(alb_binned).count()

stats = pd.DataFrame({
	'elev_med':meds,
	'elev_std':std,
	'npx':counts,
	'perc':(100 / counts.sum() * counts),
	'alb':np.arange(0.01,0.99, 0.02)
	}, index=np.arange(0.01,0.99, 0.02))

plt.figure()
ax = stats.plot(kind='scatter',x='alb',y='elev_med', yerr='elev_std')

plt.xlabel('Albedo')
plt.ylabel('Detr. Elev. (m)')


ax2 = ax.twinx()
plt.plot(stats.alb, stats.perc)
plt.ylabel('% of study area')

sns.despine(right=False)


stats_cull = stats[stats.perc > 0.5]
print(stats_cull.corr(method='spearman')**2)