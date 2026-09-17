#!/bin/bash
colcon build
. install/setup.bash
gnome-terminal -- "./gui_cam_run.sh"