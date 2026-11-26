"""Guide the Kobuki to a detected tag and hand its category to the arm."""

import math

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Int32

from .robot import Robot


class ChallengeNode(Node):
    """Search, align, approach and hold position for one pickup."""

    MAX_AGE_NS = 500_000_000
    ALIGN_TOLERANCE_RAD = 0.10
    CONFIRMATIONS = 3

    def __init__(self):
        super().__init__('challenge_node')
        self.pickup_distance = self.declare_parameter('pickup_distance_m', 0.11).value
        self.tolerance = self.declare_parameter('pickup_tolerance_m', 0.02).value
        if not (math.isfinite(self.pickup_distance)
                and 0 < self.tolerance < self.pickup_distance):
            raise ValueError('Pickup distance must exceed a positive pickup tolerance.')

        self.robot = Robot(self)
        self.pose_stamp = None
        self.bearing = 0.0
        self.distance = 0.0
        self.tag_id = None
        self.id_received = None
        self.new_pose = False
        self.new_id = False
        self.confirmations = 0
        self.tracking = False
        self.ready = False

        self.create_subscription(PoseStamped, '/tag_pose', self.receive_pose, 1)
        self.create_subscription(Int32, '/tag_id', self.receive_id, 1)
        self.pickup_pub = self.create_publisher(Int32, '/pickup_ready', 1)
        self.create_timer(0.1, self.control_base)

    def receive_pose(self, msg):
        """Keep the latest valid camera measurement and its detector timestamp."""
        position = msg.pose.position
        stamp = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
        if self.pose_stamp is not None and stamp <= self.pose_stamp:
            return
        if not (math.isfinite(position.x) and math.isfinite(position.z) and position.z > 0):
            self.pose_stamp = None
            self.confirmations = 0
            self.new_pose = False
            self.new_id = False
            return
        if self.pose_stamp is None or stamp - self.pose_stamp > self.MAX_AGE_NS:
            self.confirmations = 0
        self.pose_stamp = stamp
        self.distance = position.z
        self.bearing = math.atan2(position.x, position.z)
        self.new_pose = True
        if not self.in_pickup_position():
            self.confirmations = 0
            self.new_id = False

    def receive_id(self, msg):
        """Remember the category and restart confirmation when the target changes."""
        now = self.get_clock().now().nanoseconds
        if (msg.data != self.tag_id or self.id_received is None
                or now - self.id_received > self.MAX_AGE_NS):
            self.confirmations = 0
        self.tag_id = msg.data if msg.data in range(4) else None
        self.id_received = now
        self.new_id = self.tag_id is not None

    def in_pickup_position(self):
        """Check both the camera bearing and the calibrated pickup distance."""
        return (abs(self.bearing) <= self.ALIGN_TOLERANCE_RAD
                and abs(self.distance - self.pickup_distance) <= self.tolerance)

    def control_base(self):
        """Send one velocity command per tick, keeping vision callbacks responsive."""
        drive = self.robot.base.drive
        if self.ready:
            drive(0.0, 0.0)
            return

        now = self.get_clock().now().nanoseconds
        if self.pose_stamp is None or not 0 <= now - self.pose_stamp <= self.MAX_AGE_NS:
            # Stop on the tick that loses the target, then resume turning in place.
            drive(0.0, 0.0 if self.tracking else 0.20)
            self.tracking = False
            self.confirmations = 0
            self.new_pose = False
            self.new_id = False
            return

        self.tracking = True
        if self.in_pickup_position():
            drive(0.0, 0.0)
            # The detector sends pose and ID separately. Require new observations
            # from both streams for each confirmation, regardless of arrival order.
            if self.new_pose and self.new_id and 0 <= now - self.id_received <= self.MAX_AGE_NS:
                self.confirmations += 1
                self.new_pose = False
                self.new_id = False
                if self.confirmations >= self.CONFIRMATIONS:
                    self.ready = True
                    self.pickup_pub.publish(Int32(data=self.tag_id))
                    self.get_logger().info(f'Ready for pickup, category {self.tag_id}')
            return

        if self.distance < self.pickup_distance - self.tolerance:
            drive(0.0, 0.0)
            return

        # Camera x points right. Positive Kobuki angular velocity turns left.
        angular = max(-0.35, min(0.35, -0.8 * self.bearing))
        linear = 0.0
        if abs(self.bearing) <= self.ALIGN_TOLERANCE_RAD:
            linear = min(0.12, 0.4 * (self.distance - self.pickup_distance))
        drive(linear, angular)


def main(args=None):
    """Run the base controller until shutdown."""
    rclpy.init(args=args)
    node = ChallengeNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.robot.base.drive(0.0, 0.0)
        node.destroy_node()
        rclpy.try_shutdown()
