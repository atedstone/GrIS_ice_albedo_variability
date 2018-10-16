## Slope, DEM, etc
# for f in *commongrid.tif; do gdaldem slope -of NetCDF $f ${f: 0:-4}_slope.nc; done
# for f in *commongrid.tif; do gdaldem aspect -of NetCDF $f ${f: 0:-4}_aspect.nc; done

# Read all UAV images into one multi-temporal frame.
dem_times = [dt.datetime(2017,7,15),
	dt.datetime(2017,7,20),
	dt.datetime(2017,7,21),
	dt.datetime(2017,7,22),
	dt.datetime(2017,7,23)
	]
dems = xr.open_mfdataset('/scratch/UAV/uav2017_dem/*commongrid.nc',
	concat_dim='time')#, chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
dems['time'] = dem_times 

slopes = xr.open_mfdataset('/scratch/UAV/uav2017_dem/*slope.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
slopes['time'] = dem_times 

aspects = xr.open_mfdataset('/scratch/UAV/uav2017_dem/*aspect.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
# Set up the time coordinate.
aspects['time'] = dem_times 


## Plane fit
# http://inversionlabs.com/2016/03/21/best-fit-surfaces-for-3-dimensional-data.html
rough_x = np.linspace(dems.x[0], dems.x[-1], dems.dims['x'] / 100)
rough_y = np.linspace(dems.y[0], dems.y[-1], dems.dims['y'] / 100)
zi = dems.Band1.sel(time='2017-07-21').interp(x=rough_x, y=rough_y)
zi_zeros = zi.where(zi > 500)
zi_msk_flat = zi_zeros.values.flatten()
# figure(), zi.plot(vmin=1040, vmax=1070)
xg = np.array([zi.x.values,] * len(zi.y)).flatten()
yg = np.array([zi.y.values,] * len(zi.x)).transpose().flatten()
xg[np.isnan(zi_msk_flat)] = np.nan
yg[np.isnan(zi_msk_flat)] = np.nan
xg = xg[~np.isnan(xg)]
yg = yg[~np.isnan(yg)]
zi_msk_flat = zi_msk_flat[~np.isnan(zi_msk_flat)]

A = np.c_[xg,yg,np.ones(xg.shape[0])]
C,_,_,_ = scipy.linalg.lstsq(A, zi_msk_flat)
surfx = np.array([dems.x.values,] * len(dems.y))
surfy = np.array([dems.y.values,] * len(dems.x)).transpose()
Z = C[0] * surfx + C[1] * surfy + C[2]

detrended = dems.Band1.sel(time='2017-07-21') - Z


## Basic blurring approach, by using xarray to downsample then substract downsampled from original
xi = np.array([zi.x.values,] * len(zi.y))
yi = np.array([zi.y.values,] * len(zi.x)).transpose()
zi = zi.where(zi > 1000)
zif = zi.interp(x=dems.x,y=dems.y)  


## Gaussian low-pass approach
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
import cv2
blur = cv2.GaussianBlur(dems.Band1.sel(time='2017-07-21').values, (99,99), 0)
filtered = dems.Band1.sel(time='2017-07-21')-blur
figure(),filtered.plot(vmin=-0.1,vmax=0.1),title('cv2.Gaussian 99')
# Check no local slopes accidentally caught/removed by verifying no local slopes present in blurred DEM
grads = np.gradient(blur)
figure(),imshow(np.sqrt(grads[0]**2+grads[1]**2),vmax=10) 

# For all DEMs at once
gauss_blur = lambda x,y : cv2.GaussianBlur(x, (y,y), 0)
def gauss_blur(x,y):
	print(x.shape)
	return cv2.GaussianBlur(np.squeeze(x), (y,y), 0)
blurs = xr.apply_ufunc(gauss_blur, dems.Band1, 99, dask='parallelized', output_dtypes=[float], input_core_dims=[[],[]])
filtered = dems.Band1 - blurs

# Using dask (kept here for reference only)
# Should not be parallelised as then edges between chunks appear!
# gauss_blur = lambda x,y : cv2.GaussianBlur(x, (y,y), 0)
# blurred = xr.apply_ufunc(gauss_blur, dems.Band1.sel(time='2017-07-21'), 99, dask='parallelized', output_dtypes=[float])
# filtered = dems.Band1.sel(time='2017-07-21') - blurred
# figure(),filtered.plot(vmin=-0.1, vmax=0.1)

## Binning by aspect
# However, all this might tell us is that we haven't fully corrected for BRDF issues!!
asp21 = aspects.transpose('time','y','x').Band1.sel(time='2017-07-21').to_pandas()
alb21 = uav.albedo.sel(time='2017-07-21').to_pandas()
combo = pd.DataFrame({'asp':asp21.values.flatten(),'alb':alb21.values.flatten()})
combo.groupby(pd.cut(combo.asp,36))['alb'].agg(['count','mean'])
"""
                      count      mean
asp                                  
(-0.36, 9.998]       331401  0.355746
(9.998, 19.997]      240294  0.355395
(19.997, 29.995]     192156  0.358363
(29.995, 39.993]     158546  0.362745
(39.993, 49.991]     132943  0.365501
(49.991, 59.99]      113766  0.372682
(59.99, 69.988]      100579  0.379343
(69.988, 79.986]      93084  0.381006
(79.986, 89.984]      85705  0.378249
(89.984, 99.983]      95874  0.378355
(99.983, 109.981]     85300  0.387210
(109.981, 119.979]   104776  0.367253
(119.979, 129.977]   109899  0.403651
(129.977, 139.976]   114203  0.394563
(139.976, 149.974]   127599  0.404502
(149.974, 159.972]   145787  0.423142
(159.972, 169.97]    173267  0.411075
(169.97, 179.969]    196561  0.421740
(179.969, 189.967]   293436  0.421146
(189.967, 199.965]   372371  0.421740
(199.965, 209.964]   524687  0.415167
(209.964, 219.962]   745829  0.416766
(219.962, 229.96]    923855  0.424208
(229.96, 239.958]   1147222  0.427509
(239.958, 249.957]  1437949  0.424014
(249.957, 259.955]  1703151  0.421941
(259.955, 269.953]  1815846  0.420382
(269.953, 279.951]  2067652  0.414429
(279.951, 289.95]   1882613  0.408613
(289.95, 299.948]   1701997  0.401603
(299.948, 309.946]  1427737  0.393765
(309.946, 319.944]  1131351  0.386911
(319.944, 329.943]   867970  0.379101
(329.943, 339.941]   665133  0.370571
(339.941, 349.939]   513513  0.361856
(349.939, 359.938]   373299  0.358165
"""