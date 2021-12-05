class Joint:
    # joint of all joints, basic

    def __init__(self, name, joint_type):
        self.name = name
        self.joint_type = joint_type

    def describe(self):
        print("This is joint ", self.name)


class ContinuousJoint(Joint):
    # wheels use 'continuous' joint type

    def __init__(self, name, parent, child, wheel_indent):
        super().__init__(name, joint_type="continuous")
        self.parent = parent
        self.child = child
        self.wheel_indent = wheel_indent

    def describe(self):
        print("Joint: {}, {}, child is {}, parent is {} indent is {}".format(self.name, self.joint_type, self.child,
                                                                             self.parent, self.wheel_indent))


class FixedJoint(Joint):
    # fixed joints
    def __init__(self, name, parent, child):
        super().__init__(name, joint_type="fixed")
        self.parent = parent
        self.child = child

    def describe(self):
        print("Joint: {}, {}, child is {}, parent is {}".format(self.name, self.joint_type, self.child, self.parent))

