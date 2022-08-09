"""create a multi-band GeoTIFF from all the spectral bands with a resolution of
20m of a Sentinel-2 level 2A tile from any practical TOI (2020 - 2022), clipped to the
extent of the AOI."""

"""a. Download the Satellite data using a RESTful API or equivalent python library;"""

import os
import config
from osgeo import gdal
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt


# create download directory if not exist
download_dir = "download/"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Enter username and password from config file
api = SentinelAPI(config.user, config.password, 'https://scihub.copernicus.eu/dhus')

# api.download('805249e2-fc03-4e77-94eb-91312659b757', download_dir)

# search by polygon, time, and SciHub query keywords
aoi = geojson_to_wkt(read_geojson('aoi/AOI_extent.geojson'))

products = api.query(aoi,
                     date=('20220720', '20220721'),
                     platformname='Sentinel-2',
                     producttype='S2MSI2A')


# download all results from the search
api.download_all(products, download_dir)
