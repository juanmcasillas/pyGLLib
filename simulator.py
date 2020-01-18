
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
import gpxpy.geo
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

class GPXPoint:
    def __init__(self):
        pass

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
            #
            # don't project to UTM
            # z, l, x, y = pm.project((point.longitude, point.latitude))
            
            x = point.longitude
            y = point.latitude

            point.x = x
            point.y = y
            ret_points += [ x, y, point.time, point.elevation ]
            self.optimize and elevs.append(point.elevation)
        
        if self.optimize:
            #smoothed_elevations = np.array(savitzky_golay( np.array(elevs) , 135, 5))
            smoothed_elevations = savitzky_golay( np.array(elevs) , 11, 5)
            ret_points = np.array(ret_points).reshape( int(len(ret_points)/4), 4)
            ret_points[:,3] = smoothed_elevations[0:len(elevs)]
        else:
            ret_points = np.array(ret_points).reshape(int(len(ret_points)/4) ,4)

        ret_gpx_points = []

        for i in ret_points:
            p = GPXPoint()
            p.longitude = i[0]
            p.latitude  = i[1]
            p.time      = i[2]
            p.elevation = i[3]
            p.slope_avg = 0
            ret_gpx_points.append(p)

        return(ret_gpx_points)

    def interp(self, points, distance_gap):
        

        ret = [ points[0] ]
        i = 1
        distance_acc = 0
        elev_acc = 0
        while i < len(points)-1:
            p = points[i-1]
            q = points[i]
            distance = gpxpy.geo.distancePoints3D(p, q)
            distance_acc += distance
            elev_acc +=  (q.elevation-p.elevation)
            if distance_acc >= distance_gap:
                p.slope_avg = gpxpy.geo.gradeslope(distance_acc,elev_acc)
                ret.append( p )
                distance_acc = 0
                elev_acc = 0
            i+=1
        ret.append(q)
        return(ret)

    def slope_to_degrees(self, slope):
        "return the value in degreees"
        angle = ( 45 * slope ) / 100.0
        return(angle)

    def calculate_info(self, points, weight, weight2, NU=0.8):
        i = 1
        G = 9.8

        time_elapsed = 0.0
        distance_t = 0.0
        elevation_t = 0.0
        time_t = 0.0

        while i < len(points):
            p = points[i-1]
            q = points[i]
            
            distance = gpxpy.geo.distancePoints3D(p, q)
            elevation = (q.elevation-p.elevation)
            slope_avg = p.slope_avg
            slope_ang = self.slope_to_degrees(slope_avg)
            timedelta = q.time - p.time
            timedelta = timedelta.seconds
             
            time_t += timedelta
            if elevation > 0:
                elevation_t += elevation
            distance_t += distance

            # if ang < 0 => F_net = P+F; else F_net = F-p (movement)

            #v = distance / timedelta
            #e = 0.5at^2
            #e*2 = at^2
            #e*2/t^2 = a
            a = (2.0*distance)/(timedelta*timedelta)
            v = distance / timedelta
            #v = a * timedelta
            px = weight*G*math.sin(math.radians(math.fabs(slope_ang)))
            py = weight*G*math.cos(math.radians(math.fabs(slope_ang)))*NU

            if slope_ang < 0:
                # a*m = F+px-py
                # (a*m)-px+py = F
                F = (a*weight)-px+py
            else:
                # a*m = F-px-py
                # (a*m)+px+py = F
                F = (a*weight)+px+py

               
            # print("distance: %3.2fm elev: %3.2fm slope: %3.2f%% (%3.2f deg) time: %3.2fs F: %3.2fN, v=%3.2f km/h, a=%3.2f m/s2" % (
            #         distance,
            #         elevation,
            #         slope_avg,
            #         slope_ang,
            #         timedelta,
            #         F,v / 0.2777 ,a
            #         )
            # )

            # weight 2
            px2 = weight2*G*math.sin(math.radians(math.fabs(slope_ang)))
            py2 = weight2*G*math.cos(math.radians(math.fabs(slope_ang)))*NU

            a2 = 0
            if slope_ang < 0:
                # a = (F+px-py/m)
                a2 = (F+px2-py2) / weight2
            else:
                # a = (F-px-py/m)
                a2 = (F-px2-py2) / weight2

            if a2 < 0:
                print("can't move it")
                i+=1 
                continue
        
            # e = 0.5 * a * t^2
            # t = sqrt( e / (0.5 *a))

            t = math.sqrt( distance / (0.5 * a2))

            t_incr = math.fabs(timedelta-t)
            if t >= timedelta:
                time_elapsed  = time_elapsed + t_incr
            else:
                time_elapsed  = time_elapsed - t_incr

            if i == len(points):
                break
            i+=1

        hours_t, minutes_t = divmod(time_t, 3600)
        minutes_t, seconds_t = divmod(minutes_t, 60)

        hours, minutes = divmod(time_elapsed, 3600)
        minutes, seconds= divmod(minutes, 60)

        print("Distance: %3.2f Km" % (distance_t/1000.0))
        print("Elevation: %3.2f m" % elevation_t)
        print("Time (%3.2f kg): %02d:%02d:%02d" % (weight, hours_t, minutes_t, seconds_t))
        print("Time Elapsed (%3.2f kg): %02d:%02d:%02d" % (weight2, hours, minutes, seconds))

    
        


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("-o", "--optimize", help="Optimize GPX input(filter)", action="store_true")
    parser.add_argument("-d", "--distance", help="split the track in distance chunks", action="store", default=20.0)
    parser.add_argument("-w", "--weight", help="original weight", action="store", default=80.0, type=float)
    parser.add_argument("-t", "--target", help="target weight", action="store", default=81.0, type=float)
    parser.add_argument("gpx_file", help="GPX file to load")
    args = parser.parse_args()

    loader = GPXLoader(args.gpx_file, optimize=True)
    points = loader.load() 

    print("-" * 80)
    # now, i have to build a new array of points, calculating the distance between them
    # so we split the track in distance segments
    #
    points = loader.interp(points, args.distance)
    #
    # calculate some info from the segments

    loader.calculate_info(points, args.weight, args.target)


    gpx_out = GPXItem()
    data = gpx_out.CreateGPX11(points, trk_name="OUTPUT")
    fd = open("outpux.gpx","w+")
    fd.write(data)
    fd.close()


