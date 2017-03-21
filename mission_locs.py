#!/usr/bin/env python
import pdb
from fastkml import  kml
from zipfile import ZipFile
from os import listdir
from os.path import isfile, join
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

places_path = "places"

def point_inside_polygon(x,y,poly):
    n = len(poly)
    inside =False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

def kmz_to_points(filename):
    kmz = ZipFile(filename, 'r')
    kmlfile = kmz.open('doc.kml', 'r')
    k = kml.KML()
    k.from_string(kmlfile.read())
    shape = [[f2 for f2 in f.features()] for f in k.features()][0][0]
    shapelist = shape.geometry.exterior.geoms
    points = [(p.x, p.y) for p in shapelist]
    return points

def load_placemap():
    kmzfiles = [f for f in listdir(places_path) if isfile(join(places_path, f))]
    placemap = {}
    for f in kmzfiles:
        placemap[f[:-4]] = kmz_to_points(join(places_path, f))
    return placemap

def mission_to_locs(mission_file):
    placemap = load_placemap()
    with open(mission_file, "r") as f:
        missions = [map(lambda x: x.strip(), m.split(",")) for m in f.readlines()]
    mission_locs = [(float(x[1]), float(x[0])) for x in missions]
    locations = defaultdict(int)
    for mission_loc in mission_locs:
        loc = None
        for place_name, poly in placemap.iteritems():
            if point_inside_polygon(mission_loc[0], mission_loc[1], poly):
                loc = place_name
                break
        loc = "Other" if loc is None else loc
        locations[loc] += 1
    return locations

locs = mission_to_locs("mission_data_2017.csv")
fig, ax = plt.subplots(1)

for i in range(len(locs.keys())):
    k = sorted(locs.keys())[i]
    v = locs[k]
    plt.bar(i, height=v)

fig.suptitle('2017 Mission Locations', fontsize=14, fontweight='bold')
fig.subplots_adjust(top=0.85)
fig.subplots_adjust(bottom=0.2)
#ax.set_title('axes title')

ax.set_xlabel('Location')
ax.set_ylabel('Mission Count')

plt.xticks(range(len(locs.keys())),
        sorted(locs.keys()), rotation=45)

plt.savefig('loc.png', dpi=48)
