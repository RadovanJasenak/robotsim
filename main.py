# run from terminal
# source /opt/ros/noetic/setup.bash
# navigate back, /usr/bin/python3 main.py

from src import robot

if __name__ == '__main__':
    Robot2 = robot.Robot("nas_robot_latest.xacro")
    Robot2.describe()
