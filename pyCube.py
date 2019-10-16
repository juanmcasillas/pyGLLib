#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////////////////
#
# pyGLLib.py
# Juan M. Casillas <juanm.casillas@gmail.com>
#
# ///////////////////////////////////////////////////////////////////////////

import pyGLLib
import glm


class pyCube(pyGLLib.GLApp):
    def __init__(self, size, title, wireframe=False, grabmouse=True, diffuse=True):
        super().__init__(size, title, wireframe=wireframe, grabmouse=grabmouse )

        self.diffuse = diffuse

    def load_shaders(self):
        s = pyGLLib.shader.GLShaderAmbient()
        s.load()
        self.shaders["ambient"] = s

        s = pyGLLib.shader.GLShaderDiffuse()
        s.load()
        self.shaders["diffuse"] = s

        s = pyGLLib.shader.GLShaderVertexColor()
        s.load()
        self.shaders["color"] = s             

        s = pyGLLib.shader.GLShaderPlain()
        s.load()
        self.shaders["plain"] = s

    def set_light(self):
        self.light.pos = (0, 1.0, 1.0)
        self.light.color = (1.0,1.0,1.0)

    def set_camera(self):
        self.camera.pos = ( 3 ,3, 10)  

    def render(self):

        if not self.diffuse:
            self.shaders["ambient"].use()
            self.shaders["ambient"].setMat4(b'model',self.model_matrix)
            self.shaders["ambient"].setMat4(b'view',self.view_matrix)
            self.shaders["ambient"].setMat4(b'projection',self.projection_matrix)
            self.shaders["ambient"].setVec3(b'objectColor',(1.0,0.5,0.5))
            self.shaders["ambient"].setVec3(b'light.color',self.light.color)
            self.shaders["ambient"].setVec3(b'light.diffuse',self.light.diffuse)
            self.shaders["ambient"].setVec3(b'light.position',self.light.pos)
            self.shaders["ambient"].setVec3(b'light.ambient',self.light.ambient)
            self.shaders["ambient"].setFloat(b'light.constant',self.light.constant)
            self.shaders["ambient"].setFloat(b'light.linear',self.light.linear)
            self.shaders["ambient"].setFloat(b'light.quadratic',self.light.quadratic)
    
        else:
            self.shaders["diffuse"].use()
            self.shaders["diffuse"].setMat4(b'model',self.model_matrix)
            self.shaders["diffuse"].setMat4(b'view',self.view_matrix)
            self.shaders["diffuse"].setMat4(b'projection',self.projection_matrix)
            self.shaders["diffuse"].setVec3(b'objectColor',(1.0,0.5,0.31))
            self.shaders["diffuse"].setVec3(b'light.color',self.light.color)
            self.shaders["diffuse"].setVec3(b'light.diffuse',self.light.diffuse)
            self.shaders["diffuse"].setVec3(b'light.position',self.light.pos)
            self.shaders["diffuse"].setVec3(b'light.ambient',self.light.ambient)
            self.shaders["diffuse"].setFloat(b'light.constant',self.light.constant)
            self.shaders["diffuse"].setFloat(b'light.linear',self.light.linear)
            self.shaders["diffuse"].setFloat(b'light.quadratic',self.light.quadratic)
        
        self.objects["cube"].draw()

        # draw the "light"
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


    def main(self):

        self.init()
        # all gl calls must be done AFTER init() or doesn't work
        cube = pyGLLib.object.GLCube()
        cube.load()
        axis = pyGLLib.object.GLAxis()
        axis.load()        
        self.load_callbacks()
        self.load_shaders()
        self.set_light()
        self.set_camera()
        ##self.set_objects()
        self.add_object("cube", cube)
        self.add_object("axis", axis)
        self.run()
        self.cleanup()

if __name__ == "__main__":

    app = pyCube( (800,600), "PyGLLib Sample App")
    app.main()
    