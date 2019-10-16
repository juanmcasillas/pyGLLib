
# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLLight:
    def __init__(self, pos=(0.0,0.0,0.0), color=(1.0,1.0,1.0)):
        self.pos = pos
        self.color = color

        self.ambient = (0.5, 0.5, 0.5)
        self.diffuse = (0.5, 0.5, 0.5)
        # attenuation
        self.constant = 1.0
        self.linear = 0.09
        self.quadratic = 0.032
