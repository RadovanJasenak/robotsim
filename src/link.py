class Link:
    # link parent class

    def __init__(self, name, xyz, rpy, color):
        self.name = name
        self.connected_joints = []
        self.is_base_link = False
        self.xyz = xyz
        self.rpy = rpy
        self.color = color

    def describe(self):
        print(f"This is link {self.name}")


class Box(Link):
    # base link, robot's body, as of now - can only be box, also other box links

    def __init__(self, name, length, width, height, xyz, rpy, color):
        super().__init__(name, xyz, rpy, color)
        self.length = length
        self.width = width
        self.height = height
        self.shape = "box"

    def describe(self):
        print(f"Link Box (name, radius, dimensions LWH, shape, xyz, rpy, color):\n{self.name}, {self.length} {self.width} "
              f"{self.height}, {self.shape}, {self.xyz}, {self.rpy}, {self.color}\n")


class Cylinder(Link):
    # meant to represent robot's wheels, cylinder shapes

    def __init__(self, name, radius, length, xyz, rpy, color):
        super().__init__(name, xyz, rpy, color)
        self.radius = radius
        self.length = length
        self.shape = "cylinder"

    def describe(self):
        print(f"Link Cylinder (name, radius, length, shape, xyz, rpy,color):\n{self.name}, {self.radius}, {self.length}, "
              f"{self.shape}, {self.xyz}, {self.rpy}, {self.color}\n")


class Sphere(Link):
    # class for spherical link, meant to represent omnidirectional wheel

    def __init__(self, name, radius, xyz, rpy, color):
        super().__init__(name, xyz, rpy, color)
        self.radius = radius
        self.shape = "sphere"

    def describe(self):
        print(f"Link Sphere (name, radius, shape, xyz, rpy, color):\n{self.name}, {self.radius}, "
              f"{self.shape}, {self.xyz}, {self.rpy}, {self.color}\n")
