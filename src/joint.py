class Joint:

    def __init__(self, name, joint_type, parent, child, xyz, rpy):
        self.name = name
        self.joint_type = joint_type
        self.parent = parent
        self.child = child
        self.xyz = xyz
        self.rpy = rpy

    def describe(self):
        print(f"Joint(name, type, parent, child, xyz, rpy):\n{self.name}, {self.joint_type}, {self.parent.name}, "
              f"{self.child.name}, {self.xyz}, {self.rpy}\n")
