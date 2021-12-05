# run from terminal
# navigate to catkin_ws, source /opt/ros/noetic/setup.bash
# navigate back, /usr/bin/python3 main.py

import xml.etree.ElementTree as Et
from robot import Robot
from link import Box, Cylinder, Sphere
from joint import ContinuousJoint, FixedJoint
import error
import subprocess


def string_split(string_list):
    # splits string into floats, deletes spaces
    return [float(item) for item in string_list.split()]


def make_lists():
    # runs xacro
    # reads complete urdf - links and joints
    urdf_links = list()
    urdf_joints = list()

    result = subprocess.run(['/opt/ros/noetic/bin/xacro', 'data/my2wr.xacro'], stdout=subprocess.PIPE)
    urdf_subor = result.stdout.decode('utf-8')
    root = Et.fromstring(urdf_subor)

    for link in root.iter("link"):
        urdf_links.append(link)

    for joint in root.iter("joint"):
        urdf_joints.append(joint)

    return urdf_links, urdf_joints


def find_base_link(links, joints):
    # finds the base_link of a robot in urdf and returns object Box
    link_names = list()
    for link in links:
        link_names.append(link.name)

    joint_children = list()
    for joint in joints:
        joint_children.append(joint.child)

    base_link = list(set(link_names).symmetric_difference(set(joint_children)))[0]  # base link is not anytone's child
    for link in links:
        if base_link == link.name:
            base_link = link
    if base_link.shape != 'box':
        raise error.URDFerror
    bl = Box(base_link.name, base_link.length, base_link.width, base_link.height)
    return Robot(bl)


def create_link_objects(urdf_links):
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
            links.append(Box(name, length, width, height))

        if shape == 'cylinder':
            name = link.attrib.get("name")
            radius = link.find("visual").find('geometry')[0].attrib.get("radius")
            length = link.find("visual").find('geometry')[0].attrib.get("length")
            links.append(Cylinder(name, float(radius), float(length)))

        if shape == 'sphere':
            name = link.attrib.get("name")
            radius = link.find("visual").find('geometry')[0].attrib.get("radius")
            links.append(Sphere(name, float(radius)))
    return links


def create_joint_objects(urdf_joints):
    # extract values from urdf
    joints = list()
    for joint in urdf_joints:
        joint_type = joint.get("type")

        if joint_type == 'continuous':
            name = joint.get("name")
            parent = joint.find("parent").get("link")
            child = joint.find("child").get("link")
            axis = string_split(joint.find("axis").get("xyz"))
            rotation_axis = None
            for ax in axis:
                if ax == 1:
                    rotation_axis = axis.index(ax)
            wheel_indent = string_split(joint.find("origin").get("xyz"))[rotation_axis]
            joints.append(ContinuousJoint(name, parent, child, wheel_indent))

        if joint_type == 'fixed':
            name = joint.get("name")
            parent = joint.find("parent").get("link")
            child = joint.find("child").get("link")
            joints.append(FixedJoint(name, parent, child))
    return joints


def find_wheels(links, joints):
    # reads all links, finds wheels and finds their joints
    wheels = list()

    for link in links:
        if link.shape == "cylinder":  # if the link is a wheel
            j_length = 0

            for joint in joints:
                if joint.child == link.name:
                    j_length = joint.wheel_indent

            link.joint_length = j_length
            wheels.append(link)
    # only allows 2 wheels as of now
    if len(wheels) > 2:
        raise error.Wheelerror
    return wheels


if __name__ == '__main__':
    print()
    urdf_links, urdf_joints = make_lists()

    links = create_link_objects(urdf_links)
    joints = create_joint_objects(urdf_joints)

    Robot1 = find_base_link(links, joints)
    Robot1.wheels = find_wheels(links, joints)

    Robot1.describe()
"""
    print("Links:")
    for link in links:
        link.describe()

    print("\nJoints:")
    for joint in joints:
        joint.describe()

    print("\nWheels:")
    for wheel in Robot1.wheels:
        wheel.describe()
    print()
"""