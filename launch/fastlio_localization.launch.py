from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    fastlio_cfg = LaunchConfiguration("fastlio_cfg")
    localizer_cfg = LaunchConfiguration("localizer_cfg")

    pcd_path = LaunchConfiguration("pcd_path")
    init_x = LaunchConfiguration("init_x")
    init_y = LaunchConfiguration("init_y")
    init_z = LaunchConfiguration("init_z")
    init_yaw = LaunchConfiguration("init_yaw")
    init_roll = LaunchConfiguration("init_roll")
    init_pitch = LaunchConfiguration("init_pitch")
    relocalize_delay = LaunchConfiguration("relocalize_delay")

    fastlio_node = Node(
        package="fast_lio",
        executable="fastlio_mapping",
        name="laser_mapping",
        output="screen",
        parameters=[fastlio_cfg, {"use_sim_time": use_sim_time}],
    )

    localizer_node = Node(
        package="localizer",
        namespace="localizer",
        executable="localizer_node",
        name="localizer_node",
        output="screen",
        parameters=[{"config_path": localizer_cfg}],
    )

    # Construimos un string YAML completo
    req = [
        TextSubstitution(text="{pcd_path: '"), pcd_path,
        TextSubstitution(text="', x: "), init_x,
        TextSubstitution(text=", y: "), init_y,
        TextSubstitution(text=", z: "), init_z,
        TextSubstitution(text=", yaw: "), init_yaw,
        TextSubstitution(text=", roll: "), init_roll,
        TextSubstitution(text=", pitch: "), init_pitch,
        TextSubstitution(text="}")
    ]

    # OJO: aquí usamos bash -lc para que el argumento se pase como UNA sola cadena
    relocalize_call = ExecuteProcess(
        cmd=[
            "bash", "-lc",
            ["ros2 service call /localizer/relocalize interface/srv/Relocalize \"", *req, TextSubstitution(text="\"")]
        ],
        output="screen",
    )

    relocalize_timer = TimerAction(
        period=relocalize_delay,
        actions=[relocalize_call],
    )

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        DeclareLaunchArgument(
            "fastlio_cfg",
            default_value=PathJoinSubstitution([FindPackageShare("fast_lio"), "config", "mid360.yaml"]),
        ),
        DeclareLaunchArgument(
            "localizer_cfg",
            default_value=PathJoinSubstitution([FindPackageShare("localizer"), "config", "localizer.yaml"]),
        ),
        DeclareLaunchArgument(
            "pcd_path",
            default_value="/home/mario-cirtesu/cirtesu_ws/src/fast_lio_ros2/PCD/scans_23.pcd",
        ),
        DeclareLaunchArgument("init_x", default_value="0.0"),
        DeclareLaunchArgument("init_y", default_value="0.0"),
        DeclareLaunchArgument("init_z", default_value="0.0"),
        DeclareLaunchArgument("init_yaw", default_value="0.0"),
        DeclareLaunchArgument("init_roll", default_value="0.0"),
        DeclareLaunchArgument("init_pitch", default_value="0.0"),
        DeclareLaunchArgument("relocalize_delay", default_value="3.0"),

        fastlio_node,
        localizer_node,
        relocalize_timer,
    ])