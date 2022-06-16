import subprocess
import xml.etree.ElementTree as Et
from link import *
from joint import *
import numpy as np
import math
from operator import add


class Robot:

    def __init__(self, file_name):
        urdf_links, urdf_joints, materials = self.extract_xacro(file_name)
        self.links = self.create_link_objects(urdf_links, materials)
        self.joints = self.create_joint_objects(urdf_joints)
        # determine which link is the base link of a robot
        self.base_link = self.find_base_link(self.links, self.joints)
        self.connect_joints_links(self.links, self.joints)
        self.number_of_wheels = 0
        self.wheels = []  # joints
        for j in self.joints:
            if j.joint_type == "continuous":
                self.number_of_wheels += 1
                self.wheels.append(j)
        self.theta = self.base_link.rpy[2]
        print("*** robot vytvoreny *** ")

    def move(self):
        # for differential drive robots only ( 2 wheels)
        if self.number_of_wheels != 2:
            return
        wheel1 = self.wheels[0]
        wheel2 = self.wheels[1]

        # calculate distance between wheels
        l1 = list(map(add, self.base_link.xyz, wheel1.xyz))
        l2 = list(map(add, self.base_link.xyz, wheel2.xyz))

        dbw = math.sqrt(math.pow(l2[0] - l1[0], 2) +
                        math.pow(l2[1] - l1[1], 2) +
                        math.pow(l2[2] - l1[2], 2))
        l1 = dbw/2
        l2 = dbw/2

        # each wheel's contribution to movement (change)  in local reference frame
        xR1 = 0.5 * wheel1.child.radius * wheel1.speed
        xR2 = 0.5 * wheel2.child.radius * wheel2.speed
        xR = xR1 + xR2
        yR = 0

        # each wheel's contribution to robot's rotation
        omega1 = wheel1.child.radius * wheel1.speed / (2 * l1)
        omega2 = -wheel2.child.radius * wheel2.speed / (2 * l2)
        omega = omega1 + omega2

        # new local position
        xiR = pyrr.Vector3([xR, yR, omega])
        print(f"new local {xiR}")

        # new global position
        rotation_matrix = np.array([[np.cos(self.theta), -np.sin(self.theta), 0],
                                    [np.sin(self.theta),  np.cos(self.theta), 0],
                                    [0,                   0,                  1]])
        xiI = np.array([self.base_link.xyz[0],
                       self.base_link.xyz[1],
                       self.theta])
        xiI = xiI + (rotation_matrix @ xiR)
        self.base_link.xyz[0] = xiI[0]
        self.base_link.xyz[1] = xiI[1]
        xiI[2] = xiI[2] % math.radians(360)
        self.base_link.update_rotation(xiI[2])
        self.base_link.update_position(xiI[0], 0.1, xiI[1])
        self.theta = xiI[2]

    def update_values(self, pry, speeds):
        for i, wheel in enumerate(self.wheels):
            wheel.update_j_rotation(pry[i], speeds[i])

    def describe(self):
        print(f"Base link (name, dimensions LWH, xyz, rpy, color):\n{self.base_link.name}, {self.base_link.length} "
              f"{self.base_link.width} {self.base_link.height}, {self.base_link.xyz}, {self.base_link.rpy}, "
              f"{self.base_link.color}\n")

        for joint in self.base_link.connected_joints:
            joint.describe()
            joint.child.describe()

    def extract_xacro(self, file_name):
        # runs xacro
        # reads complete urdf - links and joints
        urdf_links = list()
        urdf_joints = list()
        materials = {}

        print("*** nacitavam *** " + file_name)
        # result = subprocess.run(['/opt/ros/noetic/bin/xacro', f'data/{file_name}'], stdout=subprocess.PIPE)
        result = subprocess.run(['./xacro.sh', f'data/{file_name}'], stdout=subprocess.PIPE)
        urdf_file = result.stdout.decode('utf-8')
        root = Et.fromstring(urdf_file)

        for link in root.iter("link"):
            urdf_links.append(link)

        for joint in root.iter("joint"):
            urdf_joints.append(joint)

        for child in root:
            if child.tag == "material":
                name = child.attrib["name"]
                value = child[0].attrib["rgba"]
                materials[name] = value

        return urdf_links, urdf_joints, materials

    def create_link_objects(self, urdf_links, materials):
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
                color = link.find("visual").find("material").attrib.get("name")
                color = materials[color]
                links.append(Box(name, length, width, height, xyz, rpy, color))

            if shape == 'cylinder':
                name = link.attrib.get("name")
                radius = link.find("visual").find('geometry')[0].attrib.get("radius")
                length = link.find("visual").find('geometry')[0].attrib.get("length")
                xyz = link.find("visual").find("origin").attrib.get("xyz")
                rpy = link.find("visual").find("origin").attrib.get("rpy")
                color = link.find("visual").find("material").attrib.get("name")
                color = materials[color]
                links.append(Cylinder(name, float(radius), float(length), xyz, rpy, color))

            if shape == 'sphere':
                name = link.attrib.get("name")
                radius = link.find("visual").find('geometry')[0].attrib.get("radius")
                xyz = link.find("visual").find("origin").attrib.get("xyz")
                rpy = link.find("visual").find("origin").attrib.get("rpy")
                color = link.find("visual").find("material").attrib.get("name")
                color = materials[color]
                links.append(Sphere(name, float(radius), xyz, rpy, color))
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
