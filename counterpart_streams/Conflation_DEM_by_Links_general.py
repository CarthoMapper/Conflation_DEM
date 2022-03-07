import geopandas as gpd
import shutil
from osgeo import gdal
from qgis import processing
from epsg_ident import EpsgIdent

def pixel(dx, dy, gt):
    px = gt[0]
    py = gt[3]
    rx = gt[1]
    ry = gt[5]
    x = round((dx - px)/rx)
    y = round((dy - py)/ry)
    return x,y

def conflate_dem_by_links(dem_path, rivers, links, distance, filter, output_dem):

    dem = gdal.Open(dem_path)
    gt = dem.GetGeoTransform()
    pixelSize = gt[1]
    temp_dem = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/temp_dem5.tif"
    buffer_z = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/buffer_zone5.shp"
    buffer_zone = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/buffer_densify.shp"
    processing.run("qgis:buffer", {'INPUT': rivers,
                                        'DISTANCE': distance,
                                        'SEGMENTS': 5,
                                        'DISSOLVE': True,
                                        'END_CAP_STYLE': 0,
                                        'JOIN_STYLE': 0,
                                        'OUTPUT': buffer_z})
    processing.run("qgis:densifygeometriesgivenaninterval",
                   {'INPUT': buffer_z, 'INTERVAL': pixelSize, 'OUTPUT': buffer_zone})


    links = gpd.read_file(links)
    n = links.shape[0]

    gcp_list = []
    pixels = set()
    coords = set()

    buffer_zone = gpd.read_file(buffer_zone)
    buffer_zone = buffer_zone.iloc[[0]]
    buffer_zone = buffer_zone.copy()
    buffer_zone = buffer_zone.apply(lambda p : p['geometry'], axis=1)
    buffer_zone = buffer_zone[0]

    i = 0
    while i<n:
        links_coords = links.iloc[[i]]
        links_coords = links_coords.copy()
        links_coords = links_coords.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
        links_coords = links_coords.to_list()
        links_coords = links_coords[0]
        links_coords0 = links_coords[0]
        links_coords1 = links_coords[1]
        x = round(links_coords1[0], 3)
        y = round(links_coords1[1], 3)

        xy = (x, y)

        px = pixel(links_coords0[0], links_coords0[1], gt)
        if (not px in pixels) and (not xy in coords):
            pixels.add(px)
            coords.add(xy)
            gcp = gdal.GCP(xy[0], xy[1], 0, px[0], px[1])
            gcp_list.append(gcp)
        i+=filter
    k = len(buffer_zone)
    pixels_buf = set()
    coords_buf = set()
    i = 0

    for pol in range(k):
        coord = list(buffer_zone[pol].exterior.coords)
        j = (len(coord))
        while i<j:
            x = round(coord[i][0], 3)
            y = round(coord[i][1], 3)
            xy_buf = (x, y)
            px = pixel(x, y, gt)
            if (not px in pixels_buf) and (not xy_buf in coords_buf):
                pixels_buf.add(px)
                coords_buf.add(xy_buf)
                gcp = gdal.GCP(xy_buf[0], xy_buf[1], 0, px[0], px[1])
                gcp_list.append(gcp)
            i+= filter

    shutil.copy(dem_path, temp_dem)
    ds = gdal.Open(temp_dem, gdal.GA_Update)
    wkt = ds.GetProjection()
    ds.SetGCPs(gcp_list, wkt)
    gdal.Warp(output_dem, ds, options=gdal.WarpOptions(dstSRS='EPSG:32662',
                                                       format='gtiff', tps=True,
                                                       multithread=True))
    ds = None
    return output_dem
