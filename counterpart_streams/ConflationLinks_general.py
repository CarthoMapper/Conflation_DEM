import geopandas as gpd
import numpy as np
import math
from scipy.spatial.distance import cdist
from shapely.geometry import Point
from shapely.geometry import LineString


def euc_dist(p1, p2):
    return math.sqrt((p2[0] - p1[0]) * (p2[0] - p1[0]) + (p2[1] - p1[1]) * (p2[1] - p1[1]))

def euc_matrix(P, Q):
    mdist = cdist(P, Q, 'euclidean')
    return mdist
def conflation_links (in_counterparts, in_hidrolines,  out_links):
    rivers = gpd.read_file(in_hidrolines)
    counts = gpd.read_file(in_counterparts)

    n = rivers.shape[0]
    features = []
    backfeatures = []

    for g in range(n):
        hydro_coords = rivers.iloc[[g]]
        count_coords = counts.iloc[[g]]

        hydro_coords = hydro_coords.copy()
        hydro_coords = hydro_coords.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
        hydro_coords = hydro_coords.to_list()
        hydro_coords = hydro_coords[0]
        hydro_coords = [(x, y) for (x, y, z) in hydro_coords]
        nj = len(hydro_coords)

        count_coords = count_coords.copy()
        count_coords = count_coords.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
        count_coords = count_coords.to_list()
        count_coords = count_coords[0]
        ni = len(count_coords)
        print(nj, ni)

        id = g
        print(id)

        eucs = euc_matrix(count_coords, hydro_coords)

        minjays = []
        minj = 0
        for i in range(0, ni):
            found = False
            for j in range(minj + 1, nj):
                for k in range(i + 1, ni):
                    if eucs[k, j] <= eucs[i, j]:
                        minj = j - 1
                        found = True
                        break
                if found:
                    break
            minjays.append(minj)

        jbacks = []
        ibacks = []
        curj = 0
        for i in range(1, ni - 1):
            nextj = minjays[i]
            if nextj - curj > 1:
                for j in range(curj + 1, nextj):
                    iback = np.argmin(eucs[(i - 1):(i + 1), j]) + i - 1
                    jbacks.append(j)
                    ibacks.append(iback)
            curj = nextj
        if nj - 1 not in minjays:
            for j in range(curj + 1, nj):
                jbacks.append(j)
                ibacks.append(ni - 1)

        # check if the first points are connected
        if 0 not in minjays:
            ibacks.insert(0, 0)
            jbacks.insert(0, 0)

        pairs = zip(range(ni), minjays)
        backpairs = zip(ibacks, jbacks)

        for pair in pairs:
            line = [Point(count_coords[pair[0]]), Point(hydro_coords[pair[1]])]
            features.append(LineString(line))


        for pair in backpairs:
            line = [Point(count_coords[pair[0]]), Point(hydro_coords[pair[1]])]
            backfeatures.append(LineString(line))

    features.extend(backfeatures)

    geom = gpd.GeoSeries(features)

    gdf = gpd.GeoDataFrame(geometry=geom)

    gdf.to_file(out_links)


