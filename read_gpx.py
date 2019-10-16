import sys
import gpxpy
import gpxpy.gpx

import pyproj
import numpy as np

_projections = {}


def zone(coordinates):
    if 56 <= coordinates[1] < 64 and 3 <= coordinates[0] < 12:
        return 32
    if 72 <= coordinates[1] < 84 and 0 <= coordinates[0] < 42:
        if coordinates[0] < 9:
            return 31
        elif coordinates[0] < 21:
            return 33
        elif coordinates[0] < 33:
            return 35
        return 37
    return int((coordinates[0] + 180) / 6) + 1


def letter(coordinates):
    return 'CDEFGHJKLMNPQRSTUVWXX'[int((coordinates[1] + 80) / 8)]


def project(coordinates):
    z = zone(coordinates)
    l = letter(coordinates)
    if z not in _projections:
        _projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
    x, y = _projections[z](coordinates[0], coordinates[1])
    if y < 0:
        y += 10000000
    return z, l, x, y


def unproject(z, l, x, y):
    if z not in _projections:
        _projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
    if l < 'N':
        y -= 10000000
    lng, lat = _projections[z](x, y, inverse=True)
    return (lng, lat)

def calc_BB(points):
    left = top = 10000000000000000
    right = bottom = 0
    elev_max = 0
    elev_min = 1000000

    for p in points:
        if p.x < left:  left = p.x
        if p.x > right: right = p.x
        if p.y < top:   top = p.y
        if p.y > bottom: bottom = p.y
        if p.elevation > elev_max: elev_max = p.elevation
        if p.elevation < elev_min: elev_min = p.elevation
        
    return((left,top),(right,bottom),(elev_max,elev_min))

def map_gpx(fname):
    gpx_file = open(fname, 'r')
    gpx = gpxpy.parse(gpx_file)

    points = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                z, l, x, y = project((point.longitude, point.latitude))
                point.x = x
                point.y = y
                points.append(point)

    for p in points:
        print("%f lat, %f lon, %f x, %f y, %f elev" % (p.latitude, p.longitude, p.x, p.y, p.elevation))

    top,bottom,elev = calc_BB(points)
    print("top: %s, bottom: %s" % (top, bottom))

    ## calculate the fragment

    mapsz = (10,10)

    size = np.array(bottom) - np.array(top)
    #top    = np.array(top) - np.array(top)

    for i in range(len(points)):
        points[i].x = points[i].x - top[0]
        points[i].y = points[i].y - top[1]
        points[i].elevation = points[i].elevation - elev[1]

        #points[i].i = np.interp(points[i].x,[0, size[0]],[0,mapsz[0]])
        #points[i].j = np.interp(points[i].y,[0, size[1]],[0,mapsz[1]])
        #points[i].k = np.interp(points[i].elevation,[0, size[1]],[0,mapsz[2]])
        #points[i].k = 1

        #points[i].i = int(round(points[i].i))
        #points[i].j = int(round(points[i].j))
        #points[i].k = int(round(points[i].k))

    for p in points:
        #print("%f lat, %f lon, %f x, %f y, %f elev" % (p.latitude, p.longitude, p.i, p.j, p.k))
        print("%f;%f;%f" % (p.x, p.y, p.elevation))

    print("size: %s, elev: %s" % (size,elev))
    return(points)
    raise RuntimeError("X")
if __name__ == "__main__":
    map_gpx(sys.argv[1])
