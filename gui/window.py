import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np
import ctypes
from src.robot import Robot
import pyrr


class App:
    # creating and checking glfw window
    def __init__(self, robot: Robot):
        if not glfw.init():
            raise Exception("glfw can not be initialized")
        self.window = glfw.create_window(1920, 1080, "RobotSim", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created")

        glfw.set_window_pos(self.window, 400, 200)
        glfw.set_window_size_callback(self.window, self.window_resize)  # window resizing
        glfw.make_context_current(self.window)  # openGL context

        glClearColor(0.2, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)

        # create openGL shaders, vertex and fragment
        self.shader = self.create_shader("gui/shaders/vertex.txt", "gui/shaders/fragment.txt")
        glUseProgram(self.shader)

        self.rotation_location = glGetUniformLocation(self.shader, "rotation")

        self.square = Square(robot.base_link.length, robot.base_link.width)
        self.cube = Cube(robot.base_link.length, robot.base_link.width, robot.base_link.height)

        self.main_loop()

    def main_loop(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()  # check for glfw events

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # refresh screen
            glUseProgram(self.shader)  # here to make sure the correct one is being used

            rot_x = pyrr.Matrix44.from_x_rotation(0.5 * glfw.get_time())
            rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())
            glUniformMatrix4fv(self.rotation_location, 1, GL_FALSE, pyrr.matrix44.multiply(rot_x, rot_y))

            glBindVertexArray(self.cube.vao)  # bind the VAO that is being drawn
            glDrawElements(GL_TRIANGLES, len(self.cube.indices), GL_UNSIGNED_INT, None)

            glBindVertexArray(self.square.vao)  # bind the VAO that is being drawn
            glDrawElements(GL_TRIANGLES, len(self.square.indices), GL_UNSIGNED_INT, None)

            glfw.swap_buffers(self.window)  # swap buffers - double buffering
        self.quit()

    def create_shader(self, vertexFilepath, fragmentFilepath):
        # load shaders from files and compile them to be used as a program
        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        return shader

    def quit(self):
        # free allocated space before exiting
        glDeleteProgram(self.shader)
        self.square.destroy()
        self.cube.destroy()
        glfw.terminate()

    def window_resize(self, window, width, height):
        # window resizing function
        glViewport(0, 0, width, height)


class Square:
    def __init__(self, length, width):
        self.vertices = [-0.8, 0.8, 0.0, 1.0, 0.0, 0.0,
                         -0.8, 0.5, 0.0, 0.0, 1.0, 0.0,
                         -0.5,  0.5, 0.0, 0.0, 0.0, 1.0,
                         -0.5, 0.8, 0.0, 1.0, 1.0, 1.0]
        # self.vertices = []
        # self.get_vertices(length, width)
        self.indices = [0, 1, 2,
                        0, 2, 3]  # describes which vertices will be used to draw to avoid re-drawing existing vertices
        # make numpy arrays to work with openGL
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)

        self.vao = glGenVertexArrays(1)  # create vertex array object
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)  # create vertex buffer object and send data to GPU
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)  # create element buffer object and send data to GPU
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # describing data stored in VBO, 0 - location, 1 - color
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def get_vertices(self, length: float, width: float):
        # only a square with center at 0,0
        # first 3 numbers are XYZ, 3 more are RGB
        self.vertices = [-width/2, -length/2, 0.0, 1.0, 0.0, 0.0,
                         width/2, -length/2, 0.0, 0.0, 1.0, 0.0,
                         -width/2, length/2, 0.0, 0.0, 0.0, 1.0,
                         width/2, length/2, 0.0, 1.0, 1.0, 1.0]

    def destroy(self):
        # free all buffer objects
        glDeleteBuffers(2, (self.vbo, self.ebo))
        glDeleteVertexArrays(1, (self.vao,))


class Cube:
    def __init__(self, length, width, height):
        self.vertices = []
        self.get_vertices(length, width, height)
        self.indices = [0, 1, 2, 2, 3, 0,
                        4, 5, 6, 6, 7, 4,
                        4, 5, 1, 1, 0, 4,
                        6, 7, 3, 3, 2, 6,
                        5, 6, 2, 2, 1, 5,
                        7, 4, 0, 0, 3, 7
                        ]  # describes which vertices will be used to draw to avoid re-drawing existing vertices
        # make numpy arrays to work with openGL
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)

        self.vao = glGenVertexArrays(1)  # create vertex array object
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)  # create vertex buffer object and send data to GPU
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)  # create element buffer object and send data to GPU
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # describing data stored in VBO, 0 - location, 1 - color
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def get_vertices(self, length: float, width: float, height: float):
        # only a square with center at 0,0
        # first 3 numbers are XYZ, 3 more are RGB
        self.vertices = [-width/2, -length/2, height/2, 1.0, 0.0, 0.0,
                         width/2, -length/2, height/2, 0.0, 1.0, 0.0,
                         width / 2, length / 2, height / 2, 1.0, 1.0, 1.0,
                         -width/2, length/2, height/2, 0.0, 0.0, 1.0,

                         -width / 2, -length / 2, -height / 2, 0.0, 1.0, 0.0,
                         width / 2, -length / 2, -height/2, 1.0, 0.0, 0.0,
                         width / 2, length / 2, -height/2, 0.0, 0.0, 1.0,
                         -width / 2, length / 2, -height/2, 1.0, 1.0, 1.0
                         ]

    def destroy(self):
        # free all buffer objects
        glDeleteBuffers(2, (self.vbo, self.ebo))
        glDeleteVertexArrays(1, (self.vao,))
