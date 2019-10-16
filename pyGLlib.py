#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////////////////
#
# pyGLLib.py
# Juan M. Casillas <juanm.casillas@gmail.com>
#
# ///////////////////////////////////////////////////////////////////////////

import glfw
from   OpenGL import GL, GLU, GLUT
from   OpenGL.arrays import vbo
from   OpenGL.GL import shaders
from   OpenGL.raw.GL import _types

import numpy as np
import ctypes

import sys
import time
import math
import glm 
import cv2
import logging
logging.basicConfig(level=logging.DEBUG)


# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLObjectBase:
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

class GLObjectBaseEBO(GLObjectBase):
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
class GLShaderBase:
    def __init__(self):
        # vertex shader (deals with the geometric transformations)
        # this version is a plain color.
        self.program = None
        self.vertex_shader = """
            #version 330 core
            layout(location = 0) in vec3 aPos; 
            uniform vec3 color;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            
            out vec3 ourColor;    // color output to fragment shader
    
            void main() {
            // transform vertex
                gl_Position = projection * view * model * vec4(aPos, 1.0); 
                ourColor = color; // Set the color to the input color from the vertex data
            }
            """

        # fragment shader (deals with the color)
        self.fragment_shader = """
            #version 330 core
             in vec3 ourColor;
             out vec4 FragColor;
             void main() {
                 FragColor = vec4(ourColor, 1.0f);
             }
            """

    def load(self, vertex=None, fragment=None):

        vertex_s   = vertex or self.vertex_shader
        fragment_s = fragment or self.fragment_shader

        vertexShader   = shaders.compileShader(vertex_s,   GL.GL_VERTEX_SHADER)
        fragmentShader = shaders.compileShader(fragment_s, GL.GL_FRAGMENT_SHADER)
        
        self.program = GL.glCreateProgram()
        if not self.program:
            raise RunTimeError('glCreateProgram faled!')

        # attach shaders
        GL.glAttachShader(self.program, vertexShader)
        GL.glAttachShader(self.program, fragmentShader)

        # Link the program
        GL.glLinkProgram(self.program)

        # check if ok.
        linked = GL.glGetProgramiv(self.program, GL.GL_LINK_STATUS)
        if not linked:
            infoLen = GL.glGetProgramiv(self.program, GL.GL_INFO_LOG_LENGTH)
            infoLog = ""
            if infoLen > 1:
                infoLog = GL.glGetProgramInfoLog(self.program, infoLen, None);
            GL.glDeleteProgram(self.program)
            raise RunTimeError("Error linking program:\n%s\n", infoLog);

        GL.glDeleteShader(vertexShader)
        GL.glDeleteShader(fragmentShader)

    def use(self):
        GL.glUseProgram(self.program)

    def setMat4(self, name,  matrix):
         GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.program, name),  
                               1, 
                               GL.GL_FALSE, 
                               glm.value_ptr(matrix)
                               )
    
    def setVec3(self, name, vec):
        GL.glUniform3fv(GL.glGetUniformLocation(self.program, name),  
                        1, 
                        list(vec))
        

class GLShaderPlain(GLShaderBase):
    def __init__(self):
        super().__init__()

class GLShaderVertexColor(GLShaderBase):
    "the default shader, supports basic color from vertex"
    def __init__(self):
        super().__init__()
        self.vertex_shader = """
            #version 330 core
            layout(location = 0) in vec3 aPos;
            layout (location = 1) in vec3 color;     // color variable has attribute position 1
    
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            
            out vec3 ourColor;    // color output to fragment shader
    
            void main() {
            // transform vertex
                gl_Position = projection * view * model * vec4(aPos, 1.0); 
                ourColor = color; // Set the color to the input color from the vertex data
            }
            """

        # fragment shader (deals with the color)
        self.fragment_shader = """
            #version 330 core
             in vec3 ourColor;
             out vec4 FragColor;
             void main() {
                 FragColor = vec4(ourColor, 1.0f);
             }
            """        


# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLLight:
    def __init__(self):
        self.pos = glm.vec3(0, 0.5, 3.0)
        self.color = glm.vec3(1.0, 1.0, 1.0)
        self.object = glm.vec3(1.0, 0.5, 0.31)
        self.pos_id = None
        self.color_id = None
        self.object_id = None


# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLCamera:
    def __init__(self, size):
        
        self.size = size
        self.width, self.height = self.size
        self.Defaults()

        self.dir = glm.normalize(self.pos - self.target)
        self.right = glm.normalize(glm.cross(self.up, self.dir))
        self.up2 = glm.cross(self.dir, self.right)
        self.first_time = True
        self.sensitivity = 0.1

      # time variables
        self.delta_time = 0.0
        self.last_frame = 0.0

    def Defaults(self):
        self.target = glm.vec3(0.0, 0.0, 0.0)
        self.pos =  glm.vec3(0.0,  0.0, 3.0)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.fov = 45
        self.speed = 0.05
        self.last_X = self.width/2.0
        self.last_Y = self.height/2.0
        self.yaw = -90.0
        self.pitch = 0.0        

# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLApp:
    def __init__(self,size,title, bgcolor = [0.1,0.1,0.1,0.1], wireframe=False, grabmouse=False):
        self.size=size
        self.width, self.height = self.size
        self.aspect = self.width/(float(self.height))
        self.title=title
        self.bgcolor = bgcolor
        self.wireframe = wireframe
        self.grabmouse = grabmouse

        # gl stuff
        self.window = None
        self.model_matrix = None
        self.view_matrix = None
        self.projection_matrix = None

        # cameras
        self.camera = GLCamera(self.size)

        # lights
        #self.light = GLLight()

        # shaders
        self.shaders = {}

        # objects
        self.objects = {}


    def init(self):

        # init the GLFW library (for managing the window)
        if not glfw.init():
            return        

        # select the OpenGL 3.3 with CORE_PROFILE ("new")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(self.width,self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            return  
        
        # create the openGL context
        glfw.make_context_current(self.window)
        GL.glViewport(0, 0, self.width,self.height)
        GL.glClearColor(self.bgcolor[0],               # This Will Clear The Background Color To Black
                        self.bgcolor[1], 
                        self.bgcolor[2],
                        self.bgcolor[3])    
        GL.glClearDepth(1.0)                            # Enables Clearing Of The Depth Buffer
        GL.glDepthFunc(GL.GL_LESS)                      # The Type Of Depth Test To Do
        GL.glEnable(GL.GL_DEPTH_TEST)                   # Enables Depth Testing

        if self.wireframe:
           GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)   # wireframe
        else:
           GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)  # solid

        if self.grabmouse:
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)


    def load_shaders(self):
        # set the shaders

        s = GLShaderPlain()
        s.load()
        self.shaders["plain"] = s


        s = GLShaderVertexColor()
        s.load()
        self.shaders["color"] = s


    def set_objects(self):

        m = GLObjectBase()
        m.load()
        self.objects["base"] = m

        m = GLObjectBaseEBO()
        m.load()
        self.objects["ebo"] = m

 


    # callback for the window

    def load_callbacks(self):
        glfw.set_key_callback(self.window       , self.key_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_callback)
        glfw.set_scroll_callback(self.window    , self.scroll_callback)        

    def key_callback(self,window,key,scancode,action,mods):


        camera_speed = 20.5 * self.camera.delta_time

        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window,glfw.TRUE)

        if key == glfw.KEY_ENTER and action == glfw.PRESS:
            self.camera.Defaults()         

        if key == glfw.KEY_W and action in [glfw.PRESS, glfw.REPEAT]:
            self.camera.pos += camera_speed * self.camera.front
        if key == glfw.KEY_S and action in [glfw.PRESS, glfw.REPEAT]:
            self.camera.pos -= camera_speed * self.camera.front

        if key == glfw.KEY_A and action in [glfw.PRESS, glfw.REPEAT]:
            self.camera.pos -= glm.normalize(glm.cross(self.camera.front, self.camera.up)) * camera_speed
        if key == glfw.KEY_D and action in [glfw.PRESS, glfw.REPEAT]:
            self.camera.pos += glm.normalize(glm.cross(self.camera.front, self.camera.up)) * camera_speed



    def cursor_callback(self,window, xpos, ypos):
        ## print("cursor_callback: xpos: %3.3f, ypos: %3.3f" % (xpos,ypos))
        if self.camera.first_time:
            self.camera.last_X = xpos
            self.camera.last_Y = ypos
            self.camera.first_time = False
   
        xoffset = xpos - self.camera.last_X
        yoffset = self.camera.last_Y - ypos
        self.camera.last_X = xpos
        self.camera.last_Y = ypos
        
        xoffset *= self.camera.sensitivity
        yoffset *= self.camera.sensitivity

        self.camera.yaw   += xoffset
        self.camera.pitch += yoffset

        if self.camera.pitch > 89.0:
            self.camera.pitch = 89.0
        if self.camera.pitch < -89.0:
            self.camera.pitch = -89.0

        front = glm.vec3()
        front.x = math.cos(glm.radians(self.camera.yaw)) * math.cos(glm.radians(self.camera.pitch))
        front.y = math.sin(glm.radians(self.camera.pitch))
        front.z = math.sin(glm.radians(self.camera.yaw)) * math.cos(glm.radians(self.camera.pitch))
        self.camera.front = glm.normalize(front)

    
    def scroll_callback(self, window,xoffset, yoffset):
        #print("scroll_callback: xoffset: %3.3f, yoffset: %3.3f" % (xoffset,yoffset))
        if self.camera.fov >= 1.0 and self.camera.fov <= 45.0:
            self.camera.fov -= yoffset
        if self.camera.fov <= 1.0:
            self.camera.fov = 1.0
        if self.camera.fov >= 45.0:
            self.camera.fov = 45.0

    def run(self):

        while not glfw.window_should_close(self.window):

            # ///////////////////////////////////////////////////////////////////////////
            # Render here, e.g. using pyOpenGL

            current_frame = glfw.get_time()
            self.camera.delta_time = current_frame - self.camera.last_frame
            self.camera.last_frame = current_frame


            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            

            #render

            self.projection_matrix = glm.perspective(glm.radians(self.camera.fov), self.aspect, 0.1, 100.0)
            self.view_matrix = glm.lookAt(self.camera.pos, self.camera.pos + self.camera.front, self.camera.up)

            # bind VAO
            try:
                # to the left
                self.model_matrix = glm.mat4(1.0)
                self.model_matrix = glm.translate(self.model_matrix, (-0.5,0,0))
                self.model_matrix = glm.scale(self.model_matrix, glm.vec3(0.5))
                
                self.shaders["plain"].use()
                self.shaders["plain"].setMat4(b'model',self.model_matrix)
                self.shaders["plain"].setMat4(b'view',self.view_matrix)
                self.shaders["plain"].setMat4(b'projection',self.projection_matrix)
                self.shaders["plain"].setVec3(b'color',(1.0,0.5,0.5))
                self.objects["base"].draw()

                # to the right
                self.model_matrix = glm.mat4(1.0)
                self.model_matrix = glm.translate(self.model_matrix, (0.5,0,0))
                self.model_matrix = glm.scale(self.model_matrix, glm.vec3(1.1))

                self.shaders["color"].use()
                self.shaders["color"].setMat4(b'model',self.model_matrix)
                self.shaders["color"].setMat4(b'view',self.view_matrix)
                self.shaders["color"].setMat4(b'projection',self.projection_matrix)
                self.objects["ebo"].draw()
            finally:
                # unbind VAO
                GL.glBindVertexArray(0)
                GL.glUseProgram(0)

            # ///////////////////////////////////////////////////////////////////////////
            # Swap front and back buffers
            glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()

        glfw.terminate()

    def cleanup(self):
        glfw.terminate()




if __name__ == "__main__":

    app = GLApp( (800,600), "PyGLLib Sample App", wireframe=True, grabmouse=True)
    app.init()
    app.load_shaders()
    app.load_callbacks()
    
    ##app.set_light()
    app.set_objects()
    app.run()
    app.cleanup()

    