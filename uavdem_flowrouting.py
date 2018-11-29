from pygeoprocessing import routing

PROCESS_DIR = '/scratch/UAV/uav2017_dem/'
dem_sm_uri = PROCESS_DIR + 'uav_20170721_dem_5cm._commongrid.tif'
## Step 0: fill pits
dempits_uri = PROCESS_DIR + 'ROUTING_dem_filledpits.tif'
routing.fill_pits(dem_sm_uri, dempits_uri)


## Step 1: flow direction
flowdir_uri = PROCESS_DIR + 'ROUTING_1flowdir.tif'
routing.flow_direction_d_inf(dempits_uri, flowdir_uri)


## Step 2: flow accumulation
accum_uri = PROCESS_DIR + 'ROUTING_2accum.tif'
routing.flow_accumulation(flowdir_uri, dempits_uri, accum_uri)