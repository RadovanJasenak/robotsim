import pyrr
import mesh_loader as ml
from OpenGL.GL import *


class Link:
    # link parent class

    def __init__(self, name, xyz, rpy, color):
        self.name = name
        self.connected_joints = []
        self.is_base_link = False
        self.xyz = [float(x) for x in xyz.split(" ")]
        self.rpy = [float(x) for x in rpy.split(" ")]
        self.color = [float(x) for x in color.split(" ")]
        self.position = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([self.xyz[0], self.xyz[2], self.xyz[1]])
        )  # Y and Z axis are swapped
        self.scale = self.get_scale()
        # X - pitch
        # Y - roll
        # Z - yaw
        self.rotation = pyrr.matrix44.create_from_eulers(
            eulers=[self.rpy[1], self.rpy[0], self.rpy[2]]
        )
        self.mesh = None

    def describe(self):
        print(f"This is link {self.name}")

    def get_scale(self):
        raise Exception()

    def draw(self, model_location, model_matrix):
        # print("LINK ", self.name, self.get_scale())
        model = pyrr.matrix44.multiply(self.position, model_matrix)
        model = pyrr.matrix44.multiply(self.rotation, model)
        glUniformMatrix4fv(model_location, 1, GL_FALSE, pyrr.matrix44.multiply(self.get_scale(), model))
        glBindVertexArray(self.mesh.vao)  # bind the VAO that is being drawn
        glDrawArrays(GL_TRIANGLES, 0, self.mesh.vertex_count)

        for joint in self.connected_joints:
            if joint.child == self:
                continue
            model2 = pyrr.Matrix44(model)
            # pridaj joint
            model2 = pyrr.matrix44.multiply(joint.position, model2)
            model2 = pyrr.matrix44.multiply(joint.rotation, model2)
            # pridaj link
            link = joint.child
            link.draw(model_location, model2)

    def __str__(self):
        return "LINK '" + self.name + "'"

    def __repr__(self):
        return self.__str__()


class Box(Link):
    # base link, robot's body, as of now - can only be box, also other box links

    def __init__(self, name, length, width, height, xyz, rpy, color):
        super().__init__(name, xyz, rpy, color)
        self.length = length
        self.width = width
        self.height = height
        self.shape = "box"
        self.scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([length, height, width]))
        self.mesh = ml.MeshLoader("models/cube.obj", self.color)

    def describe(self):
        print(f"Link Box (name, radius, dimensions LWH, shape, xyz, rpy, color):\n{self.name}, {self.length} {self.width} "
              f"{self.height}, {self.shape}, {self.xyz}, {self.rpy}, {self.color}\n")

    def get_scale(self):
        if hasattr(self, 'scale'):
            return self.scale
        return pyrr.matrix44.create_identity()


class Cylinder(Link):
    # meant to represent robot's wheels, cylinder shapes

    def __init__(self, name, radius, length, xyz, rpy, color):
        super().__init__(name, xyz, rpy, color)
        self.radius = radius
        self.length = length
        self.shape = "cylinder"
        self.scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([2 * self.radius, self.length, 2 * self.radius]))
        self.mesh = ml.MeshLoader("models/cylinder.obj", self.color)

    def describe(self):
        print(f"Link Cylinder (name, radius, length, shape, xyz, rpy,color):\n{self.name}, {self.radius}, {self.length}, "
              f"{self.shape}, {self.xyz}, {self.rpy}, {self.color}\n")

    def get_scale(self):
        if hasattr(self, 'scale'):
            return self.scale
        return pyrr.matrix44.create_identity()


class Sphere(Link):
    # class for spherical link, meant to represent omnidirectional wheel

    def __init__(self, name, radius, xyz, rpy, color):
        super().__init__(name, xyz, rpy, color)
        self.radius = radius
        self.shape = "sphere"
        self.scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([2 * self.radius, 2 * self.radius, 2 * self.radius]))
        self.mesh = ml.MeshLoader("models/sphere.obj", self.color)

    def describe(self):
        print(f"Link Sphere (name, radius, shape, xyz, rpy, color):\n{self.name}, {self.radius}, "
              f"{self.shape}, {self.xyz}, {self.rpy}, {self.color}\n")

    def get_scale(self):
        if hasattr(self, 'scale'):
            return self.scale
        return pyrr.matrix44.create_identity()
