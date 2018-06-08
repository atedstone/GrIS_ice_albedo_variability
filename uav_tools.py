


def read_gcps(fn, proj4, xoff=0.4, yoff=-0.4):
	""" Read in GCP sites saved in lat/lon.

	CSV file needs following columns:
	Id,lon,lat,z

	Id must have format GCP[n], where [n] is number of the GCP.
	lon and lat are in decimal degrees, z is elevation in metres.

	Inputs:
	fn : filename of csv file to open
	proj4 : proj4 string to convert coordinates to, e.g. +init=epsg32623
	xoff : x distance to offset GCP by
	yoff : y distance to offset GCP by

	Returns:
	pd.DataFrame

	"""

	all_gcps = pd.read_csv(fn, index_col=0)
	temporal_gcps = {}
	utm = pyproj.Proj(proj4)
	for ix, gcp in all_gcps.iterrows():
		utmx, utmy = utm(gcp.lon, gcp.lat)
		# Approximately identify the reflectance measurement center - move towards camp
		utmx += xoff
		utmy -= yoff
		all_gcps[ix] = {'x':utmx, 'y':utmy}
	all_gcps = pd.DataFrame(all_gcps).T

	return all_gcps


