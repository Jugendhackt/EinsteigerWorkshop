#!/usr/bin/env python
# -*- coding:utf-8 -*-

from mpl_toolkits.basemap import Basemap, shiftgrid, cm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import matplotlib.patches
import matplotlib.collections
import matplotlib.path

import utm
import geojson
import json
import collections
import itertools

FILE = "data/hamburg.geojson"

raw = geojson.load(open(FILE))


def isStadtteil(f):
    return f['properties'].get('name:prefix') == "Stadtteil"

regions = filter(isStadtteil, raw['features'])

borders = {
    region['properties'].get('name'):
        (region['geometry']['coordinates'][0], )
        if region['geometry']['type'] == 'Polygon'
    else tuple(map(lambda p: p[0], region['geometry']['coordinates']))
    for region in regions if all([
        region['properties'].get('name'),
        region['geometry']['type'] in ['Polygon', 'MultiPolygon'],
    ])
}

outlines = {
    name: (
        (
            [lon for lon, lat in polygon],
            [lat for lon, lat in polygon]
        ) for polygon in polygons
    ) for name, polygons in borders.iteritems()
}

corners = (
    (53.39, 9.72), (53.75, 10.33)
)


raw_data = json.load(open("data/schulen.geojson"))
schools = [
    {
        'name': feature['properties'].get('Name'),
        'region': feature['properties'].get('stadtteil'),
        'position': utm.to_latlon(feature['geometry']['coordinates'][0],
                                  feature['geometry']['coordinates'][1],
                                  32, 'N'),
        'value': feature['properties'].get('schueleranzahl', 0),
    } for feature in raw_data['features']
]
raw_data = json.load(open("data/gruenflaechen.geojson"))
gruenflaechen = [
    {
        'name': feature['properties'].get('Name'),
        'region': feature['properties'].get('stadtteil'),
        'position': utm.to_latlon(feature['geometry']['coordinates'][0],
                                  feature['geometry']['coordinates'][1],
                                  32, 'N'),
    } for feature in raw_data['features']
]

data = gruenflaechen


def count_by_position(regions, data, key=None):
    paths = {
        name: matplotlib.path.Path(
            np.array(polygon),
            ([matplotlib.path.Path.MOVETO] +
             [matplotlib.path.Path.LINETO for _ in range(len(polygon) - 2)] +
             [matplotlib.path.Path.CLOSEPOLY]
             )
        )
        for name, polygons in regions.iteritems()
        for polygon in polygons
    }
    count = collections.defaultdict(int)
    for entry in data:
        for name, path in paths.iteritems():
            pos = entry['position'][1], entry['position'][0]
            if path.contains_point(pos):
                count[name] += int(entry.get(key, 1))
    return count


def count_by_region(regions, data, key=None):
    count = collections.defaultdict(int)
    for entry in data:
        count[entry['region']] += int(entry.get(key, 1))
    return count

# count = count_by_region(borders, data, key="value")
# count = count_by_region(borders, data)
count = count_by_position(borders, data)

normalize = matplotlib.colors.Normalize(vmin=min(count.values()),
                                        vmax=max(count.values()))
colors = matplotlib.cm.get_cmap('Spectral')

m = Basemap(projection='merc',
            urcrnrlat=corners[1][0], urcrnrlon=corners[1][1],
            llcrnrlat=corners[0][0], llcrnrlon=corners[0][1],
            lat_0=53.5449, lon_0=9.9731,
            resolution='h')

ax = plt.gca()

positions = zip(*[entry['position'] for entry in data])
# values = [float(entry['value']) / 10 for entry in data]
values = 10

patches = []
counts = []
for name, polygons in outlines.iteritems():
    for (lons, lats) in polygons:
        x, y = m(lons, lats)
        xy = zip(x, y)
        area = .5 * sum(
            (xy[i][0] * xy[i + 1][1]) - (xy[i + 1][0] * xy[i][1])
            for i in range(len(xy) - 1)
        )
        cx = 1 / (6 * area) * sum(
            (xy[i][0] + xy[i + 1][0]) * ((xy[i][0] * xy[i + 1][1]) - (xy[i + 1][0] * xy[i][1]))
            for i in range(len(xy) - 1)
        )
        cy = 1 / (6 * area) * sum(
            (xy[i][1] + xy[i + 1][1]) * ((xy[i][0] * xy[i + 1][1]) - (xy[i + 1][0] * xy[i][1]))
            for i in range(len(xy) - 1)
        )
        patches.append(matplotlib.patches.Polygon(xy))
        counts.append(count[name])
        # plt.text(cx, cy, name,
        #          horizontalalignment="center",
        #          verticalalignment="center")

m.set_axes_limits()

x, y = m(positions[1], positions[0])
plt.scatter(x, y, values, "k")

p = matplotlib.collections.PatchCollection(patches, cmap=colors, norm=normalize, alpha=0.7)
p.set_array(np.array(counts))
ax.add_collection(p)
plt.colorbar(p,
             spacing="proportional",
             ticks=range(max(counts) + 1),
             boundaries=range(max(counts) + 1))

# plt.title("Anzahl der Schulen")
plt.title(u"Anzahl der Grünflächen")

plt.show()
