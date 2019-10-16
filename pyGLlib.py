#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////////////////
#
# pyGLLib.py
# Juan M. Casillas <juanm.casillas@gmail.com>
#
# ///////////////////////////////////////////////////////////////////////////

import pyGLLib

if __name__ == "__main__":

    app = pyGLLib.GLApp( (800,600), "PyGLLib Sample App", wireframe=True, grabmouse=True)
    app.init()
    app.load_shaders()
    app.load_callbacks()
    
    ##app.set_light()
    app.set_objects()
    app.run()
    app.cleanup()

    