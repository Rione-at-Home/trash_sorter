#!/usr/bin/env python3
"""
challenge_node.py  (SHUTTLE strategy - skeleton)

Search -> approach -> pick -> sort -> repeat, one item per round trip.

This file is a SKELETON, NOT A FINISHED SOLUTION. The overall state
machine structure (states, transitions, subscriptions, timer) is given
and shouldn't need to change. 

What's missing is the actual behavior inside each state. That's your job, 
following the TODO checklists below. Each TODO includes a commented-out 
example showing the general shape of one possible solution - read it for 
the idea, then write your own rather than just uncommenting it, 
so you understand what it's doing and can tune it for your robot.

Until you fill in a TODO, that state will print a warning and do nothing.
Build and test one state at a time; you don't need everything working 
before you can start testing SEARCHING or APPROACHING in isolation.
"""

import enum
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Int32

from .robot import Robot


# Tag ID -> trash category, matching the vision system's mapping.
# Your SORTING state needs to turn this into an actual arm action per
# category - see the TODO there.
CATEGORY_NAMES = {
    0: "Burnable (kanenengomi)",
    1: "PET Bottle (petbotoru)",
    2: "Can (kan)",
    3: "Non-burnable (funenengomi)",  # stretch-goal category
}


class State(enum.Enum):
    SEARCHING = 1
    APPROACHING = 2
    PICKING = 3
    SORTING = 4
    FINISHED = 5


class ChallengeNode(Node):

    def __init__(self):
        super().__init__("challenge_node")

        self.robot = Robot(self)

        self.state = State.SEARCHING

        # Camera feedback data - updated by the callbacks below.
        self.target_visible = False
        self.last_tag_time = self.get_clock().now()
        self.target_x_offset = 0.0  # Horizontal alignment error (meters)
        self.target_z_dist = 0.0    # Distance to tag (meters)
        self.target_id = -1         # Category ID, see CATEGORY_NAMES

        # --- Control gains & thresholds - TUNE THESE ---
        # Starting values only. Too aggressive and the robot will
        # oscillate or overshoot; too conservative and it'll be too slow
        # to be usable. Change one at a time and retest.
        self.PICKUP_DISTANCE = 0.11  # meters - stopping distance for arm reach
        self.KP_ANGULAR = 0.8        # steering P-gain
        self.KP_LINEAR = 0.4         # drive P-gain
        self.LOST_TIMEOUT = 1.0      # seconds before a tag is considered lost

        # How many items to sort before stopping. None = run forever
        # (stop by hand). Useful to cap for a timed demo.
        self.MAX_ITEMS = None
        self.items_sorted = 0

        # Subscriptions for the tag detector node.
        self.pose_sub = self.create_subscription(
            PoseStamped, "/tag_pose", self.tag_pose_callback, 10
        )
        self.id_sub = self.create_subscription(
            Int32, "/tag_id", self.tag_id_callback, 10
        )

        self.get_logger().info(
            "Challenge Node (shuttle skeleton) initialized! Starting control loop..."
        )

        self.timer = self.create_timer(0.1, self.control_loop)

    def tag_pose_callback(self, msg: PoseStamped):
        """
        Updates tag position published by the vision node.
        """
        self.target_visible = True
        self.last_tag_time = self.get_clock().now()
        self.target_x_offset = msg.pose.position.x
        self.target_z_dist = msg.pose.position.z

    def tag_id_callback(self, msg: Int32):
        """
        Updates tag category ID published by the vision node.
        """
        self.target_id = msg.data

    def control_loop(self):
        """
        Main State Machine Loop. Runs at 10 Hz.
        """

        # Timeout: mark invisible if no tag frame received recently.
        # This part is given - don't remove it, your states rely on
        # target_visible being accurate.
        time_since_seen = (self.get_clock().now() - self.last_tag_time).nanoseconds / 1e9
        if time_since_seen > self.LOST_TIMEOUT:
            self.target_visible = False



        # State 1: SEARCHING
        if self.state == State.SEARCHING:
            # TODO:
            #   1. If no tag is visible, rotate in place to keep looking.
            #   2. If a tag becomes visible, stop the base and switch to
            #      State.APPROACHING.
            #
            # Example:
            #   if not self.target_visible:
            #       self.robot.base.drive(linear=0.0, angular=0.3)
            #   else:
            #       self.robot.base.stop()
            #       self.state = State.APPROACHING
            self.get_logger().warn(
                "SEARCHING not implemented yet", throttle_duration_sec=2
            )



        # State 2: APPROACHING
        elif self.state == State.APPROACHING:
            # TODO:
            #   1. If the tag is no longer visible, go back to SEARCHING.
            #   2. Compute how far off you are from the pickup distance
            #      (dist_error) and how far off-center the tag is
            #      (angle_error is generally more robust than raw
            #      x_offset since it cancels out some distance-dependent
            #      error - think about why).
            #   3. Decide the stop condition: close enough AND centered
            #      enough -> stop the base and move to State.PICKING.
            #   4. Otherwise, compute angular_speed and linear_speed
            #      (P-control off the errors above, clamped to sane
            #      max values) and call self.robot.base.drive(...).
            #      Consider: should the robot drive forward at all while
            #      still significantly off-center?
            #
            # Example:
            #   if not self.target_visible:
            #       self.state = State.SEARCHING
            #       return
            #
            #   dist_error = self.target_z_dist - self.PICKUP_DISTANCE
            #   angle_error = self.target_x_offset / self.target_z_dist
            #
            #   if dist_error <= 0.1 and abs(angle_error) < 0.15:
            #       self.robot.base.stop()
            #       self.state = State.PICKING
            #       return
            #
            #   angular_speed = -self.KP_ANGULAR * angle_error
            #   angular_speed = max(-0.4, min(0.4, angular_speed))
            #
            #   if abs(angle_error) > 0.2:
            #       linear_speed = 0.0
            #   else:
            #       linear_speed = self.KP_LINEAR * dist_error
            #       linear_speed = max(0.0, min(0.2, linear_speed))
            #
            #   self.robot.base.drive(linear=linear_speed, angular=angular_speed)
            self.get_logger().warn(
                "APPROACHING not implemented yet", throttle_duration_sec=2
            )




        # State 3: PICKING
        elif self.state == State.PICKING:
            # TODO:
            #   1. Call whatever ArmController sequence actually picks
            #      up the item (check arm.py for what's already there,
            #      e.g. grab_bag() / lift_bag() - use those or add your
            #      own if your item/gripper setup differs).
            #   2. Move on to State.SORTING.
            #
            # Example:
            #   self.robot.arm.grab_bag()
            #   self.robot.arm.lift_bag()
            #   self.state = State.SORTING
            self.get_logger().warn(
                "PICKING not implemented yet", throttle_duration_sec=2
            )

        # State 4: SORTING
        elif self.state == State.SORTING:
            # TODO:
            #   1. Look at self.target_id and CATEGORY_NAMES to figure
            #      out which category this item is.
            #   2. Call the matching ArmController placement method for
            #      that category. You'll likely need to ADD new methods
            #      to arm.py (and new poses to poses.py, found using
            #      gui.py) for any categories beyond the 2 that already
            #      have example methods (place_left/place_right-style).
            #   3. Handle an unknown/unexpected ID sensibly (log a
            #      warning, pick a sane default) rather than crashing.
            #   4. Reset target_visible/target_id so a stale reading
            #      doesn't immediately re-trigger APPROACHING.
            #   5. Increment self.items_sorted, then either go back to
            #      State.SEARCHING (to keep shuttling) or State.FINISHED
            #      if self.MAX_ITEMS has been reached.
            #
            # Example (only 2 of your 3-4 categories shown - you'll add
            # the rest following the same pattern):
            #   if self.target_id == 0:
            #       self.robot.arm.place_burnable()
            #   elif self.target_id == 1:
            #       self.robot.arm.place_pet_bottle()
            #   else:
            #       self.get_logger().warn("Unknown Tag ID! Defaulting to burnable.")
            #       self.robot.arm.place_burnable()
            #
            #   self.items_sorted += 1
            #   self.target_visible = False
            #   self.target_id = -1
            #
            #   if self.MAX_ITEMS is not None and self.items_sorted >= self.MAX_ITEMS:
            #       self.state = State.FINISHED
            #   else:
            #       self.state = State.SEARCHING
            self.get_logger().warn(
                "SORTING not implemented yet", throttle_duration_sec=2
            )

        # State 5: FINISHED
        elif self.state == State.FINISHED:
            # Given - this one's simple enough that there's not much to
            # design here, but feel free to add anything you want (e.g.
            # a victory arm pose, a final log summary).
            self.robot.base.stop()
            self.get_logger().info(
                f"Mission complete! {self.items_sorted} item(s) sorted.",
                throttle_duration_sec=5
            )


def main(args=None):
    rclpy.init(args=args)
    node = ChallengeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()