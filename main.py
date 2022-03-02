#!/usr/bin/python3

# run from terminal and have ROS installed
# source /opt/ros/noetic/setup.bash
# /usr/bin/python3 main.py

from src import robot
from gui import window

if __name__ == '__main__':
    Robot2 = robot.Robot("nas_robot_latest.xacro")
    Robot2.describe()
    app = window.App(Robot2)
