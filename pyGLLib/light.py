
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