#!/usr/bin/env python3
import time
from geometry_msgs.msg import Twist


class BaseController:

    def __init__(self, node, publish_rate_hz=30.0, hold_timeout_sec=0.25):
        self.node = node
        self.dt = 1.0 / publish_rate_hz
        self.hold_timeout_sec = hold_timeout_sec
        self.cmd_pub = node.create_publisher(Twist, "/commands/velocity", 10)

        # Target & current velocities
        self.linear_speed = 0.35       # m/s
        self.angular_speed = 0.90      # rad/s
        self.max_linear_accel = 1.2    # m/s^2
        self.max_angular_accel = 1.8   # rad/s^2

        self._target_linear = 0.0
        self._target_angular = 0.0
        self._curr_linear = 0.0
        self._curr_angular = 0.0
        self._last_input_time = 0.0
        self._active = False

        # Non-blocking timer driving continuous smooth motion
        self._timer = node.create_timer(self.dt, self._update_loop)

    def _slew(self, current, target, max_rate, dt):
        max_delta = max_rate * dt
        if target > current + max_delta:
            return current + max_delta
        if target < current - max_delta:
            return current - max_delta
        return target

    def _set_target(self, linear, angular):
        self._target_linear = float(linear)
        self._target_angular = float(angular)
        self._last_input_time = time.monotonic()
        self._active = True

    # --- Continuous button-hold methods ---
    def hold_forward(self):
        self._set_target(self.linear_speed, 0.0)

    def hold_backward(self):
        self._set_target(-self.linear_speed, 0.0)

    def hold_left(self):
        self._set_target(0.0, self.angular_speed)

    def hold_right(self):
        self._set_target(0.0, -self.angular_speed)

    def release(self):
        """Call when the button is released."""
        self._target_linear = 0.0
        self._target_angular = 0.0
        self._active = False

    def stop_immediate(self):
        """Emergency / hard stop."""
        self._target_linear = 0.0
        self._target_angular = 0.0
        self._curr_linear = 0.0
        self._curr_angular = 0.0
        self._active = False
        self.cmd_pub.publish(Twist())

    def _update_loop(self):
        now = time.monotonic()

        # If hold events are being streamed and stop arriving, safely zero the target
        if self._active and (now - self._last_input_time) > self.hold_timeout_sec:
            self._target_linear = 0.0
            self._target_angular = 0.0
            self._active = False

        self._curr_linear = self._slew(
            self._curr_linear, self._target_linear, self.max_linear_accel, self.dt
        )
        self._curr_angular = self._slew(
            self._curr_angular, self._target_angular, self.max_angular_accel, self.dt
        )

        # Avoid unnecessary jitter once completely stopped
        if (
            not self._active
            and abs(self._curr_linear) < 1e-4
            and abs(self._curr_angular) < 1e-4
        ):
            self._curr_linear = 0.0
            self._curr_angular = 0.0
            return

        msg = Twist()
        msg.linear.x = self._curr_linear
        msg.angular.z = self._curr_angular
        self.cmd_pub.publish(msg)