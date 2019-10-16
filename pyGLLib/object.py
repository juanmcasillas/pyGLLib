import numpy as np
import ctypes
from   OpenGL import GL, GLU, GLUT
from   OpenGL.arrays import vbo
from   OpenGL.GL import shaders
from   OpenGL.raw.GL import _types
# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLObjectBase:
    "loads a basic quad, formed by 2 triangles"
    def __init__(self):
        # data model
        self.vertexData = None
        self.triangles = None
        # buffers
        self.VAO = None  # Vertex Array Object
        self.VBO = None  # Vertex Buffer Object

    def load_model(self):
        vertexData = np.array([
            # first triangle
            # Positions       # Color     
             0.5,  0.5, 0.0,  # top right
             0.5, -0.5, 0.0,  # bottom right
            -0.5,  0.5, 0.0,  # top left
            # second triangle
             0.5, -0.5, 0.0,  # bottom right
            -0.5, -0.5, 0.0,  # bottom left
            -0.5,  0.5, 0.0,  # top left
        ], dtype=np.float32)

        triangles = 2
        self.vertexData = vertexData
        self.triangles = triangles

    def load(self):

        self.load_model()
        self.VAO = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.VAO)

        # Need VBO for triangle vertices
        self.VBO = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertexData.nbytes, self.vertexData, GL.GL_STATIC_DRAW)

        # enable array and set up data - calculating stride length, wow; not documented
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, (3 * ctypes.sizeof(_types.GLfloat)), None)
        GL.glEnableVertexAttribArray(0)

        # Unbind so we don't mess w/ them
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)         

    def draw(self):

         GL.glBindVertexArray(self.VAO)
         GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertexData.size)


# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLObjectBaseEBO(GLObjectBase):
    "load a quad formed by two triangles, with per-vertex color, and EBO (indexing drawing)"
    def __init__(self):
        super().__init__()

        #data model
        self.indexData = None

        #buffer
        self.EBO = None  # Element Buffer Object (indexes)

    def load_model(self):

        vertexData = np.array([
            # Positions       # Color        
            0.5,  0.5, 0.0,   1.0, 0.0, 0.0, # Top Right
            0.5, -0.5, 0.0,   0.0, 1.0, 0.0, # Bottom Right
            -0.5, -0.5, 0.0,  0.0, 0.0, 1.0, # Bottom Left
            -0.5,  0.5, 0.0,  1.0, 1.0, 0.0, # Top Left
        ], dtype=np.float32)

        indexData = np.array([
            0, 1, 2, # First Triangle
            0, 2, 3, # Second Triangle
        ], dtype=np.uint32)

        triangles = 2
        self.vertexData = vertexData
        self.indexData = indexData
        self.triangles = triangles

    def load(self):
        super().load()
        
        # bind to VAO to add the EBO...
        GL.glBindVertexArray(self.VAO)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO)

        # enable array and set up data - calculating stride length, wow; not documented
        # 6 -> 3 pos, 3 color Array(0)->Pos (See Vertex Shader)
        # 9 -> 3 pos, 3 color Array(0)->Pos (See Vertex Shader), 3 -> 9 normals
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, (6 * ctypes.sizeof(_types.GLfloat)), None)
        GL.glEnableVertexAttribArray(0)

        # I like how offsets aren't documented either; http://pyopengl.sourceforge.net/documentation/manual-3.0/glVertexAttribPointer.html
        # offsets https://twistedpairdevelopment.wordpress.com/2013/02/16/using-array_buffers-in-pyopengl/
        # http://stackoverflow.com/questions/11132716/how-to-specify-buffer-offset-with-pyopengl
        # Again, 6 -> 3 pos, 3 color Array(1)->Color (see Vertex shader)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 
                        (6 * ctypes.sizeof(_types.GLfloat)), 
                        ctypes.c_void_p((3 * ctypes.sizeof(_types.GLfloat))))
        GL.glEnableVertexAttribArray(1)



        # Make a EBO buffer here based on indexData
        self.EBO = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indexData.nbytes, self.indexData, GL.GL_STATIC_DRAW)         
        
        # Unbind so we don't mess w/ them
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)     

    def draw(self):
         GL.glBindVertexArray(self.VAO)
         GL.glDrawElements(GL.GL_TRIANGLES, self.indexData.size, GL.GL_UNSIGNED_INT, None)


# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLCube(GLObjectBase):
    "a cube, built with triangles, and normals. Useful to test light"
    def __init__(self):
        super().__init__()

    def load_model(self):
        vertexData = np.array([
            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
             0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 
             0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 
             0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 
            -0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 
            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 

            -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,
             0.5, -0.5,  0.5,  0.0,  0.0, 1.0,
             0.5,  0.5,  0.5,  0.0,  0.0, 1.0,
             0.5,  0.5,  0.5,  0.0,  0.0, 1.0,
            -0.5,  0.5,  0.5,  0.0,  0.0, 1.0,
            -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,

            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
            -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,
            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
            -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,
            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,

            0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
            0.5,  0.5, -0.5,  1.0,  0.0,  0.0,
            0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
            0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
            0.5, -0.5,  0.5,  1.0,  0.0,  0.0,
            0.5,  0.5,  0.5,  1.0,  0.0,  0.0,

            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
             0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
             0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
             0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
            -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,

            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
             0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
             0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
             0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
            -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0
        ], dtype=np.float32)

        self.vertexData = vertexData
        self.triangles = 12 # 2 triangles x 6 faces

    def load(self):
        super().load()
        
        # bind to VAO to add the normals at
        GL.glBindVertexArray(self.VAO)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO)

        # enable array and set up data - calculating stride length, wow; not documented
        # 6 -> 3 pos, 3 normal Array(0)->Pos (See Vertex Shader)

        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, (6 * ctypes.sizeof(_types.GLfloat)), None)
        GL.glEnableVertexAttribArray(0)

        # I like how offsets aren't documented either; http://pyopengl.sourceforge.net/documentation/manual-3.0/glVertexAttribPointer.html
        # offsets https://twistedpairdevelopment.wordpress.com/2013/02/16/using-array_buffers-in-pyopengl/
        # http://stackoverflow.com/questions/11132716/how-to-specify-buffer-offset-with-pyopengl
        # Again, 6 -> 3 pos, 3 normal Array(1)->Normals (see Vertex shader)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 
                        (6 * ctypes.sizeof(_types.GLfloat)), 
                        ctypes.c_void_p((3 * ctypes.sizeof(_types.GLfloat))))
        GL.glEnableVertexAttribArray(1)
       
        # Unbind so we don't mess w/ them
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)             