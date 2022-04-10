from OpenGL.GL import *
import numpy as np
import ctypes


class MeshLoader:
    # for use with glDrawArrays
    def __init__(self, filepath, color):
        self.vertices = self.load_mesh(filepath, color)
        # need number of vertices
        self.vertex_count = len(self.vertices) // 6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)  # create vertex array object
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)  # create vertex buffer object and send data to GPU
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # describing data stored in .obj, 0 - location, 1 - texture, 2 - normal
        # data stored in VBO, 0 - location, 1 - color
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 7, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 7, ctypes.c_void_p(12))
        # glEnableVertexAttribArray(2)
        # glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, self.vertices.itemsize * 8, ctypes.c_void_p(20))

    def load_mesh(self, filepath, color):
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
                        for c in color:
                            vertices.append(c)

                line = f.readline()

        return vertices

    def destroy(self):
        # free all buffer objects
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))
