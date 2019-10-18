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

    def setFloat(self, name, value):
        GL.glUniform1f(GL.glGetUniformLocation(self.program, name), value)

        

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

            struct Light {
                vec3 position;
                vec3 diffuse;
                vec3 color;
                vec3 ambient;

                float constant;
                float linear;
                float quadratic;
            };             
            uniform Light light;            
            uniform vec3 objectColor;

            void main()
            {
                // ambient
                
                vec3 ambient = light.ambient * light.color;
                
                // diffuse 
                vec3 norm = normalize(Normal);
                vec3 lightDir = normalize(light.position - FragPos);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = light.diffuse * diff * light.color;

                // attenuation
                float distance = length(light.position - FragPos);
                float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));    
                        
                //ambient  *= attenuation; 
                //diffuse  *= attenuation;
    
                vec3 result = (ambient + diffuse) * objectColor;
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

            struct Light {
                vec3 position;
                vec3 diffuse;
                vec3 color;
                vec3 ambient;

                float constant;
                float linear;
                float quadratic;
            };             
            uniform Light light;            
            uniform vec3 objectColor;

            void main()
            {
                // ambient
                
                vec3 ambient = light.ambient * light.color;
                
                // diffuse 
                vec3 norm = normalize(Normal);
                vec3 lightDir = normalize(light.position - FragPos);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = light.diffuse * diff * light.color;

                // attenuation
                float distance = length(light.position - FragPos);
                float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));    
                        
                ambient  *= attenuation; 
                diffuse  *= attenuation;

                vec3 result = (ambient + diffuse) * objectColor;
                FragColor = vec4(result, 1.0);
            } 
            """

# ///////////////////////////////////////////////////////////////////////////
#
# WIPWIP new Shader
# only work with this one
#
# ///////////////////////////////////////////////////////////////////////////
class GLShaderStandard(GLShaderBase):
    "support for pos,color,normal, uv"
    def __init__(self):
        # vertex shader (deals with the geometric transformations)
        # this version support ambient + diffuse lightning (normals)
        self.program = None
        self.vertex_shader = """
            #version 330 core
            layout (location = 0) in vec3 aPos;
            layout (location = 1) in vec3 aColor;
            layout (location = 2) in vec3 aNormal;
            layout (location = 3) in vec2 aTexCoord;

            out vec3 FragPos;
            out vec3 Color;
            out vec3 Normal;
            out vec2 TexCoord;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                FragPos = vec3(model * vec4(aPos, 1.0));
                gl_Position = projection * view * vec4(FragPos, 1.0);
                Color = aColor;
                Normal = aNormal;  
                TexCoord = aTexCoord;
            }
            """

        # fragment shader (deals with the color)
        self.fragment_shader = """
            #version 330 core
            in vec3 FragPos;  
            in vec3 Color;
            in vec3 Normal;  
            in vec2 TexCoord;
                        
            out vec4 FragColor;

            struct Light {
                vec3 position;
                vec3 diffuse;
                vec3 color;
                vec3 ambient;

                float constant;
                float linear;
                float quadratic;
            };             
            uniform Light light;            
            uniform vec3 objectColor;
            uniform sampler2D ourTexture;

            void main()
            {
                // ambient
                vec3 ambient = light.ambient * light.color;
                
                // diffuse 
                vec3 norm = normalize(Normal);
                vec3 lightDir = normalize(light.position - FragPos);
                float diff = max(dot(norm, lightDir), 0.0);
                vec3 diffuse = light.diffuse * diff * light.color;

                // attenuation
                float distance = length(light.position - FragPos);
                float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));    
                        
                ambient  *= attenuation; 
                diffuse  *= attenuation;

                vec3 result;

                if (objectColor != vec3(0.0, 0.0, 0.0)) {
                    result = (ambient + diffuse) * objectColor;
                } else {
                    result = (ambient + diffuse) * Color;
                }
                // check if texture
                // tb this
                //FragColor = vec4(result, 1.0);
                //FragColor = texture(ourTexture, TexCoord);
                FragColor = texture(ourTexture, TexCoord) * vec4(result, 1.0);
            } 
            """            