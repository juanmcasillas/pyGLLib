from   OpenGL import GL, GLU, GLUT
from   OpenGL.arrays import vbo
from   OpenGL.GL import shaders
import glm

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
            raise RuntimeError('glCreateProgram faled!')

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
                infoLog = GL.glGetProgramInfoLog(self.program)
            GL.glDeleteProgram(self.program)
            raise RuntimeError("Error linking program:\n%s\n", infoLog)

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
        

# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLShaderPlain(GLShaderBase):
    def __init__(self):
        super().__init__()

# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
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
class GLShaderAmbient(GLShaderBase):
    "support for ambient light"
    def __init__(self):
        # vertex shader (deals with the geometric transformations)
        # this version is a plain color.
        self.program = None
        self.vertex_shader = """
            #version 330 core
            layout(location = 0) in vec3 aPos; 
            uniform vec3 color;
            uniform vec3 lightColor;
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
            
            out vec3 objectColor;    // color output to fragment shader
            out vec3 lightColorOut;    // color output to fragment shader
            void main() {
            // transform vertex
                gl_Position = projection * view * model * vec4(aPos, 1.0); 

            // color
                objectColor = color; // Set the color to the object color
                lightColorOut = lightColor;
            }
            """

        # fragment shader (deals with the color)
        self.fragment_shader = """
            #version 330 core
             in vec3 objectColor;
             in vec3 lightColorOut;
             out vec4 FragColor;
             void main() {
                    float ambientStrength = 0.1;
                    vec3 ambient = ambientStrength * lightColorOut;

                    vec3 result = ambient * objectColor;
                    FragColor = vec4(result, 1.0);
             }
            """

# ///////////////////////////////////////////////////////////////////////////
#
#
#
# ///////////////////////////////////////////////////////////////////////////
class GLShaderDiffuse(GLShaderBase):
    "support for ambient light"
    def __init__(self):
        # vertex shader (deals with the geometric transformations)
        # this version support ambient + diffuse lightning (normals)
        self.program = None
        self.vertex_shader = """
            #version 330 core
            layout (location = 0) in vec3 aPos;
            layout (location = 1) in vec3 aNormal;

            out vec3 FragPos;
            out vec3 Normal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                FragPos = vec3(model * vec4(aPos, 1.0));
                Normal = aNormal;  
                gl_Position = projection * view * vec4(FragPos, 1.0);
            }
            """

        # fragment shader (deals with the color)
        self.fragment_shader = """
            #version 330 core
            out vec4 FragColor;

            in vec3 Normal;  
            in vec3 FragPos;  
            
            uniform vec3 lightPos; 
            uniform vec3 lightColor;
            uniform vec3 objectColor;

            void main()
            {
                // ambient
                float ambientStrength = 0.1;
                vec3 ambient = ambientStrength * lightColor;
                
                // diffuse 
                vec3 norm = normalize(Normal);
                vec3 lightDir = normalize(lightPos - FragPos);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = diff * lightColor;
                        
                vec3 result = (ambient + diffuse) * objectColor;
                FragColor = vec4(result, 1.0);
            } 
            """