"""
Run energy balance model with S6 met measurements.

@author Andrew Tedstone (a.j.tedstone@bristol.ac.uk)
"""

import pandas as pd
import datetime as dt

import ebmodel as ebm
import imauaws

##############################################################################
## Input Data

s6 = imauaws.load('/home/at15963/Dropbox/work/data/imau_aws/grl_iws05_final_year2017.txt', 
	col_names='full')

met_data = s6['2017-07-01':'2017-08-01']
met_data = met_data.resample('1H').first()

# SWin=NRUavg(W) and SWout=NRLavg(W)
albedo = met_data['NRLavg(W)'].where(met_data['NRUavg(W)'] > 250).resample('1D').sum() / met_data['NRUavg(W)'].where(met_data['NRUavg(W)'] > 250).resample('1D').sum()
albedo_1h = met_data['NRLavg(W)'].where(met_data['NRUavg(W)'] > 250) / met_data['NRUavg(W)'].where(met_data['NRUavg(W)'] > 250)
# Graphing shows we want to ffill (not bfill)
albedo_fullts = albedo.resample('1H').ffill()
met_data['alb'] = albedo_fullts

## MODIS albedo
# modal = pd.read_csv('camp_mod10a1_albedo_2017.csv', names=['date','alb'], 
# 	index_col='date', parse_dates=True, squeeze=True)

# met_data['modalb'] = modal.ffill().resample('1H').ffill()


# lat = 67.0666
# lon = -49.38
# lon_ref = -45.
# summertime = 1
# slope = 10.
# aspect = 90.
# elevation = 1073.
# roughness = 0.002
# met_elevation = 1000.
# lapse = 0.04

lat = 67.0666
lon = -49.38
lon_ref = -45.
summertime = 1
slope = 5.
aspect = 270.
elevation = 1073.
roughness = 0.001 # 1 mm
met_elevation = 1073.
lapse = 0.

##############################################################################

flux_store = {}
melt_store = {}
for ix, ts in met_data.iterrows():

	time = str(int(float(ix.hour)) * 100).zfill(4)
	if time == 0:
		time = 2400

	# Calculate energy balance
	SWR,LWR,SHF,LHF = ebm.calculate_seb(
		lat, lon, lon_ref, int(ix.strftime('%j')), float(time), summertime,
		slope, aspect, elevation, met_elevation, lapse,
		ts['NRUavg(W)'], ts['BAP(hPa)'], ts['Taircorr(C)'], ts['HWSavg(m/s)'], ts['alb'], roughness)

	# Calculate melting
	swmelt,lwmelt,shfmelt,lhfmelt,total = ebm.calculate_melt(SWR,LWR,SHF,LHF,
		ts['HWSavg(m/s)'],ts['Taircorr(C)'])

	# Store radiative fluxes and melt rates for this timestep
	flux_store[ix] = {'SWR_Wm2':SWR, 'LWR_Wm2':LWR, 'SHF_Wm2':SHF, 
		'LHF_Wm2':LHF}
	melt_store[ix] = {'SWR_melt':swmelt, 'LWR_melt':lwmelt, 
		'SHF_melt':shfmelt, 'LHF_melt':lhfmelt}

# Convert outputs to pandas DataFrame.
fluxes = pd.DataFrame.from_dict(flux_store, orient='index')
melt_rates = pd.DataFrame.from_dict(melt_store, orient='index')
melt_rates['total'] = melt_rates.sum(axis=1)
melt_rates['total'][melt_rates['total'] < 0] = 0

fluxes.to_csv('ebm17_varalb_fluxes_5deg_asp270_z0.001_alb_S6new.csv')
melt_rates.to_csv('ebm17_varalb_melt_5deg_asp270_z0.001_alb_S6new.csv')


uav_flights = [
	dt.datetime(2017,7,20,12,0),
	dt.datetime(2017,7,21,15,0),
	dt.datetime(2017,7,22,10,0),
	dt.datetime(2017,7,23,10,30)]
Imagery on 20 July at S6 was acquired at 12:00-12:45 LT.
Imagery on 21 July at S6 was acquired at 14:50 LT onwards, hence shadows around hummocks (which are also thus visible in band 4 different maps).
22 July: 10 am LT
23 July: 10:30-11:30 LT

# Calculate amount of melt which occurred at S6 between flights.
# should I try to weight albedo used in model by that of UAV area? model running hourly, 
# uav estimates are only once a day.
# units are mmwe - but per what unit of time? --> looks like per the model timestep.
# bar chart of daily melt, split by energy flux responsible