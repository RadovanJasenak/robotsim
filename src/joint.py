import pyrr


class Joint:

    def __init__(self, name, joint_type, parent, child, xyz, rpy):
        self.name = name
        self.joint_type = joint_type
        self.parent = parent
        self.child = child
        self.xyz = [float(x) for x in xyz.split(" ")]
        self.rpy = [float(x) for x in rpy.split(" ")]
        self.position = pyrr.Vector3([self.xyz[0], self.xyz[1], self.xyz[2]])
        self.rotation_x = pyrr.matrix44.create_from_x_rotation(self.rpy[0])
        self.rotation_y = pyrr.matrix44.create_from_y_rotation(self.rpy[1])
        self.rotation_z = pyrr.matrix44.create_from_z_rotation(self.rpy[2])
        self.rotation = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(self.rotation_x, self.rotation_y),
            self.rotation_z
        )

    def describe(self):
        print(f"Joint(name, type, parent, child, xyz, rpy):\n{self.name}, {self.joint_type}, {self.parent.name}, "
              f"{self.child.name}, {self.xyz}, {self.rpy}\n")
