
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////////////////
#
# Read a GPX file, and build a road. Return the data in the normalized
# OpenGL vertexData structure
#
# ///////////////////////////////////////////////////////////////////////////

import os
import numpy as np
import math
import argparse
import sys
import gpxpy
import gpxpy.gpx
import pyproj
from gpx_optimizer import GPXOptimizer, savitzky_golay
from slopes import SlopeManager
from gpxtoolbox import GPXItem

# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////

class ProjectionMapper:
    """
    project a WSG84 to UTM
    z, l, x, y = project((point.longitude, point.latitude))
    """

    def __init__(self):
        self._projections = {}

    def zone(self,coordinates):
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


    def letter(self,coordinates):
        return 'CDEFGHJKLMNPQRSTUVWXX'[int((coordinates[1] + 80) / 8)]

    def project(self,coordinates): # lon, lat
        z = self.zone(coordinates)
        l = self.letter(coordinates)
        if z not in self._projections:
            self._projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
        x, y = self._projections[z](coordinates[0], coordinates[1])
        if y < 0:
            y += 10000000
        return z, l, x, y

    def project_2(self, lon, lat):
        
        myProj = pyproj.Proj("+proj=utm +zone=30T, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
        UTMx, UTMy = myProj(lon, lat)
        #print(lat, lon, UTMx, UTMy)
        return (UTMx, UTMy)

    def unproject(self, z, l, x, y):
        if z not in self._projections:
            self._projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
        if l < 'N':
            y -= 10000000
        lng, lat = self._projections[z](x, y, inverse=True)
        return (lng, lat)


# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////

class GPXLoader:
    def __init__(self, fname=None, optimize=False):
        self.fname = fname
        self.optimize = optimize

    def load(self,fname=None):
        f = fname or self.fname
        if f is None:
            raise ValueError("GPX file is None")
        if not os.path.exists(f):
            raise RuntimeError("GPX file %s not found" % f)

        gpx_file = open(f, 'r')
        gpx_data = gpxpy.parse(gpx_file)

        points = []
        pm = ProjectionMapper()

        # call my optimizer (remove contiguous points)
        points = []
        for track in gpx_data.tracks:
            for segment in track.segments:
                points += segment.points

        if self.optimize:
            gpx_optmizer = GPXOptimizer()
            opt_points = gpx_optmizer.Optimize(points)
            gpx_optmizer.Print_stats()
            points = opt_points
            elevs = []
        ret_points = []
        
        for point in points:
            z, l, x, y = pm.project((point.longitude, point.latitude))
            point.x = x
            point.y = y
            ret_points += [x, y, point.elevation]
            self.optimize and elevs.append(point.elevation)
        
        if self.optimize:
            #smoothed_elevations = np.array(savitzky_golay( np.array(elevs) , 135, 5))
            smoothed_elevations = savitzky_golay( np.array(elevs) , 11, 5)
            #idx = np.arange(0,44)
            #import matplotlib.pyplot as plt
            #plt.plot(idx,elevs[0:44])
            #plt.plot(idx,smoothed_elevations[0:44])
            #plt.show()
            ret_points = np.array(ret_points).reshape( int(len(ret_points)/3), 3)
            ret_points[:,2] = smoothed_elevations[0:len(elevs)]

        return(ret_points)


# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////

def draw(points):
    import matplotlib.pyplot as plt
    d = np.array(points).reshape(int(len(points)/3),3)
    x = d[:,[0]]
    y = d[:,[1]]
    plt.plot(x,y, linestyle="",marker="o")
    plt.show()    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("-o", "--optimize", help="Optimize GPX input(filter)", action="store_true")
    parser.add_argument("-d", "--distance", help="split the track in distance chunks", action="store", default=10.0)
    parser.add_argument("gpx_file", help="GPX file to load")
    args = parser.parse_args()

    slopemanager = SlopeManager(distance_gap=args.distance)
    slopemanager.LoadGPX(args.gpx_file, optimize=True)
    slopemanager.ComputeSlope()

    pcontainer = [ slopemanager[0] ]
    i = 1
    while i < slopemanager.len():
    
        p = slopemanager[i-1]       
        q = slopemanager[i]
    
        onlyOne = False
        #print(p.slope_avg, q.slope_avg)
        if p.slope_avg != q.slope_avg:
    
            # create a new segment.
            if len(pcontainer) == 1:
                pcontainer.append(q) #
                onlyOne = True 
                    
            if onlyOne:
                pcontainer = [ q ]
                i += 1
            else:
                pcontainer = [ p ]
            
        else:
            pcontainer.append(q)
            i += 1
            
    print(len(pcontainer))

    gpx_out = GPXItem()
    data = gpx_out.CreateGPX11(pcontainer, trk_name="OUTPUT")
    fd = open("outpux.gpx","w+")
    fd.write(data)
    fd.close()
