import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from nav2_msgs.srv import ClearEntireCostmap
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient


class SmartRecoveryController(Node):
    def __init__(self):
        super().__init__("smart_recovery_controller")

        self.failure_active = False
        self.recovery_in_progress = False
        self.current_goal = None
        self.retry_timer = None
        self.retry_count = 0
        self.max_retries = 2

        # Subscribe to failure detector
        self.create_subscription(Bool, "/failure_detected", self.failure_cb, 10)

        # Nav2 action client
        self.nav_client = ActionClient(self, NavigateToPose, "/navigate_to_pose")

        # Costmap clearing services (FIXED)
        self.clear_global_client = self.create_client(
            ClearEntireCostmap,
            "/global_costmap/clear_entirely_global_costmap"
        )

        self.clear_local_client = self.create_client(
            ClearEntireCostmap,
            "/local_costmap/clear_entirely_local_costmap"
        )

        self.get_logger().info("Smart Recovery Controller started.")

    def send_goal(self, x, y):
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Nav2 action server not available.")
            return

        self.current_goal = (x, y)
        self.retry_count = 0

        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.w = 1.0

        self.get_logger().info(f"Sending goal: ({x}, {y})")
        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_cb)

    def goal_response_cb(self, future):
        goal_handle = future.result()
        if goal_handle.accepted:
            self.get_logger().info("Goal accepted.")
        else:
            self.get_logger().error("Goal rejected.")

    def failure_cb(self, msg):
        if msg.data and not self.failure_active and not self.recovery_in_progress:
            self.failure_active = True
            self.recovery_in_progress = True

            if self.retry_count >= self.max_retries:
                self.get_logger().warn("Max retries reached. Not retrying again.")
                self.recovery_in_progress = False
                return

            self.retry_count += 1
            self.get_logger().warn(f"Failure detected. Starting recovery attempt {self.retry_count}.")

            self.clear_costmaps()
            self.start_retry_timer()

        elif not msg.data:
            self.failure_active = False

    def clear_costmaps(self):
        self.get_logger().info("Clearing costmaps if services are available...")

        if self.clear_global_client.wait_for_service(timeout_sec=3.0):
            self.clear_global_client.call_async(ClearEntireCostmap.Request())
            self.get_logger().info("Requested global costmap clear.")
        else:
            self.get_logger().warn("Global costmap clear service not available.")

        if self.clear_local_client.wait_for_service(timeout_sec=3.0):
            self.clear_local_client.call_async(ClearEntireCostmap.Request())
            self.get_logger().info("Requested local costmap clear.")
        else:
            self.get_logger().warn("Local costmap clear service not available.")

    def start_retry_timer(self):
        if self.retry_timer is not None:
            self.retry_timer.cancel()

        self.get_logger().info("Waiting 2 seconds before retrying original goal...")
        self.retry_timer = self.create_timer(2.0, self.retry_goal_once)

    def retry_goal_once(self):
        if self.retry_timer is not None:
            self.retry_timer.cancel()
            self.retry_timer = None

        if self.current_goal is None:
            self.get_logger().error("No stored goal to retry.")
            self.recovery_in_progress = False
            return

        x, y = self.current_goal

        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.w = 1.0

        self.get_logger().info(f"Retrying original goal: ({x}, {y})")
        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self.retry_response_cb)

    def retry_response_cb(self, future):
        goal_handle = future.result()

        if goal_handle.accepted:
            self.get_logger().info("Retry goal accepted.")
        else:
            self.get_logger().error("Retry goal rejected.")

        self.recovery_in_progress = False


def main():
    rclpy.init()
    node = SmartRecoveryController()

    # You can change this goal for testing
    node.send_goal(2.0, 2.5)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()