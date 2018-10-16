import pandas as pd


## BBA values
log_sheet = pd.read_csv('/scratch/field_spectra/temporal_log_sheet.csv')
bba = pd.read_csv('/scratch/field_spectra/BBA.txt')
# Mangle BBA.txt to get date/time information out 
info = bba['RowName'].str.split('_', 3, expand=True)
info.columns = ['Day','Month','Site','fill']
info['Month'] = info['Month'].astype(float)
info['Day'] = info['Day'].astype(float)
info['Site'] = info['Site'].astype(str)
info = info.drop('fill', axis=1)
bbas = pd.concat([bba,info], axis=1)
# BBA.txt contains albedo value for every single replicate, so generate
# means from each set of replicate measurements
bbas_mean = bbas.groupby(['Day','Month','Site']).mean()
bbas_mean = bbas_mean.reset_index()
bbas_mean['spec_id'] = ['%i_%i_%s' %(r['Day'],r['Month'],r['Site']) for ix, r in bbas_mean.iterrows()]
bbas_log = bbas_mean.merge(log_sheet,on=['Day','Month','Site'])


# Calculate daily mean BBA from Fieldspec samples
# Index corresponding to temporal samples
daily_bba_asd = bbas_log.BBA_list.groupby(bbas_log.Day).mean()
ix = [pd.datetime(2017,7,13),pd.datetime(2017,7,14),pd.datetime(2017,7,15),pd.datetime(2017,7,21),pd.datetime(2017,7,22),pd.datetime(2017,7,23),pd.datetime(2017,7,24),pd.datetime(2017,7,25)]
daily_bba_asd.index = ix