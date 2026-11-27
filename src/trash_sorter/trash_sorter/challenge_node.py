#!/usr/bin/env python3

#
## challenge_node.py
#
#  This program defines the main node for the challenge. It initializes the 
#  robot and provides a template for implementing the challenge solution.
#
#

import rclpy
from rclpy.node import Node
import time
from sensor_msgs.msg import Joy

from .robot import Robot


class ChallengeNode(Node):

    def __init__(self):
        super().__init__("cmd_vel_listener")
        self.subscription = self.create_subscription(
            Joy,
            'cmd_vel',
            self.listener_callback,
            10
        )

        self.robot = Robot(self)

        self.get_logger().info("All systems: Nominal.")

        self.run()

    def listener_callback(self, msg: Joy):
        if msg.axes[1] > 0.5:
            self.robot.base.hold_forward()
        if msg.axes[1] < -0.5:
            self.robot.base.hold_backward()
        if msg.axes[0] > 0.5:
            self.robot.base.hold_left()
        if msg.axes[0] < -0.5:
            self.robot.base.hold_right()


    def run(self):
        pass

       




def main(args=None):

    rclpy.init(args=args)

    node = ChallengeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()