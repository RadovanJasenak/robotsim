import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np
import ctypes
import gui.graphics_components as gc
from src.robot import Robot
import pyrr


class App:
    # creating and checking glfw window
    def __init__(self, robot: Robot):
        if not glfw.init():
            raise Exception("glfw can not be initialized")
        self.window = glfw.create_window(1280, 720, "RobotSim", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created")

        glfw.set_window_pos(self.window, 400, 200)
        glfw.set_window_size_callback(self.window, self.window_resize)  # window resizing
        glfw.make_context_current(self.window)  # openGL context

        # create openGL shaders, vertex and fragment
        self.shader = self.create_shader("gui/shaders/vertex.txt", "gui/shaders/fragment.txt")
        glUseProgram(self.shader)

        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)

        # create perspective projection matrix
        self.projection = pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=1280/720,
            near=0.1, far=100.0)

        # translate (move) the object in world space
        self.robot_body_model_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([-0.5, 0, 0]))
        self.ground_position = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))
        self.mesh_model_translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([1, 0, 0]))

        # create view matrix, values are negated bc when camera moves to one direction, the scene moves to the opposite
        # eye - cannot be [0, 0, 0], target i am looking at , up vector of the camera
        self.look_at = pyrr.matrix44.create_look_at(
            pyrr.Vector3([0, 1, 4]),
            pyrr.Vector3([0, 0, 0]),
            pyrr.Vector3([0, 1, 0]))

        # get the uniform's location
        self.model_location = glGetUniformLocation(self.shader, "model")
        self.projection_location = glGetUniformLocation(self.shader, "projection")
        self.view_location = glGetUniformLocation(self.shader, "view")

        # upload the projection & view matrices to the shader
        glUniformMatrix4fv(
            self.projection_location, 1,
            GL_FALSE, self.projection
        )
        glUniformMatrix4fv(self.view_location, 1, GL_FALSE, self.look_at)

        self.robot_body = Cube(robot.base_link.length, robot.base_link.width, robot.base_link.height)
        #self.cube_mesh = Mesh("models/cube.obj")
        self.cube_mesh = gc.MeshLoader("models/cube.obj", robot.base_link.color)
        self.scene = Scene()

        self.main_loop()

    def main_loop(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()  # check for glfw events

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # refresh screen
            glUseProgram(self.shader)  # here to make sure the correct one is being used

            rot_x = pyrr.Matrix44.from_x_rotation(0.5 * glfw.get_time())
            rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())

            # draw a small rotating rectangle
            # rotation = pyrr.matrix44.multiply(rot_x, rot_y)
            # model = pyrr.matrix44.multiply(rotation, self.robot_body_model_translation)
            # glUniformMatrix4fv(self.model_location, 1, GL_FALSE, self.robot_body_model_translation)
            # glBindVertexArray(self.robot_body.vao)  # bind the VAO that is being drawn
            # glDrawElements(GL_TRIANGLES, len(self.robot_body.indices), GL_UNSIGNED_INT, None)

            # draw a mesh object
            scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.2, 0.4, 0.1]))
            glUniformMatrix4fv(self.model_location, 1, GL_FALSE, scale @ self.mesh_model_translation)
            glBindVertexArray(self.cube_mesh.vao)  # bind the VAO that is being drawn
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

            # scene floor plane model
            model = pyrr.matrix44.multiply(self.scene.ground_scale, self.ground_position)
            glUniformMatrix4fv(self.model_location, 1, GL_FALSE, model)
            glBindVertexArray(self.scene.ground.vao)  # bind the VAO that is being drawn
            glDrawArrays(GL_TRIANGLES, 0, self.scene.ground.vertex_count)

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
        self.cube_mesh.destroy()
        self.robot_body.destroy()
        self.scene.ground.destroy()
        glfw.terminate()

    def window_resize(self, window, width, height):
        # window resizing function
        glViewport(0, 0, width, height)
        projection_on_resize = pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=width/height,
            near=0.1, far=100.0)
        glUniformMatrix4fv(self.projection_location, 1, GL_FALSE, projection_on_resize)


class Square:
    def __init__(self, lengthX, lengthY, lengthZ):
        self.vertices = [-lengthX / 2, -lengthY / 2, lengthZ / 2, 1.0, 0.0, 0.0,
                         lengthX / 2, -lengthY / 2, lengthZ / 2, 0.0, 1.0, 0.0,
                         -lengthX / 2, lengthY / 2, -lengthZ / 2, 0.0, 0.0, 1.0,
                         lengthX / 2, lengthY / 2, -lengthZ / 2, 1.0, 1.0, 1.0]
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
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 6, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 6, ctypes.c_void_p(12))

    def get_vertices(self, length: float, width: float, height: float):
        # only a square with center at 0,0
        # first 3 numbers are XYZ, 3 more are RGB
        self.vertices = [-width/2, -length/2, height/2, 1.0, 0.0, 0.0,
                         width/2, -length/2, height/2, 0.0, 1.0, 0.0,
                         width/2, length/2, height/2, 1.0, 1.0, 1.0,
                         -width/2, length/2, height/2, 0.0, 0.0, 1.0,

                         -width/2, -length/2, -height/2, 0.0, 1.0, 0.0,
                         width/2, -length/2, -height/2, 1.0, 0.0, 0.0,
                         width/2, length/2, -height/2, 0.0, 0.0, 1.0,
                         -width/2, length/2, -height/2, 1.0, 1.0, 1.0
                         ]

    def destroy(self):
        # free all buffer objects
        glDeleteBuffers(2, (self.vbo, self.ebo))
        glDeleteVertexArrays(1, (self.vao,))


class Mesh:
    # for use with glDrawArrays
    def __init__(self, filepath):
        self.vertices = self.load_mesh(filepath)
        # need number of vertices
        self.vertex_count = len(self.vertices) // 6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)  # create vertex array object
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)  # create vertex buffer object and send data to GPU
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # describing data stored in .obj, 0 - location, 1 - texture, 2 - normal
        # data stored in VBO, 0 - position, 1 - color
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 6, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 6, ctypes.c_void_p(12))
        # glEnableVertexAttribArray(2)
        # glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 8, ctypes.c_void_p(20))

    def load_mesh(self, filepath):
        # data from .obj file
        v = []
        vn = []
        vt = []

        # completed VBO
        vertices = []

        # load the numbers into v, vt, vn
        with open(filepath, 'r') as f:
            line = f.readline()
            while line:
                line = line.split(" ")
                if line[0] == "v":
                    values = [float(x) for x in line[1:4]]  # convert from string to float
                    v.append(values)  # [x, y, z], [x, y, z], ...
                if line[0] == "vn":
                    values = [float(x) for x in line[1:4]]
                    vn.append(values)  # [x, y, z], [x, y, z], ...
                if line[0] == "vt":
                    values = [float(x) for x in line[1:3]]
                    vt.append(values)  # [s, t], [s, t], ...
                if line[0] == "f":
                    line.remove("f")  # ["1/1/1", "5/5/1", "7/9/1", ...]
                    f_vertices = []  # to store vertex info in a face [ 1, 5, 7, ...]
                    f_normals = []  # to store normal info in a face [ 1, 5, 9, ...]
                    f_textures = []  # to store texture info in a face [ 1, 1, 1, ...]
                    for vertex in line:
                        vertex = vertex.split("/")
                        # instead of storing 1,5,7 (index of the vertice in list v) append the value at that index in list v
                        f_vertices.append(v[int(vertex[0]) - 1])  # blender uses 1 indexing

                    number_of_triangles = len(line) - 2  # how many triangles are there in a face
                    vertex_order = []  # order in which to write the vertices to form triangles
                    for i in range(number_of_triangles):  # unpack vertices in a face [0, 1, 2, 3] -> [0, 1, 2, 0, 2, 3]
                        vertex_order.append(0)
                        vertex_order.append(i + 1)
                        vertex_order.append(i + 2)
                    for i in vertex_order:
                        for j in f_vertices[i]:  # to add x,y,z instead of [x,y,z]
                            vertices.append(j)
                        if i == 0:
                            vertices.append(1.0)
                            vertices.append(0.0)
                            vertices.append(0.0)
                        elif i == 1:
                            vertices.append(0.0)
                            vertices.append(1.0)
                            vertices.append(0.0)
                        else:
                            vertices.append(0.0)
                            vertices.append(0.0)
                            vertices.append(1.0)

                line = f.readline()

        return vertices

    def destroy(self):
        # free all buffer objects
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))


class Scene:
    def __init__(self):
        self.ground = gc.MeshLoader("models/plane.obj", [0.412, 0.412, 0.412, 1.0])
        self.ground_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([10.0, 10.0, 10.0]))
        self.robot = None


# class RobotVisual:
#     def __init__(self, robot: Robot):
#         self.meshes = []
#         for item in robot.links:
#             if item.shape == "box":
#                 self.meshes.append(Mesh("models/cube.obj"))
#             elif item.shape == "cylinder":
#                 self.meshes.append(Mesh("models/cylinder.obj"))
#             elif item.shape == "sphere":
#                 self.meshes.append(Mesh("models/sphere.obj"))
#             else:
#                 raise ValueError("Attempting to draw an object that is not a box, a cylinder or a sphere")
#
#     def create_model(self):
#         # connect the meshes of links with regard to joints
#         pass
