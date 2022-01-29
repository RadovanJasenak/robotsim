class Link:
    # link of all links, basic

    def __init__(self, name, origin, shape):
        self.name = name
        self.originXYZ = origin
        self.shape = shape  # box, sphere, cylinder

    def describe(self):
        print(f"This is link {self.name}")


class Box(Link):
    # main/base link, robot's body, as of now - can only be box

    def __init__(self, name, length, width, height, originXYZ):
        super().__init__(name, originXYZ, shape="box")
        self.length = length
        self.width = width
        self.height = height

    def describe(self):
        print(f"Link Box (name, radius, dimensions LWH, origin, shape):\n{self.name}, {self.length} {self.width} "
              f"{self.height}, {self.originXYZ}, {self.shape}\n")


class Cylinder(Link):
    # meant to represent robot's wheels, cylinder shapes

    def __init__(self, name, radius, length, originXYZ):
        super().__init__(name, originXYZ, shape="cylinder")
        self.radius = radius
        self.length = length

    def describe(self):
        print(f"Link Cylinder (name, radius, length, origin, shape):\n{self.name}, {self.radius}, {self.length}, "
              f"{self.originXYZ}, {self.shape}\n")


class Sphere(Link):
    # class for spherical link, meant to represent omnidirectional wheel

    def __init__(self, name, radius, originXYZ):
        super().__init__(name, originXYZ, shape="sphere")
        self.radius = radius

    def describe(self):
        print(f"Link Sphere (name, radius, origin, shape):\n{self.name}, {self.radius}, {self.originXYZ}, "
              f"{self.shape}\n")
