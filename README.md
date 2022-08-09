# Initial Setup
Remote Sensing Engineer Challenge for Liveeo recruitment process

Download the project into a known folder, then open a Linux terminal (ctrl+alt+T) and switch to the script folder you downloaded data. Then you're ready to create your conda virtual environment with all the required libraries:

conda create -y --name testenv python=3.8

conda install --force-reinstall -y -q --name testenv -c conda-forge --file requirements.txt

## outputs:

as requested, a multiband .tif containing all the bands from Sentinel2 data

Natural Color .tif with RGB bands
False Color .tif with near-infrared band
Scl .tif with classification based on sentinel color scale (https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/level-2a/algorithm)
