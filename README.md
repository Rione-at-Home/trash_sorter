# trash_sorter
This is a trash-sorting robot made as a first-year undergraduate project for Ri-one@Home.

# Adding new nodes
To add new nodes, enter the filename in 'console_scripts' of setup.py in src/trash_sorter. It should follow the pattern of 'arbitrary_node_name = trash_sorter.filename:main'. The arbitrary_node_name is what the file will be referred to within the codebase.

# Adding new motors
To add new motors, follow these steps:
1. In arm.py, under the ArmController class, add an arbitrary name of the new motor to the self.joint_names list.
2. In crane_driver_niode.py, assign the previous arbitrary name to the ID of the motor in the JOINT_TO_ID dictionary. **Make sure you know what the motor's actual ID is.**
3. In gui.py, add the arbitrary name to the self.joint_names list.
4. In poses.py, ensure that the motor is accounter for in each of the lists within. Each list item determines the rotation of the motor according to index and thus the arm's poses (e.g., HOME[0] determines the rotation of crane_plus_joint1, which is 0).


# .sh files
These files are daisy-chained bash files used to create a build and activate all nodes and access the GUI. To use, navigate to the trash_sorter-main director, then type:
./gui_run.sh
These should automatically all nodes, going from:

gui_run.sh
- Colcon builds, then runs below file

gui_cam_run.sh
- Enables the v4l2 camera drivers, then runs below file

gui_arm_run.sh
- Enables the arm node/driver node, crane_driver_node.py, then runs below file

gui_detec_run.sh
- Enables the camera node, tag_detector_node.py, then runs the below file

gui_gui_run.sh
- Runs the gui node, allowing debug access

This isn't yet complete, unfortunately.