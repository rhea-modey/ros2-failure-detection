import csv
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, Twist

class Logger(Node):
    def __init__(self):
        super().__init__('logger')
        self.x = None
        self.y = None
        self.lin = 0.0
        self.ang = 0.0

        self.file = open('telemetry_log.csv', 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['time', 'x', 'y', 'linear', 'angular'])

        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.pose_cb, 10)
        self.create_subscription(Twist, '/cmd_vel', self.cmd_cb, 10)
        self.create_timer(0.2, self.log)

        self.get_logger().info('Logger started. Waiting for /amcl_pose...')

    def pose_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.get_logger().info(f'Pose received: x={self.x:.3f}, y={self.y:.3f}', throttle_duration_sec=2)

    def cmd_cb(self, msg):
        self.lin = msg.linear.x
        self.ang = msg.angular.z

    def log(self):
        if self.x is None:
            return
        t = self.get_clock().now().nanoseconds / 1e9
        self.writer.writerow([t, self.x, self.y, self.lin, self.ang])
        self.file.flush()

def main():
    rclpy.init()
    node = Logger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.file.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()