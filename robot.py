class Robot:

    def __init__(self, box):
        self.wheels = []
        self.base_link = box

    def describe(self):

        print(self.base_link.name, self.base_link.length, self.base_link.width, self.base_link.height)

        print("I have {} wheels: ".format(len(self.wheels)))
        for wheel in self.wheels:
            wheel.describe()
