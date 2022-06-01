#!/usr/bin/python3

# run from terminal and have ROS installed
# source /opt/ros/noetic/setup.bash
# /usr/bin/python3 main.py differential_drive.xacro

from windowQt import Window
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.showMaximized()
    app.exec()
