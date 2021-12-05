
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
