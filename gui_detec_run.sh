#!/bin/bash
. install/setup.bash
ros2 run trash_sorter camera_node & gnome-terminal -- "./gui_gui_run.sh"
read