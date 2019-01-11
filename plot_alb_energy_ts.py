import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import dates
import datetime as dt

sns.set_context('paper')
sns.set_style("ticks")

fluxes = pd.read_csv('/home/at15963/projects/uav/outputs/ebm17_varalb_fluxes_5deg_asp270_z0.001_alb_S6new.csv',
	index_col=0, parse_dates=True)
melt_rates = pd.read_csv('/home/at15963/projects/uav/outputs/ebm17_varalb_melt_5deg_asp270_z0.001_alb_S6new.csv',
	index_col=0, parse_dates=True)
albedos = pd.read_csv('/home/at15963/projects/uav/outputs/sensor_albedos.csv',
	index_col=0, parse_dates=True)
s2_albedos = pd.read_csv('/home/at15963/projects/uav/outputs/s2_alb_uavpx.csv',
	index_col=0, parse_dates=True, names=['date','alb'])

# MODIS sinusoidal albedos
sin_albs = pd.read_csv('/home/at15963/projects/uav/outputs/MOD10A1_sinusoidal_pixel_albedos.csv',
	index_col=0, parse_dates=True)

sin_albs['avg'] = sin_albs.mean(axis=1)

plt.figure()

# Albedos
ax1 = plt.subplot(311)
#plt.plot(sin_albs.index, sin_albs.left, 'o', markeredgecolor='red', color='none', label='MOD10A1 L')
#plt.plot(sin_albs.index, sin_albs.right, 'o', markeredgecolor='blue', color='none', label='MOD10A1 R')
plt.plot(sin_albs.index, sin_albs.avg, 'o', markeredgecolor='blue', color='none', label='MOD10A1')
plt.plot(albedos.index, albedos.UAV, 'x', label='UAV', color='black')
plt.plot(s2_albedos.index, s2_albedos.alb, '+', label='S2', color='black')
plt.legend(ncol=3)
plt.ylabel('Albedo')
plt.ylim(0.15, 0.85)
plt.tick_params(axis='x', bottom='off', top='off')
plt.xlim('2017-07-15', '2017-07-25')
plt.xticks([])

# Fluxes
ax2 = plt.subplot(312)
plt.plot(fluxes.index, fluxes.SWR_Wm2, color='#FF2A22', label='SW$_{net}$')
plt.plot(fluxes.index, fluxes.SHF_Wm2, color='#392C4A', label='SHF')
plt.plot(fluxes.index, fluxes.LHF_Wm2, color='#49BAD3', label='LHF')
plt.ylim(-50, 500)
plt.legend(ncol=3)
plt.ylabel('Energy (W m$^{-2}$)')
plt.tick_params(axis='x', bottom='off', top='off')
plt.xlim('2017-07-15', '2017-07-25')
plt.xticks([])

# Melt rates
ax3 = plt.subplot(313)
daily_melt = melt_rates.total.resample('1D').sum()
plt.bar(daily_melt.index + (dt.timedelta(days=1)/5), daily_melt, width=0.6, align='edge', color='#282C20')
plt.ylim(0, 80)
plt.ylabel('Melt rate (mm w.e. d$^{-1}$)')

## Wide options
plt.xlim('2017-07-15', '2017-07-25')
plt.xlabel('July 2017')

ax3.xaxis.set_major_locator(dates.DayLocator())
ax3.xaxis.set_major_formatter(dates.DateFormatter('%d'))

sns.despine()
ax1.spines['bottom'].set_visible(False)
ax2.spines['bottom'].set_visible(False)


"""
Still to do:

* Align y labels
* Tidy legends
* date limits for albedo subplot
* SHF xlim cutoff
* Style of albedo plotting? Tried a steps plot but it didn't look good. Could 
just do horizontal bars not joined up (i.e. axhspan).

"""