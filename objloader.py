# Basic objloader from:
#  Original por http://www.pygame.org/wiki/OBJFileLoader
#  Ajustes por altaruru: https://www.altaruru.com
#  >> resolucion errores a python3, carga de archivos y recursos en directorios distintos a script/codigo

#import pygame
import os
#from OpenGL.GL import *
import pyGLLib
import numpy as np

def MTL(spath2, filename):
    contents = {}
    mtl = None
    rpath=os.path.dirname(os.path.abspath(__file__)) + '/' + spath2
    #print("MTL: " + filename)
    #print("rpath: " + rpath)
    for line in open(rpath+filename, "r"):        
        if line.startswith('#'): continue        
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError("mtl file doesn't start with newmtl stmt")
        elif values[0] == 'map_Kd':
            # load the texture referred to by this declaration
            mtl[values[0]] = values[1]
            smatpath=mtl['map_Kd']           
            smatpath=smatpath.replace("\\","/")
            #print("*", rpath + smatpath)
            
            #surf = pygame.image.load(rpath + smatpath)
            #image = pygame.image.tostring(surf, 'RGBA', 1)
            #ix, iy = surf.get_rect().size
            #texid = mtl['texture_Kd'] = glGenTextures(1)
            #glBindTexture(GL_TEXTURE_2D, texid)
            #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            #glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        else:
            mtl[values[0]] = map(float, values[1:])
    return contents

class OBJ:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        material = None
        #print(">>" + filename)
        i=filename.rfind("/")
        
        if(i==-1):
            spath2=""
        else:
            spath2=filename[0:i] + '/'
        
        for line in open(os.path.dirname(os.path.abspath(__file__)) + '/' + filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                #spath2 es la ruta relativa al objeto, puede ser un directorio
                self.mtl = MTL(spath2, values[1])
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))


        #self.gl_list = glGenLists(1)
        #glNewList(self.gl_list, GL_COMPILE)
        #glEnable(GL_TEXTURE_2D)
        #glFrontFace(GL_CCW)

        self.vertex = ()
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            mtl = self.mtl[material]
            #print("#   ")
            #print(mtl)
            if 'texture_Kd' in mtl:
                # use diffuse texmap
                ##glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
                pass
            else:
                # just use diffuse colour
                #glColor(*mtl['Kd'])
                ##glColor(1, 1, 1, 0.5)
                pass
            
            #
            # juanm.casillas
            #
            # quick fix to load models in new profile (3.3 core)
            # ignore for now the color, and textures
            # next, learn how to texture things and do the work
           
            #glBegin(GL_POLYGON)            
            for i in range(len(vertices)):
                if normals[i] > 0:
                    ##glNormal3fv(self.normals[normals[i] - 1])
                    pass
                if texture_coords[i] > 0:
                    ##glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                    pass
                ##glVertex3fv(self.vertices[vertices[i] - 1])
                ##print(np.asarray(self.vertices[vertices[i]-1]))
                
                self.vertex += self.vertices[vertices[i]-1]
                self.vertex += self.normals[normals[i]-1]
            #glEnd()  
          
        #glDisable(GL_TEXTURE_2D)
        #glEndList()
        
class GLObj(pyGLLib.object.GLObjectBaseNormal):
    "Use the EBO object as we have pos,normal in the coords"
    def __init__(self, fname):
        super().__init__()
        self.fname = fname
        self.obj = OBJ(fname, swapyz=True) 


    def load_model(self):
        
        self.vertexData = np.asarray(self.obj.vertex, dtype=np.float32)        
        triangles   = len(self.vertexData)/18