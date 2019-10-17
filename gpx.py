#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////////////////
#
# Read a GPX file, and build a road. Return the data in the normalized
# OpenGL vertexData structure
#
# ///////////////////////////////////////////////////////////////////////////

import sys
import gpxpy
import gpxpy.gpx

import pyproj
import numpy as np
import os
import math
import pyGLLib

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

    def project(self,coordinates):
        z = self.zone(coordinates)
        l = self.letter(coordinates)
        if z not in self._projections:
            self._projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
        x, y = self._projections[z](coordinates[0], coordinates[1])
        if y < 0:
            y += 10000000
        return z, l, x, y

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
    def __init__(self, fname=None):
        self.fname = fname

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

        for track in gpx_data.tracks:
            for segment in track.segments:
                for point in segment.points:
                    z, l, x, y = pm.project((point.longitude, point.latitude))
                    point.x = x
                    point.y = y
                    points += [x, y, point.elevation]
        
        return points


# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class BoundingBox(object):
    """
    A 2D bounding box
    """
    def __init__(self):
        pass

    def calculate(self, points, offset=False, interp=None):
        """
        Compute the upright 2D bounding box for a set of
        2D coordinates in a (n,3) numpy array.

        You can access the bbox using the
        (minx, maxx, miny, maxy) members.
        """
        if isinstance(points,list):
            points = np.array(points).reshape(int(len(points)/3) ,3)
            
       
        self.minx = np.min(points[:,[0]]) # X
        self.maxx = np.max(points[:,[0]]) # X
        
        self.miny = np.min(points[:,[1]]) # Y
        self.maxy = np.max(points[:,[1]]) # Y
        
        self.minz = np.min(points[:,[2]]) # Z
        self.maxz = np.max(points[:,[2]]) # Z

        # offset the data to 0 (top, left)
        if offset:
            points = points - self.coords[0]
            self.minx_o = self.minx
            self.maxx_o = self.maxx

            self.miny_o = self.miny
            self.maxy_o = self.maxy

            self.minz_o = self.minz
            self.maxz_o = self.maxz

            # recompute new values
            self.minx = np.min(points[:,[0]]) # X
            self.maxx = np.max(points[:,[0]]) # X
           
            self.miny = np.min(points[:,[1]]) # Y
            self.maxy = np.max(points[:,[1]]) # Y
            
            self.minz = np.min(points[:,[2]]) # Z
            self.maxz = np.max(points[:,[2]]) # Z
        
        # interpolate the data to the new space
        if interp is not None:
            x = np.interp(points[:,[0]], (self.minx, self.maxx), interp[0])
            y = np.interp(points[:,[1]], (self.miny, self.maxy), interp[1])
            z = np.interp(points[:,[2]], (self.minz, self.maxz), interp[2])
            points = np.column_stack((x,y,z))

        #return points.reshape(points.size)
        return points.flatten()

    @property
    def width(self):
        """X-axis extent of the bounding box"""
        return self.maxx - self.minx

    @property
    def height(self):
        """Y-axis extent of the bounding box"""
        return self.maxy - self.miny

    @property
    def area(self):
        """width * height"""
        return self.width * self.height

    @property
    def aspect_ratio(self):
        """width / height"""
        return self.width / self.height

    @property
    def center(self):
        """(x,y) center point of the bounding box"""
        return (self.minx + self.width / 2, self.miny + self.height / 2)

    @property
    def max_dim(self):
        """The larger dimension: max(width, height)"""
        return max(self.width, self.height)

    @property
    def min_dim(self):
        """The larger dimension: max(width, height)"""
        return min(self.width, self.height)

    @property
    def coords(self):
        """The larger dimension: max(width, height)"""
        a = (self.minx, self.miny, self.minz)
        b = (self.maxx, self.maxy, self.maxz)
        return (a, b)

    def __repr__(self):
        return "BoundingBox({}, {}, {}, {}, {}, {})".format(
            self.minx, self.maxx, self.miny, self.maxy, self.minz, self.maxz)


def V_U(U):
    "calculate unitary vector"
    module = np.sqrt( math.pow(U[0],2) + math.pow(U[1],2) + math.pow(U[2],2) )
    U = U/module  
    return U  

class RoadGenerator(object):
    def __init__(self, points):
        # build a [len,3] matrix
        self.points = np.array(points).reshape(int(len(points)/3),3)
        
    
    def add_perpendicular(self, distance):
        i = 0
        vertex = []
        # don't forget the last one!!!

        for i in range(len(self.points)):
            if i == len(self.points)-1:
                # last point
                P = self.points[-1]
                Q = self.points[-2]
            else:
                P = self.points[i]
                Q = self.points[i+1]
            PQ = Q-P
            PQ_U = V_U(PQ)
            T1 = np.array(( -PQ[1], PQ[0], 0)) * distance
            T2 = np.array(( PQ[1], -PQ[0], 0)) * distance
            T1 = P + T1
            T2 = P + T2
            vertex += [ T1, P, T2]
            
        return vertex
        
    def build(self, distance):
        # T1, P, T2
        # Q1, Q, Q2
        # ....
        
        triangles = []
        quads = self.add_perpendicular(distance)
        i=0
        # skip last polygon.
        while i < len(quads)-5:
            Q = quads[i]
            R = quads[i+2]
            S = quads[i+3]
            Normals = self.calc_normal_from_triangle((Q,S,R))
            triangles += [ Q,S,R ]
            triangles += Normals
            
            S = quads[i+2]
            R = quads[i+3]
            Q = quads[i+4]
            Normals = self.calc_normal_from_triangle((Q,S,R))
            triangles += [ Q,S,R ]
            triangles += Normals

            i = i+3

        return(np.array(triangles).flatten())

    def calc_normal_from_triangle(self, triangle):
        
        normals = [0.0]*3
        Q,R,S = triangle
        #print(t, "->", Q,R,S)

        #first vertex
        QR = R-Q
        QS = S-Q
        normals[0] = list(np.cross(QR,QS))

        #second vertex
        RS = S-R
        RQ = Q-R
        normals[1] = list(np.cross(RS,RQ))

        #third vertex
        SQ = Q-S
        SR = R-S
        normals[2] = list(np.cross(SQ,SR))
        return normals    

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

def test_gpx(fname):

    # a = [1, 1, 1, 
    #      2, 8, 2, 
    #      10, 10, 3,
    #      15, 4, 9 ]

    # x = BoundingBox()
    # print(np.array(a).reshape(4,3))
    # a = x.calculate(a, offset=False, interp=((0,150), (0,100), (0,1)))
    # print("---")
    # print(np.array(a).reshape(4,3))
    # print(x)
    # print(x.coords)

    loader = GPXLoader(fname)
    points = loader.load() 

    #
    # get the points, move then to the top left origin, and then,
    # map the vectors to the new coordinate space.
    #
    # bb = BoundingBox()
    # points = bb.calculate(points, offset=True, interp=((0,10), (0,10), (0,5)))
    # print(points)
    # import matplotlib.pyplot as plt
    # d = np.array(points).reshape(int(len(points)/3),3)
    # x = d[:,[0]]
    # y = d[:,[1]]
    # plt.plot(x,y)
    # plt.show()

    #
    # get the points, move then to the top left origin, and then,
    # map the vectors to the new coordinate space.
    #
    bb = BoundingBox()
    points = bb.calculate(points, offset=True, interp=((0,10), (0,10), (0,5)))

    roadgen = RoadGenerator(points)
    vertex = roadgen.build(1)

    draw(vertex)

class GLRoad(pyGLLib.object.GLObjectBaseNormal):
    
    def __init__(self, fname, distance=1):
        super().__init__()
        self.fname = fname
        self.distance = distance

    def load_model(self):
        loader = GPXLoader(self.fname)
        points = loader.load() 
        bb = BoundingBox()
        points = bb.calculate(points, offset=True, interp=((0,10), (0,10), (0,5)))

        roadgen = RoadGenerator(points)
        self.vertexData = roadgen.build(self.distance)
        self.triangles = len(self.vertexData)/6


if __name__ == "__main__":
    test_gpx(sys.argv[1])
