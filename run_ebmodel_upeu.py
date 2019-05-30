"""
Run energy balance model with PROMICE met measurements

@author Andrew Tedstone (a.j.tedstone@bristol.ac.uk)
"""

import pandas as pd
import datetime as dt

import ebmodel as ebm
import promice

##############################################################################
## Input Data

upe = promice.load('/home/at15963/Dropbox/work/data/promice_data_20190123-104847/UPE_U_hour.txt', 
	freq='hourly')

met_data = upe['2018-06-29':'2018-07-31']
met_data = met_data.filter(items=('AirTemperature(C)', 'AirPressure(hPa)',
	'ShortwaveRadiationDown_Cor(W/m2)', 'WindSpeed(m/s)', 'Albedo_theta<70d'))
met_data['hour'] = met_data.index.hour.astype('float') * 100
met_data['hour'][met_data['hour'] == 0] = 2400
met_data = met_data.rename({'ShortwaveRadiationDown_Cor(W/m2)':'swd', 'AirPressure(hPa)':'avp', 
	'AirTemperature(C)':'airtemp', 'WindSpeed(m/s)':'windspeed', 'hour':'time', 'Albedo_theta<70d':'alb'}, axis='columns')

met_data['alb'] = met_data['alb'].resample('1H').ffill()

lat = 72.8878
lon = 53.5783
lon_ref = -45.
summertime = 1
slope = 1.
aspect = 270.
elevation = 940.
roughness = 0.001 # 1 mm
met_elevation = 940.
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
		ts['swd'], ts['avp'], ts['airtemp'], ts['windspeed'], ts['alb'], roughness)

	# Calculate melting
	swmelt,lwmelt,shfmelt,lhfmelt,total = ebm.calculate_melt(SWR,LWR,SHF,LHF,
		ts['windspeed'],ts['airtemp'])

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

# fluxes.to_csv('ebm17_varalb_fluxes_5deg_asp270_z0.001_alb_S6new.csv')
# melt_rates.to_csv('ebm17_varalb_melt_5deg_asp270_z0.001_alb_S6new.csv')


"""
2018 snow clearing date estimated visually from HeightSensorBoom(m):
29 June
"""
