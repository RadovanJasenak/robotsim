class Link:
    # link parent class

    def __init__(self, name, origin):
        self.name = name
        self.origin = origin
        self.connected_joints = []
        self.is_base_link = False

    def describe(self):
        print(f"This is link {self.name}")


class Box(Link):
    # base link, robot's body, as of now - can only be box, also other box links

    def __init__(self, name, length, width, height, origin):
        super().__init__(name, origin)
        self.length = length
        self.width = width
        self.height = height
        self.shape = "box"

    def describe(self):
        print(f"Link Box (name, radius, dimensions LWH, origin, shape):\n{self.name}, {self.length} {self.width} "
              f"{self.height}, {self.origin}, {self.shape}\n")


class Cylinder(Link):
    # meant to represent robot's wheels, cylinder shapes

    def __init__(self, name, radius, length, origin):
        super().__init__(name, origin)
        self.radius = radius
        self.length = length
        self.shape = "cylinder"

    def describe(self):
        print(f"Link Cylinder (name, radius, length, origin, shape):\n{self.name}, {self.radius}, {self.length}, "
              f"{self.origin}, {self.shape}\n")


class Sphere(Link):
    # class for spherical link, meant to represent omnidirectional wheel

    def __init__(self, name, radius, origin):
        super().__init__(name, origin)
        self.radius = radius
        self.shape = "sphere"

    def describe(self):
        print(f"Link Sphere (name, radius, origin, shape):\n{self.name}, {self.radius}, {self.origin}, "
              f"{self.shape}\n")
