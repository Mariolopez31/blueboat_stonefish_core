#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from tf_transformations import quaternion_from_euler

CIRTESU_MESH_PATH = "package://blueboat_stonefish/meshes/cirtesu.dae"

class CirtesuMesh(Node):
    def __init__(self):
        super().__init__("cirtesu_mesh_marker")
        self.pub = self.create_publisher(MarkerArray, "/cirtesu/mesh", 1)
        self.timer = self.create_timer(1.0, self.tick)

    def tick(self):
        ma = MarkerArray()
        m = Marker()
        m.header.frame_id = "cirtesu_base_link"
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = "cirtesu"
        m.id = 1
        m.type = Marker.MESH_RESOURCE
        m.action = Marker.ADD
        m.mesh_resource = CIRTESU_MESH_PATH
        m.mesh_use_embedded_materials = True

        m.scale.x = 1.0
        m.scale.y = 1.0
        m.scale.z = 1.0

        m.pose.position.x = 0.0
        m.pose.position.y = 0.0
        m.pose.position.z = 0.2

        qx, qy, qz, qw = quaternion_from_euler(3.1416, 0.0, 0.0)
        m.pose.orientation.x = float(qx)
        m.pose.orientation.y = float(qy)
        m.pose.orientation.z = float(qz)
        m.pose.orientation.w = float(qw)

        m.color.a = 1.0
        ma.markers.append(m)
        self.pub.publish(ma)

def main():
    rclpy.init()
    n = CirtesuMesh()
    rclpy.spin(n)
    n.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()