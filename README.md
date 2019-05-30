# README

This repository contains the scripts written for the analysis and plotting of the data underlying the study Tedstone et al. 'Algal growth and weathering crust structure drive variability in Greenland Ice Sheet ice albedo'.

## Associated repositories

The scripts in this repository make use of the following additional repositories:

- `IceSurfClassifiers`. DOI: 10.5281/zenodo.3228329 
- `ebmodel`. DOI: 10.5281/zenodo.3228331
- `micasense_calibration`. DOI: 10.5281/zenodo.3228333
- `imageprocessing`. DOI: 10.5281/zenodo.3228327



## Datasets

Datasets referenced in these scripts will be archived and allocated a DOI upon final manuscript publication. In the meantime they can be found at `https://www.dropbox.com/` or on request to the corresponding author.

In several cases the scripts make reference to GeoTIFF representations of the data. The GeoTIFF representations are exactly the same as the data contained in the NetCDF versions and were generated from the NetCDFs using `gdalwarp`.



## Description of workflows

*Note*: In most cases the scripts still contain hard-coded file paths and so require modification if before trying to execute them.



### UAS imagery pre-processing and mosaicing

1. See the README in `micasense_calibration` for information on how to calibrate raw Micasense images (not provided with this publication). Publication-specific notes are provided below.
2. Use reflectance-corrected images as inputs to Agisoft Photoscan.
3. For 2017 data, run `compare_hcrf_uav.py` on orthomosaics versus ground data to check for required per-band scaling factors (computed by reference to ground spectroscopy).
4. For 2017 data, run `georaster_common_grid.py` to put all orthomosaics onto exactly the same-sized grid.


#### Publication-specific notes on image calibration

##### Overview of steps

1. Set up the image radiance-to-reflectance environment - full instructions accompany the GitHub repository `micasense_calibration`.
2. Run image calibration (see repository readme - `calc_rad2refl` and `process_flight_images` scripts).
3. Move files into per-band folders (`sort_images.py`)
4. scp the files onto server node (if using a server)
5. Use AgiSoft Photoscan according to USGS procedure.
6. I didn't set common extents of each UAV image from 2017 in PhotoScan, instead I did this in post-processing using `georaster_common_grid.py`, which outputs new GeoTIFFs. I then converted these GeoTIFFs to netcdf files using gdalwarp, for ingestion into classification routines which are explained later in this readme.


##### Note on reflectance panels

It makes no difference to the processing chain whether the Micasense panel or a Spectralon panel is used. If using a Spectralon panel then create a panel-specific file of the same format as that for a Micasense panel - as per the Micasense website, "The calibration data is provided as absolute reflectance (a value between 0.0 and 1.0) in the range of 400 nm to 850 nm (in increments of 1 nm). The calibration curve can be further simplified to be represented by 5 reflectance values, one for each of the 5 bands of the camera, by averaging the reflectance values in the calibration curve across the bandwidth of each band." 

So, if using a 99% Spectralon panel then provide 0.99 for each band.


##### Getting images ready

1. Run `calc_rad2refl.py`
2. Run `process_flight_images.py`
3. Move images into per-band folders (`sort_images.py`)


##### For 2018 imagery

Unlike in 2017, we took refl panel photos before and after each individual flight rather than just before flight 1 and after flight 2. The pixel consisted of two separate flights and so each flight needs to be pre-processed individually, i.e.:

    20180724_F1/raw/<only raw images for this flight>
    20180724_F2/raw/<same>

Within each folder run `calc_rad2refl.py` and then `process_flight_images.py`.

Then merge refl back into a new single folder:
    
    20180724/refl/

and now run `sort_images.py`.



##### PhotoScan operating procedure

Remember that in PhotoScan speak, 'camera' equals viewing location.

Import using Workflow -> Add Folder. Select 'Create multispectral cameras from folders as bands'.

Photos will probably appear to have blown highlights when imported. To fix, in the Workspace pane right-click the Chunk then select Set Brightness... option.

Aim for at least 10 projections of each GCP. This probably won't be possible for GCPs located towards the edges of the flight area. Also, don't insist on this - if image quality is too poor to resolve GCP well then don't bother.

Set GCP Z accuracy to 20 metres to minimise their importance in solving the DEM solution - as the GCPs were not placed with accurate Z positioning in mind.

Identify the first 3-4 GCPs then run Optimise Cameras. This will auto-place subsequent estimated GCPs very near their ground targets, speeding up the process.

Open the orthomosaic and check each band separately for blown exposure. If  blown patches then follow the instructions for removing 'purple fringes' in the USGS instructions. 

Orthomosaic export: Untick alpha channel export (other GDAL, QGIS etc don't understand the format).




##### Using gdalwarp

Take care with reprojecting using gdalwarp. Even with bilinear interpolation, noise seems to be introduced that can be visible when differencing broadband albedo products. Better to export with correct projection directly out of photoscan. gdalwarp is still ok to use to crop to common grid area, though.


##### Pyramids for visualisation

Build pyramids prior to visualisation in QGIS:

    gdaladdo -clean uav_20170724_refl_5cm.tif
    gdaladdo -r average -ro --config USE_RRD NO --config TILED YES --config GDAL_CACHEMAX 10240 uav_20170724_refl_5cm.tif 2 4 8 16

(see also https://www.northrivergeographic.com/archives/pyramid-layers-qgis-arcgis)


##### Notes from 2017 processing

* Gradual selection: hit Level=10 in most cases. Did not go below this.
* Projection accuracy: all scenes are <=3.
* Tie-point accuracy: 0.3-0.5
* Reprojection error: .3.

All GCPs used in all scenes, except:

* 2017-07-21: GCP10 removed as it was obscured by GPS antenna logging its position at time of survey.
* 2017-07-24: GCP3 removed as GCP had come out of the ice.



### Classification

1. Optionally: execute `IceSurfClassifiers/classify_msrededge.py`, `classify_sentinel2.py` to train the model.
2. Execute `IceSurfClassifiers/predict_msrededge.py`, `predict_sentinel2.py`. If training the model afresh rather than using an existing model then update the model pkl filename first.



### Analysis and plotting

#### Helper scripts

* `load_s2_data.py`
* `load_ground_data.py`
* `load_uav_data.py`


#### Statistics, etc

* Topographic and hydrologic controls: 
    - `detrend_uav_dems.py` - run twice for 2017-07-21 data, (1) to detrend the surface for to enable calculation of local roughness statistics quoted in manuscript text, and (2) using a smaller window size in order to create a 'blurred' surface from which to calculate slope angle.
    - `detrend_uav2018.py` - specific to UPE DEM, run twice as above.
    - `calculate_slope_angle.py` - uses output (2) of `detrend_uav_dems.py`
* MODIS albedo change pixel-by-pixel: `examine_modis_sinusoidal.py`


#### Energy balance modelling

* S6: `ebmodel_2017.py`
* UPE: `run_ebmodel_upeu.py`
* MODIS sensitivity to albedo: `run_ebmodel_albedos.py`


#### Figures and Tables

* Fig. 1: `plot_s6_upe_comparison.py`
* Fig. 2: `plot_upe_elev.py`
* Fig. 3: `plot_s6_wc_examples.py`
* Fig. 4: `plot_uav_proportional_coverage.py`
* Fig. 5: `plot_alb_energy_ts.py`
* Figs. 6 & 7: `plot_s2_class_albedo_rasters.py`, which calls `compare_uav_s2.py`
* Fig. 8: `plot_s2_vs_modis.py`
* Fig. A1: `plot_confusion_matrices.py` (matrices were manually copied into this script from logfiles output during the classification process)
* Table 1: `plot_s2_class_albedo_rasters.py`
* Table B1: `calculate_modis_acquisition_times.py`



## Environment configuration
The scripts were executed in a miniconda environment with the following configuration:

``` 
# Name                    Version                   Build  Channel
affine                    2.2.1                      py_0    conda-forge
appdirs                   1.4.3                      py_1    conda-forge
asn1crypto                0.24.0                   py35_3    conda-forge
attrs                     18.2.0                     py_0    conda-forge
backcall                  0.1.0                      py_0    conda-forge
blas                      1.1                    openblas    conda-forge
bleach                    3.0.2                    pypi_0    pypi
bokeh                     0.13.0                   py35_0    conda-forge
boost-cpp                 1.67.0               h3a22d5f_0    conda-forge
boto3                     1.9.49                     py_0    conda-forge
botocore                  1.12.50                    py_0    conda-forge
bottleneck                1.2.1            py35h7eb728f_1    conda-forge
bzip2                     1.0.6                h470a237_2    conda-forge
ca-certificates           2018.10.15           ha4d7672_0    conda-forge
cairo                     1.14.12              he6fea26_5    conda-forge
cartopy                   0.16.0           py35h81b52dc_2    conda-forge
certifi                   2018.8.24             py35_1001    conda-forge
cffi                      1.11.5           py35h5e8e0c9_1    conda-forge
cftime                    1.0.1            py35h7eb728f_0    conda-forge
chardet                   3.0.4                    py35_3    conda-forge
click                     7.0                        py_0    conda-forge
click-plugins             1.0.4                      py_0    conda-forge
cligj                     0.5.0                      py_0    conda-forge
cloudpickle               0.6.1                      py_0    conda-forge
croissance                1.1.0                    pypi_0    pypi
cryptography              2.3.1            py35hdffb7b8_0    conda-forge
cryptography-vectors      2.3.1                    py35_0    conda-forge
curl                      7.62.0               h74213dd_0    conda-forge
cycler                    0.10.0                     py_1    conda-forge
cython                    0.28.5           py35hfc679d8_0    conda-forge
cytoolz                   0.9.0.1          py35h470a237_0    conda-forge
dask                      0.19.2                     py_0    conda-forge
dask-core                 0.19.2                     py_0    conda-forge
dbus                      1.13.0               h3a4f0e9_0    conda-forge
decorator                 4.3.0                      py_0    conda-forge
descartes                 1.1.0                      py_2    conda-forge
distributed               1.23.2                   py35_1    conda-forge
docutils                  0.14                     py35_1    conda-forge
entrypoints               0.2.3                    py35_2    conda-forge
expat                     2.2.5                hfc679d8_2    conda-forge
faceted                   0.1                      pypi_0    pypi
ffmpeg                    4.0.2                ha0c5888_2    conda-forge
fiona                     1.7.13           py35hb00a9d7_3    conda-forge
fontconfig                2.13.1               h65d0f4c_0    conda-forge
freetype                  2.9.1                h6debe1e_4    conda-forge
freexl                    1.0.5                h470a237_2    conda-forge
future                    0.17.1                   pypi_0    pypi
gdal                      2.2.4            py35hb00a9d7_9    conda-forge
geographiclib             1.49                     pypi_0    pypi
geopandas                 0.4.0                      py_1    conda-forge
geopy                     1.17.0                   pypi_0    pypi
geos                      3.6.2                hfc679d8_3    conda-forge
geotiff                   1.4.2                h700e5ad_5    conda-forge
gettext                   0.19.8.1             h5e8e0c9_1    conda-forge
giflib                    5.1.4                h470a237_1    conda-forge
glib                      2.55.0               h464dc38_2    conda-forge
gmp                       6.1.2                hfc679d8_0    conda-forge
gnutls                    3.5.19               h2a4e5f8_1    conda-forge
graphite2                 1.3.12               hfc679d8_1    conda-forge
gst-plugins-base          1.12.5               hde13a9d_0    conda-forge
gstreamer                 1.12.5               h61a6719_0    conda-forge
h5netcdf                  0.6.2                      py_0    conda-forge
h5py                      2.8.0            py35h7eb728f_2    conda-forge
harfbuzz                  1.9.0                h08d66d9_0    conda-forge
hdf4                      4.2.13               h951d187_2    conda-forge
hdf5                      1.10.2               hc401514_2    conda-forge
heapdict                  1.0.0                 py35_1000    conda-forge
icu                       58.2                 hfc679d8_0    conda-forge
idna                      2.7                      py35_2    conda-forge
imageio                   2.3.0                      py_1    conda-forge
intake                    0.2.9                      py_0    conda-forge
intel-openmp              2019.0                      118  
ipykernel                 5.1.0              pyh24bf2e0_0    conda-forge
ipython                   7.0.1            py35h24bf2e0_0    conda-forge
ipython_genutils          0.2.0                      py_1    conda-forge
ipywidgets                7.4.2                      py_0    conda-forge
jasper                    1.900.1              hff1ad4c_5    conda-forge
jedi                      0.12.1                   py35_0    conda-forge
jinja2                    2.10                       py_1    conda-forge
jmespath                  0.9.3                      py_1    conda-forge
joblib                    0.13.0                     py_0    conda-forge
jpeg                      9c                   h470a237_1    conda-forge
json-c                    0.12.1               h470a237_1    conda-forge
jsonschema                2.6.0                    py35_2    conda-forge
jupyter                   1.0.0                      py_1    conda-forge
jupyter_client            5.2.3                      py_1    conda-forge
jupyter_console           6.0.0                      py_0    conda-forge
jupyter_core              4.4.0                      py_0    conda-forge
kealib                    1.4.9                h0bee7d0_2    conda-forge
kiwisolver                1.0.1            py35h2d50403_2    conda-forge
krb5                      1.16.2               hbb41f41_0    conda-forge
libcurl                   7.62.0               hbdb9355_0    conda-forge
libdap4                   3.19.1               h8fe5423_1    conda-forge
libedit                   3.1.20170329         haf1bffa_1    conda-forge
libffi                    3.2.1                hfc679d8_5    conda-forge
libgcc-ng                 7.2.0                hdf63c60_3    conda-forge
libgdal                   2.2.4                hbd6f514_9    conda-forge
libgfortran               3.0.0                         1    conda-forge
libgfortran-ng            7.2.0                hdf63c60_3    conda-forge
libiconv                  1.15                 h470a237_3    conda-forge
libkml                    1.3.0                hccc92b1_8    conda-forge
libnetcdf                 4.6.1              h628ed10_200    conda-forge
libopenblas               0.2.20               h9ac9557_7  
libpng                    1.6.35               ha92aebf_2    conda-forge
libpq                     10.5                 he29860b_0    conda-forge
libsodium                 1.0.16               h470a237_1    conda-forge
libspatialindex           1.8.5                hfc679d8_3    conda-forge
libspatialite             4.3.0a              hdfcc80b_23    conda-forge
libssh2                   1.8.0                h5b517e9_2    conda-forge
libstdcxx-ng              7.2.0                hdf63c60_3    conda-forge
libtiff                   4.0.9                he6b73bb_2    conda-forge
libuuid                   2.32.1               h470a237_2    conda-forge
libwebp                   0.5.2                         7    conda-forge
libxcb                    1.13                 h470a237_2    conda-forge
libxml2                   2.9.8                h422b904_5    conda-forge
libxslt                   1.1.32               h88dbc4e_2    conda-forge
locket                    0.2.0                      py_2    conda-forge
lxml                      4.2.5            py35hc9114bc_0    conda-forge
markupsafe                1.0              py35h470a237_1    conda-forge
matplotlib                2.2.3            py35h8e2386c_0    conda-forge
mistune                   0.8.3            py35h470a237_2    conda-forge
mkl                       2018.0.3                      1  
mkl_fft                   1.0.6                    py35_0    conda-forge
mkl_random                1.0.1                    py35_0    conda-forge
msgpack-numpy             0.4.4.1                    py_0    conda-forge
msgpack-python            0.5.6            py35h2d50403_3    conda-forge
munch                     2.3.2                      py_0    conda-forge
nbconvert                 5.3.1                      py_1    conda-forge
nbformat                  4.4.0                      py_1    conda-forge
ncurses                   6.1                  hfc679d8_1    conda-forge
netcdf-fortran            4.4.4                h4363f12_9    conda-forge
netcdf4                   1.4.1            py35h62672b6_0    conda-forge
nettle                    3.3                           0    conda-forge
networkx                  2.2                        py_1    conda-forge
notebook                  5.7.0                    py35_0    conda-forge
numpy                     1.15.1          py35_blas_openblashd3ea46f_0  [blas_openblas]  conda-forge
numpy-base                1.14.3           py35h0ea5e3f_1  
olefile                   0.46                       py_0    conda-forge
openblas                  0.2.20                        8    conda-forge
opencv                    3.4.1           py35_blas_openblash829a850_201  [blas_openblas]  conda-forge
openh264                  1.8.0                hd28b015_0    conda-forge
openjpeg                  2.3.0                h0e734dc_3    conda-forge
openssl                   1.0.2p               h470a237_1    conda-forge
owslib                    0.17.0                     py_0    conda-forge
packaging                 18.0                       py_0    conda-forge
pandas                    0.23.4           py35hf8a1672_0    conda-forge
pandoc                    2.3.1                         0    conda-forge
pandocfilters             1.4.2                      py_1    conda-forge
parso                     0.3.1                      py_0    conda-forge
partd                     0.3.9                      py_0    conda-forge
patsy                     0.5.1                      py_0    conda-forge
pcre                      8.41                 hfc679d8_3    conda-forge
pexpect                   4.6.0                    py35_0    conda-forge
pickleshare               0.7.5                    py35_0    conda-forge
pillow                    5.3.0            py35hc736899_0    conda-forge
pip                       18.0                  py35_1001    conda-forge
pixman                    0.34.0               h470a237_3    conda-forge
poppler                   0.67.0               h4d7e492_3    conda-forge
poppler-data              0.4.9                         0    conda-forge
postgresql                10.5                 h66035e0_0    conda-forge
proj4                     4.9.3                h470a237_8    conda-forge
prometheus_client         0.4.2                      py_0    conda-forge
prompt_toolkit            2.0.7                      py_0    conda-forge
psutil                    5.4.7            py35h470a237_1    conda-forge
psycopg2                  2.7.5            py35hdffb7b8_2    conda-forge
pthread-stubs             0.4                  h470a237_1    conda-forge
ptyprocess                0.6.0                 py35_1000    conda-forge
pycparser                 2.19                       py_0    conda-forge
pydem                     0.1.1                    pypi_0    pypi
pyepsg                    0.3.2                      py_1    conda-forge
pygments                  2.2.0                      py_1    conda-forge
pymodis                   2.0.9                    pypi_0    pypi
pyopenssl                 18.0.0                   py35_0    conda-forge
pyparsing                 2.3.0                      py_0    conda-forge
pyproj                    1.9.5.1          py35h508ed2a_5    conda-forge
pyqt                      5.6.0            py35h8210e8a_7    conda-forge
pysal                     1.14.4.post2             py35_0    conda-forge
pyshp                     2.0.0                      py_0    conda-forge
pysocks                   1.6.8                    py35_2    conda-forge
python                    3.5.5                h5001a0f_2    conda-forge
python-dateutil           2.7.5                      py_0    conda-forge
python-snappy             0.5.3            py35h00d4201_0    conda-forge
pytz                      2018.7                     py_0    conda-forge
pywavelets                1.0.1            py35h7eb728f_0    conda-forge
pyyaml                    3.13             py35h470a237_1    conda-forge
pyzmq                     17.1.2           py35hae99301_0    conda-forge
qt                        5.6.2                hf70d934_9    conda-forge
qtconsole                 4.4.2                      py_1    conda-forge
rasterio                  1.0.7            py35h1b5fcde_0    conda-forge
readline                  7.0                  haf1bffa_1    conda-forge
requests                  2.19.1                   py35_1    conda-forge
richdem                   0.3.4                    pypi_0    pypi
rtree                     0.8.3                    py35_0    conda-forge
ruamel.yaml               0.15.71          py35h470a237_0    conda-forge
s3transfer                0.1.13                   py35_1    conda-forge
salem                     0.2.2                    pypi_0    pypi
scikit-image              0.14.0           py35hfc679d8_1    conda-forge
scikit-learn              0.19.2          py35_blas_openblasha84fab4_201  [blas_openblas]  conda-forge
scipy                     1.1.0           py35_blas_openblash7943236_201  [blas_openblas]  conda-forge
seaborn                   0.9.0                      py_0    conda-forge
send2trash                1.5.0                      py_0    conda-forge
setuptools                40.4.3                   py35_0    conda-forge
shapely                   1.6.4            py35h164cb2d_1    conda-forge
simplegeneric             0.8.1                      py_1    conda-forge
sip                       4.18.1           py35hfc679d8_0    conda-forge
six                       1.11.0                   py35_1    conda-forge
sklearn-xarray            0.3.0                    pypi_0    pypi
snappy                    1.1.7                hfc679d8_2    conda-forge
snuggs                    1.4.1                      py_1    conda-forge
sortedcontainers          2.0.5                      py_0    conda-forge
sqlalchemy                1.2.12           py35h470a237_0    conda-forge
sqlite                    3.25.3               hb1c47c0_0    conda-forge
statsmodels               0.9.0                    py35_0    conda-forge
tblib                     1.3.2                      py_1    conda-forge
terminado                 0.8.1                    py35_1    conda-forge
testpath                  0.3.1                    py35_1    conda-forge
tk                        8.6.8                ha92aebf_0    conda-forge
toolz                     0.9.0                      py_1    conda-forge
tornado                   5.1.1            py35h470a237_0    conda-forge
tqdm                      4.31.1                   pypi_0    pypi
traitlets                 4.3.2                    py35_0    conda-forge
traits                    4.6.0                    pypi_0    pypi
urllib3                   1.23                     py35_1    conda-forge
wcwidth                   0.1.7                      py_1    conda-forge
webencodings              0.5.1                    pypi_0    pypi
wheel                     0.32.0                py35_1000    conda-forge
widgetsnbextension        3.4.2                    py35_0    conda-forge
x264                      1!152.20180717       h470a237_1    conda-forge
xarray                    0.10.9                   py35_0    conda-forge
xerces-c                  3.2.0                h5d6a6da_2    conda-forge
xlrd                      1.1.0                      py_2    conda-forge
xorg-kbproto              1.0.7                h470a237_2    conda-forge
xorg-libice               1.0.9                h470a237_4    conda-forge
xorg-libsm                1.2.3                h8c8a85c_0    conda-forge
xorg-libx11               1.6.6                h470a237_0    conda-forge
xorg-libxau               1.0.8                h470a237_6    conda-forge
xorg-libxdmcp             1.1.2                h470a237_7    conda-forge
xorg-libxext              1.3.3                h470a237_4    conda-forge
xorg-libxrender           0.9.10               h470a237_2    conda-forge
xorg-renderproto          0.11.1               h470a237_2    conda-forge
xorg-xextproto            7.3.0                h470a237_2    conda-forge
xorg-xproto               7.0.31               h470a237_7    conda-forge
xz                        5.2.4                h470a237_1    conda-forge
yaml                      0.1.7                h470a237_1    conda-forge
zeromq                    4.2.5                hfc679d8_6    conda-forge
zict                      0.1.3                      py_0    conda-forge
zlib                      1.2.11               h470a237_3    conda-forge
```

However, scripts which relied on Micasense's `imageprocessing` repository required different dependencies and so were excecuted in the following environment:

```
# Name                    Version                   Build  Channel
backports                 1.0                      py35_1    conda-forge
backports.functools_lru_cache 1.4                      py35_1    conda-forge
blas                      1.1                    openblas    conda-forge
bzip2                     1.0.6                         1    conda-forge
ca-certificates           2017.7.27.1                   0    conda-forge
cairo                     1.14.6                        5    conda-forge
certifi                   2017.7.27.1              py35_0    conda-forge
cycler                    0.10.0                   py35_0    conda-forge
dbus                      1.10.22                       0    conda-forge
decorator                 4.1.2                    py35_0    conda-forge
et_xmlfile                1.0.1                    py35_0    conda-forge
expat                     2.2.1                         0    conda-forge
ffmpeg                    3.2.4                         1    conda-forge
fontconfig                2.12.1                        5    conda-forge
freetype                  2.7                           2    conda-forge
gettext                   0.19.7                        1    conda-forge
giflib                    5.1.4                         0    conda-forge
glib                      2.51.4                        0    conda-forge
gst-plugins-base          1.8.0                         0    conda-forge
gstreamer                 1.8.0                         2    conda-forge
harfbuzz                  1.3.4                         2    conda-forge
hdf5                      1.8.18                        2    conda-forge
icu                       58.1                          1    conda-forge
ipython                   5.3.0                    py35_0    conda-forge
ipython_genutils          0.2.0                    py35_0    conda-forge
jasper                    1.900.1                       4    conda-forge
jdcal                     1.3                      py35_0    conda-forge
jedi                      0.10.2                   py35_0    conda-forge
jpeg                      9b                            2    conda-forge
libffi                    3.2.1                         3    conda-forge
libgfortran               3.0.0                         1  
libiconv                  1.14                          4    conda-forge
libpng                    1.6.28                        2    conda-forge
libtiff                   0.4.1                    pypi_0    pypi
libwebp                   0.5.2                         7    conda-forge
libxcb                    1.12                          1    conda-forge
libxml2                   2.9.5                         1    conda-forge
matplotlib                2.1.0                    py35_1    conda-forge
ncurses                   5.9                          10    conda-forge
numpy                     1.13.3          py35_blas_openblas_200  [blas_openblas]  conda-forge
olefile                   0.44                     py35_0    conda-forge
openblas                  0.2.19                        2    conda-forge
opencv                    3.3.0           py35_blas_openblas_200  [blas_openblas]  conda-forge
openpyxl                  2.5.1                    py35_0    conda-forge
openssl                   1.0.2l                        0    conda-forge
pandas                    0.21.0                   py35_0    conda-forge
patsy                     0.4.1                    py35_0    conda-forge
pcre                      8.39                          0    conda-forge
pexpect                   4.2.1                    py35_0    conda-forge
pickleshare               0.7.4                    py35_0    conda-forge
piexif                    1.0.13                   pypi_0    pypi
pillow                    4.3.0                    py35_1    conda-forge
pip                       9.0.1                    py35_0    conda-forge
pixman                    0.34.0                        0    conda-forge
prompt_toolkit            1.0.15                   py35_0    conda-forge
ptyprocess                0.5.2                    py35_0    conda-forge
pyexiftool                0.1                      pypi_0    pypi
pygments                  2.2.0                    py35_0    conda-forge
pyparsing                 2.2.0                    py35_0    conda-forge
pyqt                      5.6.0                    py35_4    conda-forge
python                    3.5.4                         1    conda-forge
python-dateutil           2.6.1                    py35_0    conda-forge
pytz                      2017.3                     py_1    conda-forge
qt                        5.6.2                         3    conda-forge
readline                  6.2                           0    conda-forge
scipy                     0.19.1          py35_blas_openblas_202  [blas_openblas]  conda-forge
setuptools                36.6.0                   py35_1    conda-forge
simplegeneric             0.8.1                    py35_0    conda-forge
sip                       4.18                     py35_1    conda-forge
six                       1.11.0                   py35_1    conda-forge
sqlite                    3.13.0                        1    conda-forge
statsmodels               0.8.0                    py35_0    conda-forge
tifffile                  0.12.1                   pypi_0    pypi
tk                        8.5.19                        2    conda-forge
tornado                   4.5.2                    py35_0    conda-forge
traitlets                 4.3.2                    py35_0    conda-forge
wcwidth                   0.1.7                    py35_0    conda-forge
wheel                     0.30.0                     py_1    conda-forge
x264                      20131217                      3    conda-forge
xorg-libxau               1.0.8                         3    conda-forge
xorg-libxdmcp             1.1.2                         3    conda-forge
xz                        5.2.3                         0    conda-forge
zlib                      1.2.11                        0    conda-forge
```