
# def main():
#     result = subprocess.run(['/opt/ros/noetic/bin/xacro', 'data/nas_robot_latest.xacro'], stdout=subprocess.PIPE)
#     urdf_subor = result.stdout.decode('utf-8')
#
#     root = Et.fromstring(urdf_subor)
#     # root = tree.getroot()
#
#     # print(root.tag) # robot
#     # print(root.attrib) # {'name': 'nas_robot'}
#     r1.name = root.attrib.get("name")
#
#     print("LINKS: ")
#     for link in root.iter("link"):
#         print(link.attrib)  # {'name': 'telo'}
#         visual = link.find('visual')
#         origin = visual.find('origin').attrib
#
#         geometry = visual.find('geometry')
#         shape = geometry[0].tag
#         print(shape)  # box
#         if link.attrib["name"] == "telo":
#             r1.geometry = geometry[0].tag
#         for child in geometry:
#             shape = child.attrib  # child.tag
#             print(shape)  # {'size': '0.4 0.2 0.1'}
#             if link.attrib["name"] == "telo":
#                 r1.dimensions.append(shape["size"])
#
#         print(origin)  # {'xyz': '0 0 0', 'rpy': '0 0 0'}
#         if link.attrib["name"] == "telo":
#             r1.originXYZ.append(origin["xyz"])
#         print()


# def str_to_int(string_list):
#     # converts string to integers, deletes spaces
#     string_list = string_split(string_list[0])
#     string_list = [ele for ele in string_list if ele.strip()]
#     integer_map = map(int, string_list)
#     integer_list = list(integer_map)
#     return integer_list


# def find_wheels(links, joints):
#     # reads all links, finds wheels and finds their joints
#     wheels = list()
#
#     for link in links:
#         if link.shape == "cylinder":  # if the link is a wheel
#             j_length = 0
#
#             for joint in joints:
#                 if joint.child == link.name:
#                     j_length = joint.wheel_indent
#
#             link.joint_length = j_length
#             wheels.append(link)
#     # only allows 2 wheels as of now
#     if len(wheels) > 2:
#         raise error.Wheelerror
#     return wheels

# class ContinuousJoint(Joint):
#     # wheels use 'continuous' joint type
#
#     def __init__(self, name, parent, child, wheel_indent):
#         super().__init__(name, joint_type="continuous")
#         self.parent = parent
#         self.child = child
#         self.wheel_indent = wheel_indent
#
#     def describe(self):
#         print("Joint: {}, {}, child is {}, parent is {} indent is {}".format(self.name, self.joint_type, self.child,
#                                                                              self.parent, self.wheel_indent))
#
#
# class FixedJoint(Joint):
#     # fixed joints
#     def __init__(self, name, parent, child):
#         super().__init__(name, joint_type="fixed")
#         self.parent = parent
#         self.child = child
#
#     def describe(self):
#         print("Joint: {}, {}, child is {}, parent is {}".format(self.name, self.joint_type, self.child, self.parent))

# def make_lists():
#     # runs xacro
#     # reads complete urdf - links and joints
#     urdf_links = list()
#     urdf_joints = list()
#
#     result = subprocess.run(['/opt/ros/noetic/bin/xacro', 'data/nas_robot_latest.xacro'], stdout=subprocess.PIPE)
#     urdf_subor = result.stdout.decode('utf-8')
#     root = Et.fromstring(urdf_subor)
#
#     for link in root.iter("link"):
#         urdf_links.append(link)
#
#     for joint in root.iter("joint"):
#         urdf_joints.append(joint)
#
#     return urdf_links, urdf_joints
