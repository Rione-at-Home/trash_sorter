# TEST FILE/REFERENCE ONLY DO NOT USE
"""import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy


class CmdVelListener(Node):

    def __init__(self):
        super().__init__('cmd_vel_listener')
        self.subscription = self.create_subscription(
            Joy,
            'cmd_vel',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg: Joy):
        self.get_logger().info(f"LeftX: {msg.axes[0]:.2f}, LeftY: {msg.axes[1]:.2f}")
        self.get_logger().info(f"RightX: {msg.axes[3]:.2f}, RightY: {msg.axes[4]:.2f}")
        self.get_logger().info(f"X pressed: {msg.buttons[0]}")
        self.get_logger().info(f"L2 pressed: {msg.buttons[6]:.2f}")
        self.get_logger().info(f"R2 pressed: {msg.buttons[7]:.2f}")


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
"""