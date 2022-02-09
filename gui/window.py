import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np
import ctypes
from src.robot import Robot


class App:
    # creating and checking glfw window
    def __init__(self, robot: Robot):
        if not glfw.init():
            raise Exception("glfw can not be initialized")
        self.window = glfw.create_window(1920, 1080, "RobotSim", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created")

        glfw.set_window_pos(self.window, 2000, 400)
        glfw.set_window_size_callback(self.window, self.window_resize)  # window resizing
        glfw.make_context_current(self.window)  # openGL context

        glClearColor(0.2, 0.2, 0.2, 1)
        # create openGL shaders, vertex and fragment
        self.shader = self.create_shader("gui/shaders/vertex.txt", "gui/shaders/fragment.txt")
        glUseProgram(self.shader)

        self.square = Square(robot.base_link.length, robot.base_link.width)

        self.main_loop()

    def main_loop(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()  # check for glfw events

            glClear(GL_COLOR_BUFFER_BIT)  # refresh screen
            glUseProgram(self.shader)  # here to make sure the correct one is being used

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
        glfw.terminate()

    def window_resize(self, window, width, height):
        # window resizing function
        glViewport(0, 0, width, height)


class Square:
    def __init__(self, length, width):
        self.vertices = []
        self.get_vertices(length, width)
        self.indices = [0, 1, 2,
                        1, 2, 3]  # describes which vertices will be used to draw to avoid re-drawing existing vertices
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
                         width / 2, length / 2, 0.0, 1.0, 1.0, 1.0]

    def destroy(self):
        # free all buffer objects
        glDeleteBuffers(2, (self.vbo, self.ebo))
        glDeleteVertexArrays(1, (self.vao,))
