"""
Run energy balance model with S6 met measurements.

@author Andrew Tedstone (a.j.tedstone@bristol.ac.uk)
"""

import pandas as pd
import datetime as dt
import numpy as np
import ebmodel as ebm
import imauaws


##############################################################################
## Input Data

s6 = imauaws.load('/home/at15963/Dropbox/work/data/imau_aws/grl_iws05_final_year2017.txt', 
	col_names='full')

met_data = s6['2017-07-01':'2017-08-01']
met_data = met_data.resample('1H').first()

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

albedos = np.arange(0, 1, 0.01)
for albedo in albedos:

	# Check time zone that ebmodel uses!
	time = '1200'

	# Calculate energy balance
	SWR,LWR,SHF,LHF = ebm.calculate_seb(
		lat, lon, lon_ref, 201, float(time), summertime,
		slope, aspect, elevation, met_elevation, lapse,
		578.0, 892, 0.0058, 4.89, albedo, roughness)

	# Calculate melting
	swmelt,lwmelt,shfmelt,lhfmelt,total = ebm.calculate_melt(SWR,LWR,SHF,LHF,
		4.89,0.0058)

	# Store radiative fluxes and melt rates for this timestep
	flux_store[albedo] = {'SWR_Wm2':SWR, 'LWR_Wm2':LWR, 'SHF_Wm2':SHF, 
		'LHF_Wm2':LHF}
	melt_store[albedo] = {'SWR_melt':swmelt, 'LWR_melt':lwmelt, 
		'SHF_melt':shfmelt, 'LHF_melt':lhfmelt}

# Convert outputs to pandas DataFrame.
fluxes = pd.DataFrame.from_dict(flux_store, orient='index')
melt_rates = pd.DataFrame.from_dict(melt_store, orient='index')
#melt_rates['total'] = melt_rates.sum(axis=1)

total_melt_rates = melt_rates.sum(axis=1)

