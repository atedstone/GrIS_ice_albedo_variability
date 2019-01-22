import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import dates
from matplotlib import rcParams
import datetime as dt
import numpy as np

import imauaws 

sns.set_context('paper', rc={"font.size":8,"axes.titlesize":8,"axes.labelsize":8,"legend.fontsize":8})
sns.set_style("ticks")

# old_size = rcParams['font.size']
# rcParams['font.size'] = 8
# rcParams['axes.labelsize'] = 8
#rcParams['legend.fontsize'] = 8

fluxes = pd.read_csv('/home/at15963/projects/uav/outputs/ebm17_varalb_fluxes_5deg_asp270_z0.001_alb_S6new.csv',
	index_col=0, parse_dates=True)
melt_rates = pd.read_csv('/home/at15963/projects/uav/outputs/ebm17_varalb_melt_5deg_asp270_z0.001_alb_S6new.csv',
	index_col=0, parse_dates=True)
albedos = pd.read_csv('/home/at15963/projects/uav/outputs/sensor_albedos.csv',
	index_col=0, parse_dates=True)
s2_albedos = pd.read_csv('/home/at15963/projects/uav/outputs/s2_alb_uavpx.csv',
	index_col=0, parse_dates=True, names=['date','alb'])
s2_albedos_modis = pd.read_csv('/home/at15963/projects/uav/outputs/s2_alb_modispx.csv',
	index_col=0, parse_dates=True, names=['date','alb'])

s6 = imauaws.load('/home/at15963/Dropbox/work/data/imau_aws/grl_iws05_final_year2017.txt', 
	col_names='full')

met_data = s6['2017-07-01':'2017-08-01']
met_data = met_data.resample('1H').first()

# MODIS sinusoidal albedos
sin_albs = pd.read_csv('/home/at15963/projects/uav/outputs/MOD10A1_sinusoidal_pixel_albedos.csv',
	index_col=0, parse_dates=True)

sin_albs['avg'] = sin_albs.mean(axis=1)

plt.figure(figsize=(4.5,4))

# Albedos
ax1 = plt.subplot(311)
#plt.plot(sin_albs.index, sin_albs.left, 'o', markeredgecolor='red', color='none', label='MOD10A1 L')
#plt.plot(sin_albs.index, sin_albs.right, 'o', markeredgecolor='blue', color='none', label='MOD10A1 R')
plt.plot(s2_albedos_modis.index + dt.timedelta(hours=12), s2_albedos_modis.alb, 's', label='S2 (MOD)', markeredgecolor='grey', color='none', markersize=6)
plt.plot(s2_albedos.index + dt.timedelta(hours=12), s2_albedos.alb, 'x', label='S2 (UAS)', color='black')
plt.plot(sin_albs.index + dt.timedelta(hours=12), sin_albs.avg, 'o', markeredgecolor='blue', color='none', label='MOD10A1')
plt.plot(albedos.index + dt.timedelta(hours=12), albedos.UAV, 'x', label='UAS', color='purple')
plt.legend(ncol=1, loc=(1,0.0), frameon=False)
plt.ylabel('Albedo', labelpad=9)
plt.ylim(0.15, 0.85)
plt.tick_params(axis='x', bottom=False, top=False)
plt.xlim('2017-07-14 18:00', '2017-07-25')
plt.xticks([])
ax1.annotate('(a)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Fluxes
ax2 = plt.subplot(312)
fluxes = fluxes.rolling('6H').mean()
plt.plot(fluxes.index, fluxes.SWR_Wm2, color='#FF2A22', label='SW$_{net}$')
plt.plot(fluxes.index, fluxes.SHF_Wm2, color='#392C4A', label='SHF')
plt.plot(fluxes.index, fluxes.LHF_Wm2, color='#49BAD3', label='LHF')
plt.ylim(-100, 500)
plt.legend(ncol=1, loc=(1.04,0.15), frameon=False, handlelength=1)
plt.ylabel('Energy (W m$^{-2}$)')
plt.tick_params(axis='x', bottom=False, top=False)
plt.xlim('2017-07-14 18:00', '2017-07-25')
plt.xticks([])
ax2.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Melt rates
ax3 = plt.subplot(313)
daily_melt = melt_rates.total.resample('1D').sum()
daily_melt = daily_melt['2017-07-15':'2017-07-25']
plt.bar(daily_melt.index + (dt.timedelta(days=1)/5), daily_melt, width=0.6, align='edge', color='#282C20')
plt.ylim(0, 80)
plt.ylabel('Melt (mm w.e.)', labelpad=9)
plt.xlim('2017-07-14 18:00', '2017-07-25')
plt.yticks(np.arange(0,80,20), np.arange(0,80,20))
plt.xlabel('July 2017')
ax3.annotate('(c)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

ax4 = ax3.twinx()
t_smooth = met_data['Taircorr(C)'].rolling('6H').mean()
ax4.plot(t_smooth.index, t_smooth, color='white', linewidth=3)
ax4.plot(t_smooth.index, t_smooth)
plt.ylim(-8,4)
plt.yticks([-6, -3, 0, 3], [-6, -3, 0, 3])
plt.ylabel('2 m T ($^o C$)')

## Wide options
plt.xlim('2017-07-14 18:00', '2017-07-25')

ax3.xaxis.set_major_locator(dates.DayLocator())
ax3.xaxis.set_major_formatter(dates.DateFormatter('%d'))

sns.despine()
ax1.spines['bottom'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax4.spines['right'].set_visible(True)
ax4.spines['left'].set_visible(False)
plt.tick_params(axis='y', right=True, left=False)

ax1.spines['left'].set_position(('outward', 5))
ax2.spines['left'].set_position(('outward', 5))
ax3.spines['left'].set_position(('outward', 5))
ax4.spines['right'].set_position(('outward', 5))

plt.tight_layout()
plt.subplots_adjust(hspace=0.08)

# rcParams['font.size'] = old_size
# rcParams['axes.labelsize'] = old_size
# rcParams['legend.fontsize'] = old_size

"""
Still to do:

* Align y labels
* Tidy legends
* date limits for albedo subplot
* SHF xlim cutoff
* Style of albedo plotting? Tried a steps plot but it didn't look good. Could 
just do horizontal bars not joined up (i.e. axhspan).

"""