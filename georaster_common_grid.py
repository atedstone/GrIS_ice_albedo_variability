
import subprocess
import numpy as np
import pandas as pd

import georaster

ims = ['uav_20170715_refl_5cm.tif',
'uav_20170717_refl_5cm.tif',
'uav_20170720_refl_5cm.tif',
'uav_20170721_refl_5cm.tif',
'uav_20170722_refl_5cm.tif',
'uav_20170723_refl_nolenscorr_5cm.tif',
'uav_20170724_refl_5cm_v2.tif'
]

ims = ['uav_20170715_dem_5cm.tif',
'uav_20170720_dem_5cm.tif',
'uav_20170721_dem_5cm.tif',
'uav_20170722_dem_5cm.tif',
'uav_20170723_dem_5cm.tif']

dcs = []
for imf in ims:
	im = georaster.MultiBandRaster(imf, load_data=False)
	# Order  [xll,xur,yll,yur]
	xll,xur,yll,yur = im.extent
	xpx,ypx = im.nx, im.ny
	dc = dict(xll=xll,xur=xur,yll=yll,yur=yur,xpx=xpx,ypx=ypx)
	dcs.append(dc)
	im = None

df = pd.DataFrame(dcs)
xll_min = np.floor(df.xll.min())
xur_max = np.ceil(df.xur.max())
yll_min = np.floor(df.yll.min())
yur_max = np.ceil(df.yur.max())

# Hard-code the values that this script chose for the reflectance mosaics
xll_min = 310895.000
xur_max = 311219.000
yll_min = 7446509.000
yur_max = 7446839.000

print('XLL min: ', xll_min)
print('XUR max: ', xur_max)
print('YLL min: ', yll_min)
print('YUR max: ', yur_max)

# construct gdalwarp arguments
cmd = 'gdalwarp -te %s %s %s %s ' %(xll_min, yll_min, xur_max, yur_max)
cmd = cmd + '-tr 0.05 0.05 '
#cmd = cmd + '-of NetCDF '

for imf in ims:
	cmdh = '%s %s %s' %(cmd, imf, imf[:-3]+'_commongrid.tif')
	print(cmdh)
	subprocess.call(cmdh, shell=True)

