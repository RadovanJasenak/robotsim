import pyrr


class Joint:

    def __init__(self, name, joint_type, parent, child, xyz, rpy):
        self.name = name
        self.joint_type = joint_type
        self.parent = parent
        self.child = child
        self.xyz = [float(x) for x in xyz.split(" ")]
        self.rpy = [float(x) for x in rpy.split(" ")]
        self.position = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([self.xyz[0], self.xyz[2], self.xyz[1]])
        )  # Y and Z axis are swapped
        self.rotation = pyrr.matrix44.create_from_eulers(
            eulers=[self.rpy[1], self.rpy[0], self.rpy[2]]
        )

    def describe(self):
        print(f"Joint(name, type, parent, child, xyz, rpy):\n{self.name}, {self.joint_type}, {self.parent.name}, "
              f"{self.child.name}, {self.xyz}, {self.rpy}\n")
