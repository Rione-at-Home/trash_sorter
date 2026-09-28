#!/bin/bash
. install/setup.bash
ros2 run v4l2_camera v4l2_camera_node --ros-args \
  -p video_device:=/dev/video2 \
  -p pixel_format:=YUYV \
  -p image_size:="[320,240]" & gnome-terminal -- "./gui_arm_run.sh"
read