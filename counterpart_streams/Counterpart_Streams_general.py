import geopandas as gpd
import numpy as np
from .WBT.whitebox_tools import WhiteboxTools
from osgeo import gdal
from qgis import processing
import os


def linestring_to_points(line, i, j):
   return line.coords[i][j]
def extract_point(input, i):
    layer = input.copy()
    layer['x'] = layer.apply(lambda l: linestring_to_points(l['geometry'], i, 0), axis=1)
    layer['y'] = layer.apply(lambda l: linestring_to_points(l['geometry'], i, 1), axis=1)
    layer['geometry'] = gpd.points_from_xy(layer['x'], layer['y'])
    layer = layer.drop(columns=['x', 'y'])
    return layer

def counterpart_streams(dem, streams, field, dist, acc_mask_filter, counterpart_vectors):



    rivers = gpd.read_file(streams)

    wbt = WhiteboxTools()
    wbt.set_whitebox_dir('/Users/vital/Desktop/Kursovaya/WTB_general_script/WBT')
    wbt.set_verbose_mode(False)



    fill = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/fill.tif"
    wbt.fill_depressions(dem, fill)

    dir = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/dir.tif"
    wbt.d8_pointer(fill, dir)

    acc = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/acc.tif"
    wbt.d8_flow_accumulation(dir, acc, pntr=True)

    river = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/river.shp"
    raster_rivers = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/raster_rivers.tif"
    euc_dist = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/euc_dist.tif"
    euc_dist_filter = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/euc_dist_filter.tif"
    divided_euc_dist = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/divided_euc_dist.tif"
    acc_mask = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/acc_mask.tif"
    multiplied_acc_mask = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/multiplied_acc_mask.tif"
    divided_fill = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/divided_fill.tif"
    added_euc_dist = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/added_euc_dist.tif"
    added_fill = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/added_fill.tif"
    first_multiply = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/first_multiply.tif"
    cost = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/cost.tif"
    vector_source = 'C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/vector_source.shp'
    vector_destination = 'C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/vector_destination.shp'
    raster_source = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/raster_source.tif"
    raster_destination = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/raster_destination.tif"
    accum = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/accum.tif"
    backlink = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/backlink.tif"
    counterpart_streams = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/counterpart_streams.tif"
    counterpart_vector = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/counterpart_vector.shp"
    counterpart_temp = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/counterpart_temp.shp"
    count_densify = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/count_densify.shp"


    n = rivers.shape[0]

    raster = gdal.Open(dem)
    band = raster.GetRasterBand(1)
    npband = np.array(band.ReadAsArray())
    npcount = np.zeros((n, npband.shape[0], npband.shape[1]))


    print(npband)


    filter_minus_one = acc_mask_filter - 1

    vals = []

    for i in range(n):

        rivers.iloc[[i]].to_file(river)

        wbt.rasterize_streams(river, fill, raster_rivers, nodata=False, feature_id=False)

        wbt.euclidean_distance(raster_rivers, euc_dist)

        wbt.less_than(euc_dist, dist, euc_dist_filter, incl_equals=False)

        wbt.divide(euc_dist, euc_dist_filter, euc_dist)

        wbt.divide(euc_dist, 1000, divided_euc_dist)

        wbt.less_than(acc, acc_mask_filter, acc_mask, incl_equals=False)

        wbt.multiply(acc_mask, filter_minus_one, multiplied_acc_mask)

        wbt.add(multiplied_acc_mask, 1, acc_mask)

        wbt.divide(fill, 1000, divided_fill)

        wbt.add(divided_euc_dist, 1, added_euc_dist)

        wbt.add(divided_fill, 1, added_fill)

        wbt.multiply(acc_mask, added_euc_dist, first_multiply)

        wbt.multiply(first_multiply, added_fill, cost)

        df_source = extract_point(rivers.iloc[[i]], -1)
        df_destination = extract_point(rivers.iloc[[i]], 0)
        df_source.to_file(vector_source)
        df_destination.to_file(vector_destination)
        wbt.vector_points_to_raster(vector_source, raster_source, field="FID", assign='last', nodata=False, base=fill)
        wbt.vector_points_to_raster(vector_destination, raster_destination, field="FID", assign='last', nodata=False,
                                    base=fill)

        wbt.cost_distance(raster_source, cost, accum, backlink)
        wbt.cost_pathway(raster_destination, backlink, counterpart_streams)
        wbt.raster_streams_to_vector(counterpart_streams, backlink, counterpart_vector, esri_pntr=False)

        cont = gpd.read_file(counterpart_vector)

        cont[field] = rivers.iloc[i][field]

        vals.append(rivers.iloc[i][field])

        if (i == 0):
            cont.to_file(counterpart_temp)
        else:
            cont.to_file(counterpart_temp, mode='a')

    if os.path.isfile(count_densify):
        os.remove(count_densify)
    raster = gdal.Open(dem)
    gt = raster.GetGeoTransform()
    pixelSize = gt[1]
    processing.run("qgis:densifygeometriesgivenaninterval",
                   {'INPUT': counterpart_temp, 'INTERVAL': pixelSize, 'OUTPUT': counterpart_vectors})

    print(vals)

    return
