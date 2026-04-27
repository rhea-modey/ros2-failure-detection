import math
from collections import deque

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, Twist
from std_msgs.msg import Bool


class RealtimeFailureDetector(Node):
    def __init__(self):
        super().__init__("realtime_failure_detector")

        # Sliding window of recent states
        self.window = deque(maxlen=50)  # ~10 sec at 5 Hz

        self.latest_pose = None
        self.latest_linear = 0.0
        self.latest_angular = 0.0

        self.failure_active = False

        # Subscriptions
        self.create_subscription(
            PoseWithCovarianceStamped,
            "/amcl_pose",
            self.pose_cb,
            10
        )

        self.create_subscription(
            Twist,
            "/cmd_vel",
            self.cmd_cb,
            10
        )

        # Publisher
        self.failure_pub = self.create_publisher(Bool, "/failure_detected", 10)

        # Timer
        self.timer = self.create_timer(0.2, self.check_failure)

        self.get_logger().info("Realtime failure detector started.")
        self.get_logger().info("Detects: low movement + high rotation → failure.")

    def pose_cb(self, msg):
        self.latest_pose = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
        )

    def cmd_cb(self, msg):
        self.latest_linear = msg.linear.x
        self.latest_angular = msg.angular.z

    def check_failure(self):
        if self.latest_pose is None:
            return

        now = self.get_clock().now().nanoseconds / 1e9
        x, y = self.latest_pose

        # Add current state to window
        self.window.append({
            "time": now,
            "x": x,
            "y": y,
            "linear": self.latest_linear,
            "angular": self.latest_angular,
        })

        # Need enough data
        if len(self.window) < 20:
            return

        first = self.window[0]
        last = self.window[-1]

        # Compute features
        displacement = math.sqrt(
            (last["x"] - first["x"])**2 +
            (last["y"] - first["y"])**2
        )

        moving_rows = sum(
            1 for r in self.window if abs(r["linear"]) > 0.01
        )

        rotating_rows = sum(
            1 for r in self.window if abs(r["angular"]) > 0.1
        )

        # Heuristic (based on your data)
        failure = (
            displacement < 0.10 and
            moving_rows < 3 and
            rotating_rows > 8
        )

        # Publish result
        msg = Bool()
        msg.data = failure
        self.failure_pub.publish(msg)

        # --- PRINT STABLE STATE ---
        if not failure:
            self.get_logger().info(
                f"STABLE: disp={displacement:.3f}, "
                f"move={moving_rows}, rot={rotating_rows}",
                throttle_duration_sec=2
            )

        # --- PRINT FAILURE TRANSITION ---
        if failure and not self.failure_active:
            self.failure_active = True
            self.get_logger().warn(
                f"FAILURE DETECTED: disp={displacement:.3f}, "
                f"move={moving_rows}, rot={rotating_rows}"
            )

        # --- PRINT RECOVERY ---
        elif not failure and self.failure_active:
            self.failure_active = False
            self.get_logger().info("Failure cleared. Robot stable again.")


def main():
    rclpy.init()
    node = RealtimeFailureDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()