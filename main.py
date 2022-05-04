#!/usr/bin/python3

# run from terminal and have ROS installed
# source /opt/ros/noetic/setup.bash
# /usr/bin/python3 main.py

import window

if __name__ == '__main__':
    app = window.App("nas_robot_latest.xacro")
    app.robot.describe()
