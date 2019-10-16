#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////////////////
#
# pyGLLib.py
# Juan M. Casillas <juanm.casillas@gmail.com>
#
# ///////////////////////////////////////////////////////////////////////////

from terrain import Terrain,GLTerrain
import pyGLLib
import glm



class pyTerrain(pyGLLib.GLApp):
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

        s = pyGLLib.shader.GLShaderPlain()
        s.load()
        self.shaders["plain"] = s

        s = pyGLLib.shader.GLShaderVertexColor()
        s.load()
        self.shaders["color"] = s        

    def set_light(self):
        self.light.pos = (0.0, 1.0, 2.0)
        self.light.color = (1.0,1.0,1.0)

    def render(self):

        if not self.diffuse:
            self.shaders["ambient"].use()
            self.shaders["ambient"].setMat4(b'model',self.model_matrix)
            self.shaders["ambient"].setMat4(b'view',self.view_matrix)
            self.shaders["ambient"].setMat4(b'projection',self.projection_matrix)
            self.shaders["ambient"].setVec3(b'color',(1.0,0.5,0.5))
            self.shaders["ambient"].setVec3(b'lightColor',(1.0,1.0,1.0))
        else:
            self.shaders["diffuse"].use()
            self.shaders["diffuse"].setMat4(b'model',self.model_matrix)
            self.shaders["diffuse"].setMat4(b'view',self.view_matrix)
            self.shaders["diffuse"].setMat4(b'projection',self.projection_matrix)
            self.shaders["diffuse"].setVec3(b'objectColor',(1.0,0.5,0.31))
            self.shaders["diffuse"].setVec3(b'lightPos',self.light.pos)
            self.shaders["diffuse"].setVec3(b'lightColor',self.light.color)
        
        self.objects["terrain"].draw()

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
        terrain = GLTerrain((10,10))
        terrain.load()
        cube = pyGLLib.object.GLCube()
        cube.load()
        axis = pyGLLib.object.GLAxis()
        axis.load()

        self.load_callbacks()
        self.load_shaders()
        ##self.set_light()
        ##self.set_objects()
        self.add_object("terrain", terrain)
        self.add_object("cube", cube)
        self.add_object("axis", axis)
        self.run()
        self.cleanup()

if __name__ == "__main__":

    app = pyTerrain( (800,600), "pyTerrain Sample App")
    app.main()
    


