import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='blueboat',
        description='Name of the robot'
    )

    xacro_file = PathJoinSubstitution([
        FindPackageShare('blueboat_stonefish'),
        "urdf",
        "blueboat.xacro"
    ])

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[{
            "robot_description": Command(["xacro ", xacro_file]),
            "use_sim_time": False,
        }],
        output="screen",
    )

    namespace_action = GroupAction(
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([
                        FindPackageShare("stonefish_ros2"),
                        "launch",
                        "stonefish_simulator.launch.py",
                    ])
                ),
                launch_arguments={
                    "simulation_data": PathJoinSubstitution([
                        FindPackageShare("blueboat_stonefish"),
                        "data",
                    ]),
                    "scenario_desc": PathJoinSubstitution([
                        FindPackageShare("blueboat_stonefish"),
                        "scenarios",
                        "blueboat_cirtesu_full_tank.scn",
                    ]),
                    "simulation_rate": "100.0",
                    "window_res_x": "1200",
                    "window_res_y": "800",
                    "rendering_quality": "high",
                    "use_sim_time": "false",
                }.items(),
            ),
        ]
    )

    # world_ned -> map
    world_to_map = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="world_ned_to_map",
        arguments=["0", "0", "0", "0", "0", "3.1416", "world_ned", "map"],
        output="screen",
    )

    # map -> cirtesu_base_link
    map_to_cirtesu = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="map_to_cirtesu_base_link",
        arguments=["0", "0", "0", "3.1416", "0", "3.1416", "map", "cirtesu_base_link"],
        output="screen",
    )

    cirtesu_mesh = Node(
        package="blueboat_stonefish",
        executable="cirtesu_mesh_marker.py",
        name="cirtesu_mesh_marker",
        output="screen",
        parameters=[{"use_sim_time": False}],
    )

    rviz_cfg = PathJoinSubstitution([
        FindPackageShare("blueboat_stonefish"),
        "config",
        "blueboat_cirtesu_config.rviz",
    ])
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        parameters=[{"use_sim_time": False}],
        arguments=["-d", rviz_cfg],
        output="screen",
    )

    # Livox CustomMsg -> PointCloud2 
    livox2_to_pc2_node = Node(
        package="livox2_to_pc2",
        executable="livox2_to_pc2",
        name="livox2_to_pc2",
        output="screen",
        parameters=[{
            "in_topic": "/stonefish_ros2/blueboat/livox",
            "out_topic": "/blueboat/livox/points",
            "frame_id": "blueboat/lidar_front",
            "include_ring": True,
            "reliability": "best_effort",
        }],
    )

    # INCLUDE: FastLIO + Localizer stack
    fastlio_loc_include = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("blueboat_stonefish"),
                "launch",
                "fastlio_localization.launch.py",
            ])
        ),
        launch_arguments={
            "use_sim_time": "false",
            # optional: 
            # "fastlio_cfg": PathJoinSubstitution([FindPackageShare("fast_lio"), "config", "mid360.yaml"]),
            # "localizer_cfg": PathJoinSubstitution([FindPackageShare("localizer"), "config", "localizer.yaml"]),
        }.items(),
    )

    return LaunchDescription([
        robot_name_arg,
        robot_state_publisher_node,
        namespace_action,
        world_to_map,
        map_to_cirtesu,
        cirtesu_mesh,
        livox2_to_pc2_node,
        fastlio_loc_include,
        rviz_node,
    ])