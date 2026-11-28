# Node responsible for listening to the DualShock controller and publishing its button states under the cmd_vel topic

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class PS4JoyBridge(Node):

    def __init__(self):
        super().__init__('ps4_joy_bridge')
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10
        )
        self.publisher = self.create_publisher(Joy, 'cmd_vel', 10)

        self.get_logger().info("Control Link: Online.")

    def joy_callback(self, msg: Joy):
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PS4JoyBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
