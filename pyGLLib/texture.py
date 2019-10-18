import glm 
from PIL import Image
from   OpenGL import GL, GLU, GLUT
from   OpenGL.arrays import vbo
from   OpenGL.GL import shaders
from   OpenGL.raw.GL import _types

# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLTexture:
    def __init__(self,fname):
        self.id = None
        self.fname = fname
        

    def load(self):

        #load the image file
        im = Image.open(self.fname)
        try:
            ## Note the conversion to RGB the crate bitmap is paletted!
            im = im.convert( 'RGB')
            ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBA", 0, -1)
        except Exception:
            ix, iy, image = im.size[0], im.size[1], im.tobytes("raw", "RGBX", 0, -1)
        assert ix*iy*4 == len(image), """Image size != expected array size"""

        ##im.show()
        
        self.id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameteri( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
        #GL.glTexParameteri( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        #GL.glTexParameteri( GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, ix, iy, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

        return self