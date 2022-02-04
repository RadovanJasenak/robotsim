import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np
import ctypes


class App:
    # creating and checking window
    def __init__(self, width: int, height: int, title: str):
        if not glfw.init():
            raise Exception("glfw can not be initialized")
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created")

        glfw.set_window_pos(self.window, 400, 200)
        glfw.make_context_current(self.window)

        glClearColor(0.2, 0.2, 0.2, 1)
        self.shader = self.create_shader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)
        self.square = Square()

        self.main_loop()

    def main_loop(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.shader)

            glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

            glfw.swap_buffers(self.window)
        glfw.terminate()

    def create_shader(self, vertexFilepath, fragmentFilepath):
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
        glDeleteProgram(self.shader)
        self.square.destroy()
        glfw.terminate()


class Square:
    def __init__(self):
        self.vertices = []
        self.get_vertices(0.4, 0.2)
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertex_count = 4

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def get_vertices(self, length: float, width: float):
        # only a square with center at 0,0
        self.vertices = [-width/2, -length/2, 0.0, 1.0, 0.0, 0.0,
                         width/2, -length/2, 0.0, 0.0, 1.0, 0.0,
                         -width/2, length/2, 0.0, 1.0, 1.0, 1.0,
                         width / 2, length / 2, 0.0, 0.0, 0.0, 1.0]

    def destroy(self):
        # free all buffer objects
        glDeleteBuffers(1, (self.vbo,))


if __name__ == '__main__':
    myapp = App(1200, 720, "title")
