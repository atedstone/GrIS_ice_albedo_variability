import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import dates

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

plt.figure()

# Albedos
ax1 = plt.subplot(311)
plt.plot(albedos.index, albedos.MOD10A1, 'o', label='MOD10A1')
plt.plot(albedos.index, albedos.UAV, 'o', label='UAV')
plt.plot(s2_albedos.index, s2_albedos.alb, 'o', label='S2')
plt.legend()
plt.ylabel('Albedo')
plt.ylim(0.2, 0.8)

# Fluxes
ax2 = plt.subplot(312, sharex=ax1)
plt.plot(fluxes.index, fluxes.SWR_Wm2, color='#FF2A22', label='SW$_{net}$')
plt.plot(fluxes.index, fluxes.SHF_Wm2, color='#FF832C', label='SHF')
plt.plot(fluxes.index, fluxes.LHF_Wm2, color='#49BAD3', label='LHF')
plt.ylim(-50, 500)
plt.legend()
plt.ylabel('Energy (W m$^{-2}$)')

# Melt rates
ax3 = plt.subplot(313, sharex=ax1)
daily_melt = melt_rates.total.resample('1D').sum()
plt.bar(daily_melt.index, daily_melt, width=0.7, align='edge')
plt.ylim(0, 80)
plt.ylabel('Melt rate (mm w.e. d$^{-1}$)')

## Wide options
plt.xlim('2017-07-15', '2017-07-25')
plt.xlabel('July 2017')

ax1.xaxis.set_major_locator(dates.DayLocator())
ax1.xaxis.set_major_formatter(dates.DateFormatter('%d'))

sns.despine()