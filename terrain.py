import numpy as np
import random
import math
import pyGLLib

class Terrain:
    "terrain oriented in x,z mean Y the height"
    def __init__(self,width, height):
        self.width = width+1
        self.height = height+1
        self.vertex = [ 0.0 ] * (self.width*self.height)
      
        self.vertex_counter = 0
        self.idxmap = {}
    
    def fillRandom(self):
        for j in range(self.height):
            for i in range(self.width):
                self.vertex[self.I(i,j)] = random.uniform( 0, 0.5)
    
    def set(self, x, y, z=0):
        #print(x,y, self.I(x,y))
        self.vertex[self.I(x,y)] = z

    def I(self, x, y):
        "maps the X,Y to the current vertex position in the array"
        #(3,3) -> 28
        i = ((y)*self.width)+x
        return(i)

    def _getVID(self,i,j):
        p = "%d_%d" % (i,j)
        if p in self.idxmap.keys():
            vertex_id = self.idxmap[p]
        else:
            vertex_id = self.vertex_counter
            self.idxmap[p] = vertex_id
            self.vertex_counter +=1

        return vertex_id

    def _isVID(self,i,j):
        p = "%d_%d" % (i,j)
        if p in self.idxmap.keys():
            return True
        return False

    def T(self, tile_size=5):
        
        # each vertex has a color, and a normal.
        ret = []
        idx = []
        normals = []
        
        self.vertex_counter = 0
        self.idxmap = {}
        tri_counter = 0

        for j in range(self.height-1):
            for i in range(self.width-1):
  
                # first triangle  
               
                pos = []
                if not self._isVID(i  ,j):     pos += [[i  ,j  , self.vertex[self.I(i  ,j)]   ]]
                if not self._isVID(i+1,j+1):   pos += [[i+1,j+1, self.vertex[self.I(i+1,j+1)] ]]
                if not self._isVID(i  ,j+1):   pos += [[i  ,j+1, self.vertex[self.I(i  ,j+1)] ]]
                pos_idx = [ self._getVID(i,j), self._getVID(i+1,j+1), self._getVID(i,j+1) ]
                ret += pos
                idx += pos_idx
                # calculate normal for the three vertex
                normals += self.calc_normal_from_triangle(pos_idx, ret)
                
                # second triangle
                pos = []
                if not self._isVID(i  ,j):     pos += [[i  ,j  , self.vertex[self.I(i  ,j)]   ]]
                if not self._isVID(i+1,j+1):   pos += [[i+1,j+1, self.vertex[self.I(i+1,j+1)] ]]
                if not self._isVID(i+1,j  ):   pos += [[i+1,j  , self.vertex[self.I(i+1,j)]   ]]
                pos_idx = [ self._getVID(i,j), self._getVID(i+1,j), self._getVID(i+1,j+1) ]

                ret += pos
                idx += pos_idx
                
                # calculate normal for the three vertex
                normals += self.calc_normal_from_triangle(pos_idx, ret)


                tri_counter += 2
        
        #print(ret)
        return (ret,idx,tri_counter,normals)

    def calc_normal_from_triangle(self, t, vertex):
        
        normals = [0.0]*3
        Q,R,S = list(map(lambda x: np.array(vertex[x]), t))
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

        #raise RuntimeError("X")
        #module = np.sqrt( math.pow(N[0],2) + math.pow(N[1],2) + math.pow(N[2],2) )
        #U = N/module
        #print("U,",N,"->",U)


        






class GLTerrain(pyGLLib.object.GLObjectBaseEBO):
    "Use the EBO object as we have pos,normal in the coords"
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.width, self.height = self.size
        self.terrain = Terrain(self.width, self.height)

    def load_model(self):
        self.terrain.fillRandom()
        W = self.terrain.width-1
        H = self.terrain.height-1
        D = max(self.terrain.width,self.terrain.height)
        r  = []
   
        triangles,idx, counter, normals = self.terrain.T()
        
        #normals = self.terrain.calc_normals(np.array(triangles, np.float32), np.array(idx, np.uint32))
        #normals = self.terrain.calc_normals_x(np.array(triangles, np.float32), np.array(idx, np.uint32))

        # adjust the CENTER of the terrain to 0,0 (don't move z)
        center = ( W /2, H/ 2, 0)
        triangles = np.array(triangles, dtype=np.float32)
        triangles = triangles - center

        #print(triangles)
        #print(normals)

        i = 0
        for t in triangles:
            #x = 2 * t[0] / W - 1;
            #y = 2 * t[1] / H - 1;
            #z = 2 * t[2] / D - 1;
            x, y, z = t

            n = normals[i]
            nx,ny,nz = n
                  #coords    #normals
            r += [ x, z, y, nx, nz, ny ]
            i += 1
        
        self.vertexData = np.array(r, np.float32)
        self.indexData  = np.array(idx, np.uint32)
        triangles   = counter
  


if __name__ == "__main__":
    terrain = Terrain(8,6)
    terrain.set(0,0,1)
    terrain.set(terrain.width-1,0,1)
    terrain.set(terrain.width-1,terrain.height-1,1)
    terrain.set(0,terrain.height-1,1)
    terrain.set(int((terrain.width-1)/2),int((terrain.height-1)/2),1)
    terrain.T()
