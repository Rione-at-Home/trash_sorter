#!/bin/bash
colcon build
bash install/setup.bash
gnome-terminal -- "./testbash2.sh"