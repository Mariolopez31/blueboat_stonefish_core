#!/usr/bin/env python3

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener


class TfDebugPoses(Node):
    def __init__(self):
        super().__init__("tf_debug_poses")

        self.declare_parameter("world_frame", "world_ned")
        self.declare_parameter("map_frame", "map")
        self.declare_parameter("base_link_enu_frame", "blueboat/base_link_enu")
        self.declare_parameter("base_link_frame", "blueboat/base_link")
        self.declare_parameter("base_link_enu_topic", "/debug/base_link_enu_pose")
        self.declare_parameter("map_base_link_enu_topic", "/debug/map_base_link_enu_pose")
        self.declare_parameter("base_link_topic", "/debug/base_link_pose")
        self.declare_parameter("publish_rate_hz", 10.0)

        self.world_frame = self.get_parameter("world_frame").get_parameter_value().string_value
        self.map_frame = self.get_parameter("map_frame").get_parameter_value().string_value
        self.base_link_enu_frame = self.get_parameter(
            "base_link_enu_frame").get_parameter_value().string_value
        self.base_link_frame = self.get_parameter(
            "base_link_frame").get_parameter_value().string_value
        base_link_enu_topic = self.get_parameter(
            "base_link_enu_topic").get_parameter_value().string_value
        map_base_link_enu_topic = self.get_parameter(
            "map_base_link_enu_topic").get_parameter_value().string_value
        base_link_topic = self.get_parameter("base_link_topic").get_parameter_value().string_value
        publish_rate_hz = self.get_parameter("publish_rate_hz").get_parameter_value().double_value

        self.tf_buffer = Buffer(cache_time=Duration(seconds=5.0))
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.base_link_enu_pub = self.create_publisher(PoseStamped, base_link_enu_topic, 10)
        self.map_base_link_enu_pub = self.create_publisher(PoseStamped, map_base_link_enu_topic, 10)
        self.base_link_pub = self.create_publisher(PoseStamped, base_link_topic, 10)

        timer_period = 0.1 if publish_rate_hz <= 0.0 else 1.0 / publish_rate_hz
        self.timer = self.create_timer(timer_period, self.publish_debug_poses)

        self.get_logger().info(
            "Publishing TF debug poses: "
            f"{self.world_frame} -> {self.base_link_enu_frame} on {base_link_enu_topic}, "
            f"{self.map_frame} -> {self.base_link_enu_frame} on {map_base_link_enu_topic}, "
            f"{self.world_frame} -> {self.base_link_frame} on {base_link_topic}"
        )

    def publish_debug_poses(self):
        self._publish_pose(self.base_link_enu_pub, self.world_frame, self.base_link_enu_frame)
        self._publish_pose(self.map_base_link_enu_pub, self.map_frame, self.base_link_enu_frame)
        self._publish_pose(self.base_link_pub, self.world_frame, self.base_link_frame)

    def _publish_pose(self, publisher, parent_frame, child_frame):
        try:
            transform = self.tf_buffer.lookup_transform(
                parent_frame,
                child_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except TransformException as exc:
            self.get_logger().debug(
                f"TF lookup failed for {parent_frame} -> {child_frame}: {exc}"
            )
            return

        msg = PoseStamped()
        msg.header = transform.header
        msg.pose.position.x = transform.transform.translation.x
        msg.pose.position.y = transform.transform.translation.y
        msg.pose.position.z = transform.transform.translation.z
        msg.pose.orientation = transform.transform.rotation
        publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TfDebugPoses()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
