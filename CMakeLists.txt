cmake_minimum_required(VERSION 3.5)
project(blueboat_stonefish_core)

# Detect Raspberry-like architectures and skip build there
set(TARGET_RASPBERRY FALSE)
if(CMAKE_SYSTEM_PROCESSOR MATCHES "armv7|aarch64")
  set(TARGET_RASPBERRY TRUE)
endif()

if(TARGET_RASPBERRY)
  message(WARNING
    "Package '${PROJECT_NAME}' will NOT be compiled because a Raspberry/ARM "
    "architecture was detected "
    "(CMAKE_SYSTEM_PROCESSOR='${CMAKE_SYSTEM_PROCESSOR}')."
  )
  find_package(ament_cmake REQUIRED)
  ament_package()
  return()
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(stonefish_ros2 REQUIRED)
find_package(urdf REQUIRED)
find_package(xacro REQUIRED)
find_package(robot_state_publisher REQUIRED)

enable_language(C)

include_directories(
  include
  ${std_msgs_INCLUDE_DIRS}
  ${stonefish_ros2_INCLUDE_DIRS}
)

set(PYTHON_EXECUTABLE /usr/bin/python3)

install(
  PROGRAMS
    scripts/odom2tf.py
    scripts/cirtesu_mesh_marker.py
  DESTINATION lib/${PROJECT_NAME}
)

# Launch files: install only once
install(
  DIRECTORY data/launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

# Data folders except launch
install(
  DIRECTORY
    data/blueboat
    data/cirtesu
    data/net
    data/opti_blueboat
    data/resources
  DESTINATION share/${PROJECT_NAME}/data
)

install(
  DIRECTORY scenarios urdf meshes config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()