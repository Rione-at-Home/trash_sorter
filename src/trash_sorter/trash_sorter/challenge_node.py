#!/usr/bin/env python3
"""
challenge_node.py  (BATCH strategy - skeleton)

Search -> approach -> pick -> stow onboard, repeated up to CAPACITY
times or until nothing new is found for a while, THEN a single
RETURNING + SORTING phase that empties everything collected in one
trip back to the drop-off point.

This file is a SKELETON, not a finished solution. The overall state
structure (states, transitions, subscriptions, timer, capacity
tracking) is given. What's missing is the actual behavior inside each
state - that's your job, following the TODO checklists below. Each
TODO includes a commented-out example showing the general shape of one
possible solution - read it for the idea, then write your own rather
than uncommenting it directly, so you understand what it's doing and
can tune/adapt it.

Until you fill in a TODO, that state will log a warning and do nothing
- this is expected. Build top-down: get SEARCHING and APPROACHING
working and tested (you can reuse/compare against the shuttle version
for these, since they're identical in both strategies) before moving
on to STOWING, RETURNING, and SORTING.

IMPORTANT PHYSICAL ASSUMPTION - confirm with the mechanical team before
writing STOWING/SORTING:
  The Crane+ gripper can only hold one item at a time, so "gathering"
  multiple items requires the robot to have ONBOARD STORAGE (e.g. a
  small tray with a compartment per category) that the arm drops items
  into during collection. Classification still happens at pickup time
  (same as the shuttle version) - the difference is WHERE the item
  goes after pickup: an onboard compartment now, vs. straight to the
  final external bin.

  This means arm.py will need NEW methods that don't exist yet -
  something like stow_X() for putting an item into the matching
  onboard compartment during collection, and empty_X() for dumping a
  compartment into the real external bin once back at the drop-off
  point. Design these with gui.py the same way you would any new arm
  action, following the existing method pattern.

RETURNING is a genuinely unsolved problem in this codebase - there's no
localization/mapping here, so "drive back to the drop-off point" isn't
something you get for free. A couple of starting approaches:
  - Dead reckoning: track total turn/drive commands issued while
    searching, then reverse them to retrace your path.
  - Place a second ArUco tag at the drop-off point and treat driving to
    it as basically another APPROACHING-style behavior you already know
    how to write.
Expect this to be the hardest part of this version. It's a reasonable
thing to timebox and de-scope (fall back to the shuttle strategy) if
it isn't working reliably by roughly the 6-week mark.
"""

import enum
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Int32

from .robot import Robot


# Tag ID -> trash category, matching the vision system's mapping.
# Your STOWING and SORTING states need to turn this into actual arm
# actions per category - see the TODOs there.
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
    STOWING = 4     # put the just-picked item into onboard storage
    RETURNING = 5   # drive back to the drop-off point
    SORTING = 6     # empty each onboard compartment into its real bin
    FINISHED = 7


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
        # Same meaning as in the shuttle version - these only affect
        # SEARCHING/APPROACHING, which are identical in both strategies.
        self.PICKUP_DISTANCE = 0.11  # meters - stopping distance for arm reach
        self.KP_ANGULAR = 0.8        # steering P-gain
        self.KP_LINEAR = 0.4         # drive P-gain
        self.LOST_TIMEOUT = 1.0      # seconds before a tag is considered lost

        # --- Batch-specific tuning ---
        # Total items the onboard storage can hold before forcing a
        # return trip, regardless of category mix.
        self.CAPACITY = 4

        # If at least one item has been collected but nothing new has
        # been found in this many seconds, give up searching early and
        # head back rather than waiting for full capacity.
        self.SEARCH_GIVE_UP_TIME = 20.0

        # Count of items collected per category so far this run. Keyed
        # by tag ID, matching CATEGORY_NAMES.
        self.collected_counts = {tag_id: 0 for tag_id in CATEGORY_NAMES}
        self.search_start_time = self.get_clock().now()

        # Subscriptions for the tag detector node.
        self.pose_sub = self.create_subscription(
            PoseStamped, "/tag_pose", self.tag_pose_callback, 10
        )
        self.id_sub = self.create_subscription(
            Int32, "/tag_id", self.tag_id_callback, 10
        )

        self.get_logger().info(
            "Challenge Node (batch skeleton) initialized! Starting control loop..."
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

    def total_collected(self):
        return sum(self.collected_counts.values())

    def control_loop(self):
        """
        Main State Machine Loop. Runs at 10 Hz.
        """

        # Timeout: mark invisible if no tag frame received recently.
        # Given - don't remove it, your states rely on target_visible
        # being accurate.
        time_since_seen = (self.get_clock().now() - self.last_tag_time).nanoseconds / 1e9
        if time_since_seen > self.LOST_TIMEOUT:
            self.target_visible = False



        # State 1: SEARCHING
        if self.state == State.SEARCHING:
            # TODO:
            #   1. If no tag is visible, rotate in place to keep looking
            #      (identical to the shuttle version).
            #   2. If a tag becomes visible, stop and switch to
            #      State.APPROACHING.
            #   3. Batch-specific: if you've already collected at least
            #      one item AND haven't seen anything new for longer
            #      than self.SEARCH_GIVE_UP_TIME, stop searching early
            #      and switch to State.RETURNING instead of continuing
            #      to look. (self.search_start_time is provided but not
            #      yet used - decide when it should be reset.)
            #
            # Example:
            #   if not self.target_visible:
            #       self.robot.base.drive(linear=0.0, angular=0.3)
            #
            #       time_searching = (
            #           self.get_clock().now() - self.search_start_time
            #       ).nanoseconds / 1e9
            #       if (self.total_collected() > 0
            #               and time_searching > self.SEARCH_GIVE_UP_TIME):
            #           self.robot.base.stop()
            #           self.state = State.RETURNING
            #   else:
            #       self.robot.base.stop()
            #       self.state = State.APPROACHING
            self.get_logger().warn(
                "SEARCHING not implemented yet", throttle_duration_sec=2
            )



        # State 2: APPROACHING
        elif self.state == State.APPROACHING:
            # TODO: identical logic to the shuttle version - copy your
            # working implementation from there once you have it.
            #   1. If the tag is no longer visible, go back to SEARCHING.
            #   2. Compute dist_error and angle_error.
            #   3. Close enough and centered enough -> stop, go to
            #      State.PICKING.
            #   4. Otherwise compute angular_speed/linear_speed and
            #      drive.
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
            #   1. Call whatever ArmController sequence picks up the
            #      item off the ground (grab_bag()/lift_bag() or your
            #      own, same as the shuttle version).
            #   2. Move on to State.STOWING (NOT SORTING - the item goes
            #      into onboard storage first, not the final bin).
            #
            # Example:
            #   self.robot.arm.grab_bag()
            #   self.robot.arm.lift_bag()
            #   self.state = State.STOWING
            self.get_logger().warn(
                "PICKING not implemented yet", throttle_duration_sec=2
            )



        # State 4: STOWING
        elif self.state == State.STOWING:
            # TODO:
            #   1. Look at self.target_id / CATEGORY_NAMES to determine
            #      the category.
            #   2. Call the matching stow_X() arm method (you'll need to
            #      design and add these to arm.py - see the module
            #      docstring's physical-assumption note).
            #   3. Increment self.collected_counts for that category.
            #   4. Reset target_visible/target_id.
            #   5. If self.total_collected() has reached self.CAPACITY,
            #      go to State.RETURNING. Otherwise back to
            #      State.SEARCHING to look for more.
            #
            # Example (only 2 of 3-4 categories shown - extend the
            # pattern for the rest):
            #   if self.target_id == 0:
            #       self.robot.arm.stow_burnable()
            #       self.collected_counts[0] += 1
            #   elif self.target_id == 1:
            #       self.robot.arm.stow_pet_bottle()
            #       self.collected_counts[1] += 1
            #   else:
            #       self.get_logger().warn("Unknown Tag ID! Defaulting to burnable.")
            #       self.robot.arm.stow_burnable()
            #       self.collected_counts[0] += 1
            #
            #   self.target_visible = False
            #   self.target_id = -1
            #
            #   if self.total_collected() >= self.CAPACITY:
            #       self.state = State.RETURNING
            #   else:
            #       self.state = State.SEARCHING
            self.get_logger().warn(
                "STOWING not implemented yet", throttle_duration_sec=2
            )




        # State 5: RETURNING
        elif self.state == State.RETURNING:
            # TODO: this is the hard, open-ended one - see the module
            # docstring for two possible approaches (dead reckoning, or
            # a second ArUco tag at the drop-off point). There's no
            # single "correct" example to give here since it depends
            # entirely on which approach you pick.
            #
            # Whatever you implement, once the robot has actually
            # reached the drop-off point, stop the base and transition
            # to State.SORTING.
            self.get_logger().warn(
                "RETURNING not implemented yet - see module docstring "
                "for approaches", throttle_duration_sec=2
            )



        # State 6: SORTING
        elif self.state == State.SORTING:
            # TODO:
            #   1. For each category with collected_counts > 0, call the
            #      matching empty_X() arm method to dump that onboard
            #      compartment into the real external bin.
            #   2. Once everything's emptied, reset collected_counts
            #      back to zero for the next run and go to
            #      State.FINISHED.
            #
            # Example (only 2 of 3-4 categories shown):
            #   if self.collected_counts[0] > 0:
            #       self.robot.arm.empty_burnable()
            #   if self.collected_counts[1] > 0:
            #       self.robot.arm.empty_pet_bottle()
            #
            #   self.collected_counts = {tag_id: 0 for tag_id in CATEGORY_NAMES}
            #   self.state = State.FINISHED
            self.get_logger().warn(
                "SORTING not implemented yet", throttle_duration_sec=2
            )



        # State 7: FINISHED
        elif self.state == State.FINISHED:
            # Given - simple enough there's not much to design here.
            # Feel free to add a victory pose or a final summary log.
            self.robot.base.stop()
            self.get_logger().info(
                "Batch complete!", throttle_duration_sec=5
            )


def main(args=None):
    rclpy.init(args=args)
    node = ChallengeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()