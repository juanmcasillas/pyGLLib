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

from .camera import GLCamera
from .shader import GLShaderPlain, GLShaderVertexColor
from .object import GLObjectBase, GLObjectBaseEBO
from .light  import GLLight

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
        self.light = GLLight()

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

    def add_object(self, name, obj):
        self.objects[name] = obj

    # callback for the window

    def load_callbacks(self):
        glfw.set_key_callback(self.window       , self.key_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_callback)
        glfw.set_scroll_callback(self.window    , self.scroll_callback)        

    def key_callback(self,window,key,scancode,action,mods):


        camera_speed = self.camera.speed * self.camera.delta_time

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

        if key == glfw.KEY_Q and action in [glfw.PRESS, glfw.REPEAT]:
            self.camera.pos += self.camera.up * camera_speed
        if key == glfw.KEY_Z and action in [glfw.PRESS, glfw.REPEAT]:
            self.camera.pos -= self.camera.up * camera_speed

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

    def set_light(self):
        "override this"
        self.light.pos = (0.0, 0.0, 0.0)
        self.light.color = (1.0, 1.0, 1.0)

    def run(self):

        while not glfw.window_should_close(self.window):

            # ///////////////////////////////////////////////////////////////////////////
            # Render here, e.g. using pyOpenGL

            current_frame = glfw.get_time()
            self.camera.delta_time = current_frame - self.camera.last_frame
            self.camera.last_frame = current_frame

            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            
        
            # set view, model and projection matrices
            self.model_matrix = glm.mat4(1.0)
            self.projection_matrix = glm.perspective(glm.radians(self.camera.fov), self.aspect, 0.1, 100.0)
            self.view_matrix = glm.lookAt(self.camera.pos, self.camera.pos + self.camera.front, self.camera.up)

            # render the thing.
            try:
                self.render()
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

    def render(self):
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

    def cleanup(self):
        glfw.terminate()
        
    def main(self):
        self.init()
        self.load_shaders()
        self.load_callbacks()
        self.set_light()
        self.set_objects()
        self.run()
        self.cleanup()
