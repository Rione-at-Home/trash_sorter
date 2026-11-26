#!/bin/bash
colcon build --packages-select trash_sorter
. install/setup.bash
gnome-terminal -- "./gui_cam_run.sh"