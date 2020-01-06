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

### COLORS
color_LHF = '#49BAD3'
color_SHF = '#392C4A'
color_SWR = '#FF2A22'
color_AirTemp = '#666666'

# old_size = rcParams['font.size']
# rcParams['font.size'] = 8
# rcParams['axes.labelsize'] = 8
#rcParams['legend.fontsize'] = 8

fluxes = pd.read_csv('/home/at15963/projects/uav/outputs/ebm17_varalb_fluxes_5deg_asp270_z0.001_alb_S6new.csv',
	index_col=0, parse_dates=True)
melt_rates = pd.read_csv('/home/at15963/projects/uav/outputs/ebm17_varalb_melt_5deg_asp270_z0.001_alb_S6new.csv',
	index_col=0, parse_dates=True)
surface_lowering = pd.read_excel('/home/at15963/Dropbox/work/data/field_processed_2017/ablation_stakes.xlsx',
	sheet_name='stakes_fmt_python', parse_dates=True, index_col=1)
albedos = pd.read_csv('/home/at15963/projects/uav/outputs/sensor_albedos.csv',
	index_col=0, parse_dates=True)
s2_albedos = pd.read_csv('/home/at15963/projects/uav/outputs/s2_alb_uavpx.csv',
	index_col=0, parse_dates=True, names=['date','alb'])
s2_albedos_modis = pd.read_csv('/home/at15963/projects/uav/outputs/s2_alb_modispx.csv',
	index_col=0, parse_dates=True, names=['date','alb'])

s6 = imauaws.load('/home/at15963/Dropbox/work/data/imau_aws/grl_s6_final_year2017.txt', 
	col_names='full')

met_data = s6['2017-07-01':'2017-08-01']
met_data = met_data.resample('1H').first()

# MODIS sinusoidal albedos
sin_albs = pd.read_csv('/home/at15963/projects/uav/outputs/MOD10A1_sinusoidal_pixel_albedos.csv',
	index_col=0, parse_dates=True)

sin_albs['avg'] = sin_albs.mean(axis=1)

plt.figure(figsize=(4.5,5))

# Fluxes
ax1 = plt.subplot(411)
fluxes = fluxes.rolling('6H').mean()
fluxes.SWR_Wm2[fluxes.SWR_Wm2 < 0] = 0
plt.plot(fluxes.index, fluxes.SWR_Wm2, color=color_SWR, label='SW$_{net}$')
plt.plot(fluxes.index, fluxes.SHF_Wm2, color=color_SHF, label='SHF')
plt.plot(fluxes.index, fluxes.LHF_Wm2, color=color_LHF, label='LHF')
plt.ylim(-100, 500)
plt.legend(ncol=1, loc=(1.04,0.15), frameon=False, handlelength=1, markerfirst=False)
plt.ylabel('Energy (W m$^{-2}$)')
plt.tick_params(axis='x', bottom=False, top=False)
plt.xlim('2017-07-14 18:00', '2017-07-25')
plt.xticks([])
ax1.annotate('(a)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

# Melt rates
ax2 = plt.subplot(412)
#daily_melt = melt_rates.total.resample('1D').sum()
#plt.bar(daily_melt.index + (dt.timedelta(days=1)/5), daily_melt, width=0.6, align='edge', color='#282C20')
daily_melt = melt_rates.filter(like='melt')
daily_melt = daily_melt.where(daily_melt > 0)
daily_melt = daily_melt.where(s6['Taircorr(C)'] >= 0)

surface_lowering = surface_lowering.dropna()
surface_lowering = surface_lowering[surface_lowering.index < '2017-07-24']
melt_sampled = {}
for ix, row in surface_lowering.iterrows():
	dm = daily_melt.loc[ix:row.date_meas_taken].sum()
	melt_sampled[ix] = dict(date_meas_taken=row.date_meas_taken,
		SHF_melt=dm.SHF_melt, LHF_melt=dm.LHF_melt, SWR_melt=dm.SWR_melt,
		LWR_melt=dm.LWR_melt)
melt_sampled_df = pd.DataFrame.from_dict(melt_sampled, orient='index')

widths = melt_sampled_df.date_meas_taken - melt_sampled_df.index.to_series()
widths_frac = (widths.dt.total_seconds() / 60 / 60 / 24) - 0.1

daily_melt = daily_melt.resample('1D').sum()
daily_melt = daily_melt['2017-07-15':'2017-07-25']
daily_melt.index = daily_melt.index + (dt.timedelta(days=1)/5)
plt.bar(melt_sampled_df.index, melt_sampled_df.SWR_melt, width=widths_frac, align='edge', 
	color=color_SWR)
plt.bar(melt_sampled_df.index, melt_sampled_df.LHF_melt, width=widths_frac, align='edge', 
	color=color_LHF, bottom=melt_sampled_df.SWR_melt)
plt.bar(melt_sampled_df.index, melt_sampled_df.SHF_melt, width=widths_frac, align='edge', 
	color=color_SHF, bottom=melt_sampled_df.SWR_melt+melt_sampled_df.LHF_melt)
plt.ylim(0, 80)
plt.ylabel('Melt (mm w.e.)', labelpad=11)
plt.xlim('2017-07-14 18:00', '2017-07-25')
plt.yticks(np.arange(0,80,20), np.arange(0,80,20))
plt.tick_params(axis='x', bottom=True, top=False)
xticks, xticklabels = plt.xticks()
plt.xticks(xticks)
ax2.annotate('(b)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')

ax3 = ax2.twinx()
t_smooth = met_data['Taircorr(C)'].rolling('2H').mean()
ax3.plot(t_smooth.index, t_smooth, color='white', linewidth=3)
ax3.plot(t_smooth.index, t_smooth, color=color_AirTemp)
plt.ylim(-8,4.5)
plt.yticks([-6, -3, 0, 3], [-6, -3, 0, 3])
plt.ylabel('2 m T ($^o C$)', color=color_AirTemp)
ax3.yaxis.label.set_color(color_AirTemp)
ax3.tick_params(axis='y', colors=color_AirTemp)
ax3.spines['right'].set_color(color_AirTemp)
plt.tick_params(axis='x', bottom=False, top=False)
plt.xticks([])
plt.tick_params(axis='y', right=True, left=False)


# Surface lowering
ax4 = plt.subplot(413)
# In general
#surface_lowering.index = surface_lowering.index + dt.timedelta(60*60*17.5)
surface_lowering = surface_lowering.dropna()
widths = surface_lowering.date_meas_taken - surface_lowering.index.to_series()
widths_frac = (widths.dt.total_seconds() / 60 / 60 / 24) - 0.1
surface_lowering = surface_lowering.filter(items=['snow_lowering', 'ice_lowering']) * 10 # convert to mm
plt.bar(surface_lowering.index, surface_lowering['ice_lowering'], width=widths_frac, 
	align='edge', color='black', label='Ice')
plt.bar(surface_lowering.index, surface_lowering['snow_lowering'], width=widths_frac, 
	align='edge', color='gray',	bottom=surface_lowering['ice_lowering'],
	label='Snow')
plt.xlim('2017-07-14 18:00', '2017-07-25')

plt.ylabel('Surf. lowering (mm)', labelpad=7)
plt.tick_params(axis='x', bottom=False, top=False)
plt.xticks([])
plt.legend(ncol=1, loc=(0.8,0.6), frameon=False, handlelength=1, markerfirst=True)

ax4.annotate('(c)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')


# Albedos
ax5 = plt.subplot(414)
#plt.plot(sin_albs.index, sin_albs.left, 'o', markeredgecolor='red', color='none', label='MOD10A1 L')
#plt.plot(sin_albs.index, sin_albs.right, 'o', markeredgecolor='blue', color='none', label='MOD10A1 R')
plt.plot(s2_albedos_modis.index + dt.timedelta(hours=12), s2_albedos_modis.alb, 's', label='S2 (MOD)', markeredgecolor='grey', color='none', markersize=6)
plt.plot(s2_albedos.index + dt.timedelta(hours=12), s2_albedos.alb, 'x', label='S2 (UAS)', color='black')
plt.plot(sin_albs.index + dt.timedelta(hours=12), sin_albs.avg, 'o', markeredgecolor='blue', color='none', label='MOD10A1')
plt.plot(albedos.index + dt.timedelta(hours=12), albedos.UAV, 'x', label='UAS', color='orange')
plt.legend(ncol=1, loc=(1.04,0.1), frameon=False, markerfirst=False, handletextpad=0)
plt.ylabel('Albedo', labelpad=8.5)
plt.ylim(0.15, 0.85)
plt.tick_params(axis='x', bottom=True, top=False)
plt.xlim('2017-07-14 18:00', '2017-07-25')
plt.xlabel('July 2017')

ax5.annotate('(d)', fontsize=8, fontweight='bold', xy=(0.02,0.95), xycoords='axes fraction',
           horizontalalignment='left', verticalalignment='top')


## Wide options
plt.xlim('2017-07-14 18:00', '2017-07-25')

ax5.xaxis.set_major_locator(dates.DayLocator())
ax5.xaxis.set_major_formatter(dates.DateFormatter('%d'))

sns.despine()
ax1.spines['bottom'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax3.spines['right'].set_visible(True)
ax3.spines['left'].set_visible(False)

ax1.spines['left'].set_position(('outward', 5))
ax2.spines['left'].set_position(('outward', 5))
ax3.spines['right'].set_position(('outward', 5))
ax4.spines['left'].set_position(('outward', 5))
ax5.spines['left'].set_position(('outward', 5))

plt.tight_layout()
plt.subplots_adjust(hspace=0.08)

plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission3/figures/s6_energy_alb_ts.png', dpi=300)
plt.savefig('/home/at15963/Dropbox/work/papers/tedstone_uavts/submission3/figures/s6_energy_alb_ts.pdf', dpi=300)
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