class Joint:

    def __init__(self, name, joint_type, parent, child, origin):
        self.name = name
        self.joint_type = joint_type
        self.parent = parent
        self.child = child
        self.originXYZ = origin

    def describe(self):
        print(f"Joint(name, type, parent, child, origin):\n{self.name}, {self.joint_type}, {self.parent.name}, "
              f"{self.child.name}, {self.originXYZ}\n")
