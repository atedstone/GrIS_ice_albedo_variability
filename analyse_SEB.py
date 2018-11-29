# Analyse surface energy balance conditions for pixel

# Using EB_AUTO outputs

# Albedo from MODIS - from pixel in which 2017 camp was located
fluxes_modis = pd.read_csv('/home/at15963/Dropbox/work/papers/tedstone_uavts/ebm17_varalb_fluxes_5deg_asp270_z0.001_modalb_S6new.csv', 
	index_col=0, parse_dates=True)
melting_modis = pd.read_csv('/home/at15963/Dropbox/work/papers/tedstone_uavts/ebm17_varalb_melt_5deg_asp270_z0.001_modalb_S6new.csv', 
	index_col=0, parse_dates=True)

# Albedo from the S6 AWS
fluxes_s6alb = pd.read_csv('/home/at15963/Dropbox/work/papers/tedstone_uavts/ebm17_varalb_fluxes_5deg_asp270_z0.001_alb_S6new.csv', 
	index_col=0, parse_dates=True)
melting_s6alb = pd.read_csv('/home/at15963/Dropbox/work/papers/tedstone_uavts/ebm17_varalb_melt_5deg_asp270_z0.001_alb_S6new.csv', 
	index_col=0, parse_dates=True)


# Get rid of negative net SW radiation
fluxes_modis.SWR_Wm2 = fluxes_modis.SWR_Wm2[fluxes_modis.SWR_Wm2 > 0]

# Compute balance between turbulent and radiative energy sources
radsrc = ((fluxes_modis.LHF_Wm2 + fluxes_modis.SHF_Wm2)-(fluxes_modis.SWR_Wm2))

# Add LWR flux (which is basically always -ve) to find out if melting is able to occur
# I.e. if we get a +ve value then conditions for melt-out are met.
# In MAR this is sorted by only computing radsrc when wem_SV > 0 - ie only computed for melting surfaces.
radsrc_lw = radsrc + fluxes_modis.LWR_Wm2


#figure()

