from pyGLlib import GLApp
from terrain import Terrain
import numpy as np

class GLAppTerrain(GLApp):
    def __init__(self, size, wireframe=False):
        super().__init__(size,"Terrain Generator", wireframe=wireframe)
    
    def load_model(self):

        terrain = Terrain(10,10)
        terrain.fillRandom()
        W = terrain.width-1
        H = terrain.height-1
        D = max(terrain.width,terrain.height)

        r  = []
   
        triangles,idx, counter = terrain.T()
        
     
        #normals = terrain.calc_normals(np.array(triangles, np.float32), np.array(idx, np.uint32))
        normals = terrain.calc_normals_x(np.array(triangles, np.float32), np.array(idx, np.uint32))
        i = 0
        for t in triangles:
            x = 2 * t[0] / W - 1;
            y = 2 * t[1] / H - 1;
            z = 2 * t[2] / D - 1;

            n = normals[i]
                 #coords     #color         #normals
            r += [ x, z, y,  1.0, 0.0, 0.0,  2 * n[0]/W - 1, 2 *n[2]/ D - 1, 2 *n[1]/ H - 1 ]
            i += 1
        vertexData = np.array(r, np.float32)
        indexData  = np.array(idx, np.uint32)
        triangles   = counter
       
        return(vertexData, indexData, triangles)


if __name__ == "__main__":

    app = GLAppTerrain( (1024,768), wireframe=False)
    app.init()
    app.load_shaders()
    app.set_light()
    app.set_gl_buffers()
    app.load_callbacks()
    app.run()
    app.cleanup()
