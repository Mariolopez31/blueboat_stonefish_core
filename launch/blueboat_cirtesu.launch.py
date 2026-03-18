import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Declare launch arguments
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
            'use_sim_time':True
        }]
    )

    # Group action with namespace
    namespace_action = GroupAction(
        actions=[
            # Include the simulator launch file
            IncludeLaunchDescription(
                PathJoinSubstitution([
                    FindPackageShare('stonefish_ros2'), 'launch', 'stonefish_simulator.launch.py'
                ]),
                launch_arguments={
                    'simulation_data': PathJoinSubstitution([
                        FindPackageShare('blueboat_stonefish'), 'data'
                    ]),
                    'scenario_desc': PathJoinSubstitution([
                        FindPackageShare('blueboat_stonefish'), 'scenarios' ,'blueboat_cirtesu_full_tank.scn'
                    ]),
                    'simulation_rate': '100.0',
                    'window_res_x': '1200',
                    'window_res_y': '800',
                    'rendering_quality': 'high',
                }.items()
            ),
        ]
    )
    #core_sim = os.path.join(get_package_share_directory('bluerov2_cirtesu_core'), 'launch', 'core_sim.launch.py')
    #mav2ros = os.path.join(get_package_share_directory('bluerov_mav2ros'), 'launch', 'bluerov_mav2ros.launch.py')

    return LaunchDescription([
        robot_name_arg,
        robot_state_publisher_node,
        namespace_action
    ,
        Node(
        package='blueboat_stonefish',
        executable='odom2tf.py',
        output='screen',
        parameters=[{'use_sim_time': True}],
        ),
            
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            parameters=[{'use_sim_time': True}],
            arguments=['-d', PathJoinSubstitution(['src', 'blueboat_stonefish', 'config', 'blueboat_cirtesu_config.rviz'])],
            output='screen'
        ),

        # Launch core_sim
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(core_sim),
        #     launch_arguments={}.items()  # Aquí puedes añadir argumentos si es necesario
        # ),

        # # Launch bluerov_mav2ros
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource(mav2ros),
        #     launch_arguments={}.items()  # Aquí puedes añadir argumentos si es necesario
        # ),
 
        ])


