#!/bin/sh

if [ -f /opt/ros/noetic/bin/xacro ]
then
	/opt/ros/noetic/bin/xacro $1
elif [ -f /usr/bin/docker ]
	/usr/bin/docker run -it --name ros-sh --net=host -v "$(pwd)":/app osrf/ros:noetic-desktop-full /opt/ros/noetic/bin/xacro /app/$1
then
  pass
else
	echo "xacro nebolo najdene!"
fi
