#!/bin/bash
. install/setup.bash
ros2 run trash_sorter driver_node & gnome-terminal -- "./testbash3.sh"
read