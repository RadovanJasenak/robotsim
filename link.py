class Link:
    # link of all links, basic

    def __init__(self, name, shape):
        self.name = name
        self.shape = shape  # box, sphere, cylinder

    def describe(self):
        print("This is link ", self.name)


class Box(Link):
    # main/base link, robot's body, as of now - can only be box

    def __init__(self, name, length, width, height):
        super().__init__(name, shape="box")
        self.length = length
        self.width = width
        self.height = height

    def describe(self):
        print("Link: {}, {}, dimensions: {} length, {} width, {} height".format(self.name, self.shape, self.length, self.width,
                                                                self.height))


class Cylinder(Link):
    # meant to represent robot's wheels, cylinder shapes

    def __init__(self, name, radius, length):
        super().__init__(name, shape="cylinder")
        self.radius = radius
        self.length = length
        self.joint_length = 0

    def describe(self):
        print("Link: {}, {}, dimensions: {} radius,  {} length, joint length is {}".format(self.name, self.shape, self.radius,
                                                                                self.length, self.joint_length))


class Sphere(Link):
    # class for spherical link, meant to represent omnidirectional wheel

    def __init__(self, name, radius):
        super().__init__(name, shape="sphere")
        self.radius = radius

    def describe(self):
        print("Link: {}, {}, dimensions: {} radius".format(self.name, self.shape, self.radius))
