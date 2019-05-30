# load_s2_data.py
import datetime as dt
import xarray as xr
import salem


s2_times = [dt.datetime(2017, 7, 20), dt.datetime(2017, 7, 21)]
s2_data = xr.open_mfdataset('/home/at15963/projects/uav/data/S2/*class_clf20190305_170648.nc',
	concat_dim='time', chunks={'y':2000, 'x':2000})
s2_data['time'] = s2_times

s2_data.albedo.attrs['pyproj_srs'] = 'epsg:32622'
s2_data.classified.attrs['pyproj_srs'] = 'epsg:32622'
