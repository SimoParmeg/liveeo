"""b. Mask unusable data with the Sentinel-2 SCL layer - Please convert all values of the
S-2 spectral bands to nodata/NA values for which there are NO_DATA,
SATURATED_OR_DEFECTIVE, CLOUD_HIGH_PROBABILITY values in the S-2 SCL layer;"""

import os
import geopandas as gpd
import raster_clip as rc
from osgeo import gdal

# S2A_MSIL2A CLASSIFICATION LINK:
# https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/level-2a/algorithm

# create output directory if not exist
download_dir = "output/"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

in_fn = "aoi/AOI_extent.geojson"
aoi = gpd.read_file(in_fn)
# print(aoi.crs)
aoi_reproj = aoi.to_crs(32633)  # Inserted SRS manually to save time, this should be imported from raster's attributes
# print(aoi_reproj.crs)
aoi_reproj.to_file("aoi/AOI_extent_reproj.geojson", driver='GeoJSON')

path = "download/S2A_MSIL2A_20220720T101611_N0400_R065_T33UUU_20220720T164302.SAFE/GRANULE/L2A_T33UUU_A036956_20220720T101819/IMG_DATA/R20m/"
scl = f"{path}T33UUU_20220720T101611_SCL_20m.jp2"
b01 = f"{path}T33UUU_20220720T101611_B01_20m.jp2"  # Coastal aerosol
b02 = f"{path}T33UUU_20220720T101611_B02_20m.jp2"  # Blue
b03 = f"{path}T33UUU_20220720T101611_B03_20m.jp2"  # Green
b04 = f"{path}T33UUU_20220720T101611_B04_20m.jp2"  # Red
b05 = f"{path}T33UUU_20220720T101611_B05_20m.jp2"  # Vegetation Red Edge
b06 = f"{path}T33UUU_20220720T101611_B06_20m.jp2"  # Vegetation Red Edge
b07 = f"{path}T33UUU_20220720T101611_B07_20m.jp2"  # Vegetation Red Edge
b8a = f"{path}T33UUU_20220720T101611_B8A_20m.jp2"  # Vegetation Red Edge
b11 = f"{path}T33UUU_20220720T101611_B11_20m.jp2"  # Short wave infrared SWIR
b12 = f"{path}T33UUU_20220720T101611_B12_20m.jp2"  # Short wave infrared SWIR
band_list = [scl, b01, b02, b03, b04, b05, b06, b07, b8a, b11, b12]

nodata = 0
saturated_or_defective = 1
cloud_high_prob = 9

# CLIPPING ALL BANDS WITH AOI
bands = []
for band in band_list:
    print(f"clipping {band[-11:]}")
    out_band_path = 'output/' + band[-11:-4] + '_masked.tif'
    rc.raster_clip("aoi/AOI_extent_reproj.geojson", band, out_band_path)
    bands.append(out_band_path)

bands.pop(0)  # POP SCL To have only bands in list

"""c. Store the resultant image as a multiband Geotiff."""
# REFERENCE https://www.satimagingcorp.com/satellite-sensors/other-satellite-sensors/sentinel-2a/
# RGB / Nat colors -> BO4 (Red) - B03 (Green) - B02 (Blue)
# False color -> B06 (Infrared) - B04(Red) - B03(Green)
band1_fn = bands[3]

# OPEN BAND 1 and CREATE MULTIBAND RASTER
in_ds = gdal.Open(band1_fn)
in_band = in_ds.GetRasterBand(1)

# CREATE A THREE BAND GEOTIFF WITH THE SAME PROPERTIES OF THE BAND 1
gtiff_driver = gdal.GetDriverByName('GTiff')
out_ds = gtiff_driver.Create('output/multiband.tif',  # filename
                             in_band.XSize,  # xsize (number of columns)
                             in_band.YSize,  # ysize (number of rows)
                             len(bands),  # number of bands
                             in_band.DataType)  # data type

out_ds.SetProjection(in_ds.GetProjection())
out_ds.SetGeoTransform(in_ds.GetGeoTransform())
#  WRITE BAND 1 (RED)
out_ds.GetRasterBand(1).WriteArray(gdal.Open(band1_fn).ReadAsArray())

# WRITE BAND 2 (GREEN)
band2_fn = bands[2]
out_ds.GetRasterBand(2).WriteArray(gdal.Open(band2_fn).ReadAsArray())

# WRITE BAND 3 (BLUE)
band3_fn = bands[1]
out_ds.GetRasterBand(3).WriteArray(gdal.Open(band3_fn).ReadAsArray())

# WRITE INFRARED BANDS (B05, B06, B07, B8A)
band4_fn = bands[4]
out_ds.GetRasterBand(4).WriteArray(gdal.Open(band4_fn).ReadAsArray())
band5_fn = bands[5]
out_ds.GetRasterBand(5).WriteArray(gdal.Open(band5_fn).ReadAsArray())
band6_fn = bands[6]
out_ds.GetRasterBand(6).WriteArray(gdal.Open(band6_fn).ReadAsArray())
band7_fn = bands[7]
out_ds.GetRasterBand(7).WriteArray(gdal.Open(band7_fn).ReadAsArray())

# WRITE SWIR BANDS (B11, B12)
band8_fn = bands[8]
out_ds.GetRasterBand(8).WriteArray(gdal.Open(band8_fn).ReadAsArray())
band9_fn = bands[9]
out_ds.GetRasterBand(9).WriteArray(gdal.Open(band9_fn).ReadAsArray())

# WRITE COASTAL AEROSOL BAND (B01)
band10_fn = bands[0]
out_ds.GetRasterBand(10).WriteArray(gdal.Open(band10_fn).ReadAsArray())

# COMPUTE STATISTICS ON EACH OUTPUT BAND
out_ds.FlushCache()
for i in range(1, 11):
    out_ds.GetRasterBand(i).ComputeStatistics(False)

# BUILD OVERVIEWS (PYRAMIDS)
out_ds.BuildOverviews('average', [2, 4, 8, 16, 32])

del out_ds
