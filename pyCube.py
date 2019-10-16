#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////////////////
#
# pyGLLib.py
# Juan M. Casillas <juanm.casillas@gmail.com>
#
# ///////////////////////////////////////////////////////////////////////////

import pyGLLib


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

    def render(self):

        if not self.diffuse:
            self.shaders["ambient"].use()
            self.shaders["ambient"].setMat4(b'model',self.model_matrix)
            self.shaders["ambient"].setMat4(b'view',self.view_matrix)
            self.shaders["ambient"].setMat4(b'projection',self.projection_matrix)
            self.shaders["ambient"].setVec3(b'color',(1.0,0.5,0.5))
            self.shaders["ambient"].setVec3(b'ligtColor',(1.0,1.0,1.0))
        else:
            self.shaders["diffuse"].use()
            self.shaders["diffuse"].setMat4(b'model',self.model_matrix)
            self.shaders["diffuse"].setMat4(b'view',self.view_matrix)
            self.shaders["diffuse"].setMat4(b'projection',self.projection_matrix)
            self.shaders["diffuse"].setVec3(b'objectColor',(1.0,0.5,0.31))
            self.shaders["diffuse"].setVec3(b'lightPos',(1.2, 1.0, 2.0))
            self.shaders["diffuse"].setVec3(b'lightColor',(1.0,1.0,1.0))
        
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
    