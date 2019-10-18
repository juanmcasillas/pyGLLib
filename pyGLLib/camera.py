import glm 

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
        self.pos =  glm.vec3(0.0,  0.0, 8.0)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.fov = 45
        self.speed = 50
        self.last_X = self.width/2.0
        self.last_Y = self.height/2.0
        self.yaw = -90.0
        self.pitch = 0.0       