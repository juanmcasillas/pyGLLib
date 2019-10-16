#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////////////////
#
# pyGLLib.py
# Juan M. Casillas <juanm.casillas@gmail.com>
#
# ///////////////////////////////////////////////////////////////////////////

import pyGLLib


class pyCube(pyGLLib.GLApp):
    def __init__(self, size, title, wireframe=False, grabmouse=True):
        super().__init__(size, title, wireframe=wireframe, grabmouse=grabmouse )

    def load_shaders(self):
        s = pyGLLib.shader.GLShaderAmbient()
        s.load()
        self.shaders["ambient"] = s

    def render(self):
        #self.model_matrix = glm.mat4(1.0)
        #self.model_matrix = glm.translate(self.model_matrix, (-0.5,0,0))
        #self.model_matrix = glm.scale(self.model_matrix, glm.vec3(0.5))
        
        self.shaders["ambient"].use()
        self.shaders["ambient"].setMat4(b'model',self.model_matrix)
        self.shaders["ambient"].setMat4(b'view',self.view_matrix)
        self.shaders["ambient"].setMat4(b'projection',self.projection_matrix)
        self.shaders["ambient"].setVec3(b'color',(1.0,0.5,0.5))
        self.shaders["ambient"].setVec3(b'ligtColor',(1.0,1.0,1.0))
        self.objects["cube"].draw()

    def main(self):

        self.init()
        # all gl calls must be done AFTER init() or doesn't work
        cube = pyGLLib.object.GLCube()
        cube.load()
        self.load_callbacks()
        self.load_shaders()
        ##self.set_light()
        ##self.set_objects()
        self.add_object("cube", cube)
        self.run()
        self.cleanup()

if __name__ == "__main__":

    app = pyCube( (800,600), "PyGLLib Sample App")
    app.main()
    