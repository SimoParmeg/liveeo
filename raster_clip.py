import fiona
import rasterio, rasterio.mask

def raster_clip(in_geojson, in_file, out_file,):
    """This function take a geojson as parameter and clips a raster, saving the clipped image to
    a given path. the 2 files in input must have same CRS in order to work properly"""
    with fiona.open(in_geojson, "r") as geojson:
        shapes = [feature["geometry"] for feature in geojson]

    with rasterio.open(in_file) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta

    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    with rasterio.open(out_file, "w", **out_meta) as dest:
        dest.write(out_image)