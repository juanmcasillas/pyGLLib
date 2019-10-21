#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////////////////
#
# pyGLLib.py
# Juan M. Casillas <juanm.casillas@gmail.com>
#
# ///////////////////////////////////////////////////////////////////////////

import pyGLLib
import glm
import sys
import numpy as np
import math
from objloader import *

class pyObjViewer(pyGLLib.GLApp):
    def __init__(self, size,  title, wireframe=False, grabmouse=True, shadows=False):
        super().__init__(size, title, wireframe=wireframe, grabmouse=grabmouse )
        self.shadows = shadows
        self.angle = 0.0
   
    def load_shaders(self):
        # this will be de "default shader"
        s = pyGLLib.shader.GLShaderStandard()
        s.load()
        self.shaders["standard"] = s

        s = pyGLLib.shader.GLShaderPlain()
        s.load()
        self.shaders["plain"] = s

        s = pyGLLib.shader.GLShaderVertexColor()
        s.load()
        self.shaders["color"] = s        

    def set_light(self):
        self.light.pos = (0.0, 2.0, 2.0)
        self.light.color = (1.0,1.0,1.0)
        self.light.ambient = (0.8, 0.8, 0.8)
        self.light.diffuse = (0.8, 0.8, 0.8)
        
    def set_camera(self):
        self.camera.pos = (0,5, 15)
        self.camera.speed = 100


    def render(self):

        shader="standard"

        # self.model_matrix = glm.mat4(1.0)
        # self.model_matrix = glm.translate(self.model_matrix, glm.vec3(-2,0,0))
        # self.model_matrix = glm.rotate(self.model_matrix, math.radians(-90),(1,0,0))
        # self.model_matrix = glm.rotate(self.model_matrix, math.radians(180),(0,0,1))
        # self.model_matrix = glm.scale(self.model_matrix, glm.vec3(0.2))            
        
        self.shaders[shader].use()
        self.shaders[shader].setMat4(b'model',self.model_matrix)
        self.shaders[shader].setMat4(b'view',self.view_matrix)
        self.shaders[shader].setMat4(b'projection',self.projection_matrix)
        self.shaders[shader].setVec3(b'objectColor',(1.0,0.5,0.31))
        self.shaders[shader].setVec3(b'light.color',self.light.color)
        self.shaders[shader].setVec3(b'light.diffuse',self.light.diffuse)
        self.shaders[shader].setVec3(b'light.position',self.light.pos)
        self.shaders[shader].setVec3(b'light.ambient',self.light.ambient)
        self.shaders[shader].setFloat(b'light.constant',self.light.constant)
        self.shaders[shader].setFloat(b'light.linear',self.light.linear)
        self.shaders[shader].setFloat(b'light.quadratic',self.light.quadratic)
        self.objects["obj"].draw()

        # self.model_matrix = glm.mat4(1.0)
        # self.model_matrix = glm.translate(self.model_matrix, glm.vec3(2,0,0))
        # self.model_matrix = glm.rotate(self.model_matrix, math.radians(-90),(1,0,0))
        # self.model_matrix = glm.rotate(self.model_matrix, math.radians(180),(0,0,1))
        # self.model_matrix = glm.scale(self.model_matrix, glm.vec3(2.0))            
    
        # self.shaders[shader].setMat4(b'model',self.model_matrix)
        # self.shaders[shader].setMat4(b'view',self.view_matrix)
        # self.shaders[shader].setMat4(b'projection',self.projection_matrix)
        # self.shaders[shader].setVec3(b'objectColor',(1.3,0.8,0.31))
        # self.objects["pikachu"].draw()

        # move the light in the Z plane.
        
        
        a,b,c = self.light.pos
        self.light.pos = [  5.0 * math.cos(math.radians(self.angle)) ,b, 5.0 * math.sin(math.radians(self.angle)) ]
        self.angle += 0.1
        self.angle = self.angle % 360.0

        self.model_matrix = glm.mat4(1.0)
        self.model_matrix = glm.translate(self.model_matrix, self.light.pos)
        self.model_matrix = glm.scale(self.model_matrix, glm.vec3(0.2))
        self.shaders["plain"].use()
        self.shaders["plain"].setMat4(b'model',self.model_matrix)
        self.shaders["plain"].setMat4(b'view',self.view_matrix)
        self.shaders["plain"].setMat4(b'projection',self.projection_matrix)
        self.shaders["plain"].setVec3(b'color',(1.0,1.0,1.0))
        self.objects["cube"].draw()

        self.model_matrix = glm.mat4(1.0)
        self.shaders["color"].use()
        self.shaders["color"].setMat4(b'model',self.model_matrix)
        self.shaders["color"].setMat4(b'view',self.view_matrix)
        self.shaders["color"].setMat4(b'projection',self.projection_matrix)
        self.objects["axis"].draw()

    def main(self, points=None):

        self.init()
        # all gl calls must be done AFTER init() or doesn't work
        obj = GLObj("Models/mayacube.obj")
        #obj = GLObj("Models/cube.obj")
        #obj = GLObj("Models/Charizard.obj")
        #obj = GLObj("Models/pikachu.obj")
        obj.load()
        
        cube = pyGLLib.object.GLCube()
        cube.load()
        axis = pyGLLib.object.GLAxis()
        axis.load()

        self.load_callbacks()
        self.load_shaders()
        self.set_light()
        self.set_camera()


        self.add_object("cube", cube)
        self.add_object("axis", axis)
        self.add_object("obj", obj)
        self.run()
        self.cleanup()

if __name__ == "__main__":

    #points = map_gpx(sys.argv[1])

    #points = []
    #from line import bresenham
    #points += bresenham((0,0),(10,10),5.0)
    #points += bresenham((0,10),(10,0),5.0)

    
    

    app = pyObjViewer( (800,600),  "pyObjViewer Sample App", shadows=True, wireframe=False)
    app.main()
    


