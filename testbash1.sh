#!/bin/bash
colcon build
. install/setup.bash
gnome-terminal -- "./testbash2.sh"