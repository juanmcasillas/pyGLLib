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
                self.vertex[self.I(i,j)] = random.uniform( -1, 1)
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
   
                
                # second triangle
                pos = []
                if not self._isVID(i  ,j):     pos += [[i  ,j  , self.vertex[self.I(i  ,j)]   ]]
                if not self._isVID(i+1,j+1):   pos += [[i+1,j+1, self.vertex[self.I(i+1,j+1)] ]]
                if not self._isVID(i+1,j  ):   pos += [[i+1,j  , self.vertex[self.I(i+1,j)]   ]]
                pos_idx = [ self._getVID(i,j), self._getVID(i+1,j+1), self._getVID(i+1,j) ]

                ret += pos
                idx += pos_idx

                tri_counter += 2
        
        #print(ret)
        return (ret,idx,tri_counter)

    def normalize_v3(self, arr):
        ''' Normalize a numpy array of 3 component vectors shape=(n,3) '''
        lens = np.sqrt( arr[:,0]**2 + arr[:,1]**2 + arr[:,2]**2 )
        print("lens", lens)
        arr[:,0] /= lens
        arr[:,1] /= lens
        arr[:,2] /= lens                
        return arr

    def normalize_v31(self, arr):
        ''' Normalize a numpy array of 3 component vectors shape=(n,3) '''
        lens = np.sqrt( math.pow(arr[0],2) + math.pow(arr[1],2) + math.pow(arr[2],2) )
        if lens != 0.0:
            arr[0] /= lens
            arr[1] /= lens
            arr[2] /= lens
        else:
            arr[0] = 0.0
            arr[1] = 0.0
            arr[2] = 0.0

        return arr

    def calc_normals_x(self, vertices, faces):
   
        vertices = vertices.reshape([int(vertices.size/3),3])
        faces = faces.reshape([int(faces.size/3),3])
        
        #Create a zeroed array with the same type and shape as our vertices i.e., per vertex normal
        norm = np.zeros( vertices.shape, dtype=vertices.dtype )
        #Create an indexed view into the vertex array using the array of three indices for triangles
        tris = vertices[faces]

        #Calculate the normal for all the triangles, by taking the cross product of the vectors v1-v0, and v2-v0 in each triangle             
        n = np.cross( tris[::,1 ] - tris[::,0]  , tris[::,2 ] - tris[::,0] )
        # n is now an array of normals per triangle. The length of each normal is dependent the vertices, 
        # we need to normalize these, so that our next step weights each normal equally.
        self.normalize_v3(n)
        # now we have a normalized array of normals, one per triangle, i.e., per triangle normals.
        # But instead of one per triangle (i.e., flat shading), we add to each vertex in that triangle, 
        # the triangles' normal. Multiple triangles would then contribute to every vertex, so we need to normalize again afterwards.
        # The cool part, we can actually add the normals through an indexed view of our (zeroed) per vertex normal array
        norm[ faces[:,0] ] += n
        norm[ faces[:,1] ] += n
        norm[ faces[:,2] ] += n
        self.normalize_v3(norm)  
        return(norm)      

    def calc_normals(self, vertices, faces):
        n = []
        v = vertices.reshape([int(vertices.size/3),3])
        f = faces.reshape([int(faces.size/3),3])
        for i in f:
            
            triangle = v[i]
            v1 = triangle[1] - triangle[0]
            v2 = triangle[2] - triangle[0]
            normal = self.normalize_v31(np.cross(v1, v2))
            ##normal = np.cross(v2, v1)
            n.append(normal)
        return(n)



class GLTerrain(pyGLLib.object.GLObjectBaseEBO):
    "Use the EBO object as we have pos,normal in the coords"
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.width, self.height = self.size
        self.terrain = Terrain(self.width, self.height)

    def load_model(self):
        ##self.terrain.fillRandom()
        W = self.terrain.width-1
        H = self.terrain.height-1
        D = max(self.terrain.width,self.terrain.height)
        r  = []
   
        triangles,idx, counter = self.terrain.T()
        
        #normals = terrain.calc_normals(np.array(triangles, np.float32), np.array(idx, np.uint32))
        normals = self.terrain.calc_normals_x(np.array(triangles, np.float32), np.array(idx, np.uint32))
        i = 0
        for t in triangles:
            x = 2 * t[0] / W - 1;
            y = 2 * t[1] / H - 1;
            z = 2 * t[2] / D - 1;

            n = normals[i]
                 #coords    #normals
            r += [ x, z, y, 1.0, 0.0, 0.0 ]
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
