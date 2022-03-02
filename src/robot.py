from src import error
import subprocess
import xml.etree.ElementTree as Et
from src.link import *
from src.joint import *


class Robot:

    def __init__(self, file_name):
        self.wheels = []  # TODO: maybe will be needed in the future

        urdf_links, urdf_joints = self.extract_xacro(file_name)
        self.links = self.create_link_objects(urdf_links)
        self.joints = self.create_joint_objects(urdf_joints)
        # create base_link attribute and pop the object from links List, base link is box link
        self.base_link = self.find_base_link(self.links, self.joints)
        self.connect_joints_links(self.links, self.joints)

    def describe(self):
        print(f"Base link (name, dimensions LWH, xyz, rpy):\n{self.base_link.name}, {self.base_link.length} "
              f"{self.base_link.width} {self.base_link.height}, {self.base_link.xyz}, {self.base_link.rpy}\n")

        for joint in self.base_link.connected_joints:
            joint.describe()
            joint.child.describe()

    def extract_xacro(self, file_name):
        # runs xacro
        # reads complete urdf - links and joints
        urdf_links = list()
        urdf_joints = list()

        print("*** nacitavam *** " + file_name)
        # result = subprocess.run(['/opt/ros/noetic/bin/xacro', f'data/{file_name}'], stdout=subprocess.PIPE)
        result = subprocess.run(['./xacro.sh', f'data/{file_name}'], stdout=subprocess.PIPE)
        urdf_file = result.stdout.decode('utf-8')
        root = Et.fromstring(urdf_file)

        for link in root.iter("link"):
            urdf_links.append(link)

        for joint in root.iter("joint"):
            urdf_joints.append(joint)

        return urdf_links, urdf_joints

    def create_link_objects(self, urdf_links):
        # extract values from urdf
        links = list()
        for link in urdf_links:
            shape = link.find("visual").find('geometry')[0].tag

            if shape == 'box':
                name = link.attrib.get("name")
                dimensions = string_split(link.find("visual").find('geometry')[0].attrib.get("size"))
                length = dimensions[0]
                width = dimensions[1]
                height = dimensions[2]
                xyz = link.find("visual").find("origin").attrib.get("xyz")
                rpy = link.find("visual").find("origin").attrib.get("rpy")
                links.append(Box(name, length, width, height, xyz, rpy))

            if shape == 'cylinder':
                name = link.attrib.get("name")
                radius = link.find("visual").find('geometry')[0].attrib.get("radius")
                length = link.find("visual").find('geometry')[0].attrib.get("length")
                xyz = link.find("visual").find("origin").attrib.get("xyz")
                rpy = link.find("visual").find("origin").attrib.get("rpy")
                links.append(Cylinder(name, float(radius), float(length), xyz, rpy))

            if shape == 'sphere':
                name = link.attrib.get("name")
                radius = link.find("visual").find('geometry')[0].attrib.get("radius")
                xyz = link.find("visual").find("origin").attrib.get("xyz")
                rpy = link.find("visual").find("origin").attrib.get("rpy")
                links.append(Sphere(name, float(radius), xyz, rpy))
        return links

    def create_joint_objects(self, urdf_joints):
        # extract values from urdf
        joints = list()
        for joint in urdf_joints:
            name = joint.get("name")
            jtype = joint.get("type")
            parent = joint.find("parent").get("link")
            child = joint.find("child").get("link")
            xyz = joint.find("origin").get("xyz")
            rpy = joint.find("origin").get("rpy")
            joints.append(Joint(name, jtype, parent, child, xyz, rpy))
        return joints

    def find_base_link(self, links, joints):
        # finds the base_link of a robot in urdf and returns object Box
        link_names = list()
        for link in links:
            link_names.append(link.name)

        joint_children = list()
        for joint in joints:
            joint_children.append(joint.child)

        base_link = None
        for name in link_names:  # base link is not anyone's child
            if name not in joint_children:
                base_link = name
        for link in links:
            if base_link == link.name:
                link.is_base_link = True
                base_link = link

        if base_link.shape != 'box':
            raise error.URDFerror
        return base_link

    def connect_joints_links(self, links, joints):
        # create tree structure of the robot
        for joint in joints:
            # connecting links to joints
            for link in links:
                # connect links to joints as children
                if link.name == joint.child:
                    joint.child = link
                # connect links to joints as parents
                if link.name == joint.parent:
                    joint.parent = link

        # connect joints to links
        for link in links:
            for joint in joints:
                if link.name == joint.parent.name or link.name == joint.child.name:
                    link.connected_joints.append(joint)

        # print("1==============================")
        # for joint in joints:
        #     print(joint.child.name)
        # print("2==============================")
        # for joint in joints:
        #     print(joint.parent.name)
        # print("3==============================")
        # for link in links:
        #     print(f"This is link {link.name}")
        #     for item in link.connected_joints:
        #         print(item.name)
        # print("3==============================")
        # for link in links:
        #     print(link.is_base_link)


def string_split(string_list):
    # splits string into floats, deletes spaces
    return [float(item) for item in string_list.split()]
