#!/bin/bash
. install/setup.bash
ros2 run trash_sorter driver_node & gnome-terminal -- "./gui_detec_run.sh"
read