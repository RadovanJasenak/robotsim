from src import error
import subprocess
import xml.etree.ElementTree as Et
from src.link import *
from src.joint import *


class Robot:

    def __init__(self, file_name):
        self.wheels = []  # TODO: maybe will be needed in the future
        self.c_joints = []  # joints connected to base link TODO: maybe all links and joints should have an array

        urdf_links, urdf_joints = self.extract_xacro(file_name)
        links = self.create_link_objects(urdf_links)
        joints = self.create_joint_objects(urdf_joints)
        self.base_link = self.find_base_link(links, joints)
        self.connect_joints_links(links, joints)

    def describe(self):
        print(f"Base link (name, dimensions LWH, origin):\n{self.base_link.name}, {self.base_link.length} "
              f"{self.base_link.width} {self.base_link.height}, {self.base_link.originXYZ}\n")

        for joint in self.c_joints:
            joint.describe()
            joint.child.describe()

    def extract_xacro(self, file_name):
        # runs xacro
        # reads complete urdf - links and joints
        urdf_links = list()
        urdf_joints = list()

        result = subprocess.run(['/opt/ros/noetic/bin/xacro', f'data/{file_name}'], stdout=subprocess.PIPE)
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
                origin = link.find("visual").find("origin").attrib.get("xyz")
                links.append(Box(name, length, width, height, origin))

            if shape == 'cylinder':
                name = link.attrib.get("name")
                radius = link.find("visual").find('geometry')[0].attrib.get("radius")
                length = link.find("visual").find('geometry')[0].attrib.get("length")
                origin = link.find("visual").find("origin").attrib.get("xyz")
                links.append(Cylinder(name, float(radius), float(length), origin))

            if shape == 'sphere':
                name = link.attrib.get("name")
                radius = link.find("visual").find('geometry')[0].attrib.get("radius")
                origin = link.find("visual").find("origin").attrib.get("xyz")
                links.append(Sphere(name, float(radius), origin))
        return links

    def create_joint_objects(self, urdf_joints):
        # extract values from urdf
        joints = list()
        for joint in urdf_joints:
            name = joint.get("name")
            jtype = joint.get("type")
            parent = joint.find("parent").get("link")
            child = joint.find("child").get("link")
            origin = joint.find("origin").get("xyz")
            joints.append(Joint(name, jtype, parent, child, origin))
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
                base_link = link

        if base_link.shape != 'box':
            raise error.URDFerror
        # links.pop(links.index(base_link))
        return base_link

    def connect_joints_links(self, links, joints):
        # create tree structure of the robot
        # joints are only attached for base link
        b_parent = self.base_link.name

        for joint in joints:
            j_child = joint.child
            j_parent = joint.parent
            if b_parent == j_parent:
                self.c_joints.append(joint)

            for link in links:
                if link.name == j_child:
                    joint.child = link
                if link.name == j_parent:
                    joint.parent = link


def string_split(string_list):
    # splits string into floats, deletes spaces
    return [float(item) for item in string_list.split()]
