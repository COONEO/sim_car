#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_sim_car = get_package_share_directory('sim_car')
    pkg_joy = get_package_share_directory('joy')
    world = LaunchConfiguration("world")
    headless = "False"



    bringup_dir = get_package_share_directory('sim_car')
    launch_dir = os.path.join(bringup_dir, 'launch')
    world_config = DeclareLaunchArgument(
          'world',
          default_value=[os.path.join(pkg_sim_car, 'worlds', 'simple.world'), ''],
          description='SDF world file')

    use_simulator = "True" # LaunchConfiguration('use_simulator')


    # Specify the actions
    start_gazebo_server_cmd = ExecuteProcess(
        condition=IfCondition(use_simulator),
        cmd=['gzserver', '-s', 'libgazebo_ros_init.so',  '-s', 'libgazebo_ros_factory.so', world],
        cwd=[launch_dir], output='screen')

    start_gazebo_client_cmd = ExecuteProcess(
        condition=IfCondition(PythonExpression(
            [use_simulator, ' and not ', headless])),
        cmd=['gzclient'],
        cwd=[launch_dir], output='screen')

    rviz_config_path = os.path.join(pkg_sim_car, 'config', 'red-crash.rviz')
    print("-----------------: "+rviz_config_path)
    start_rviz2_cmd = ExecuteProcess(
        cmd=['rviz2','--display-config',rviz_config_path], 
        cwd=[launch_dir], 
        output='screen')


    bringup_dir = get_package_share_directory('nav2_bringup')
    bringup_launch_dir = os.path.join(bringup_dir, 'launch')
    nav2_params_path = os.path.join(get_package_share_directory('sim_car'), 'config/', 'nav2_params.yaml')

    nav_bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_launch_dir, 'bringup_launch.py')),
        launch_arguments={
                          #'namespace': namespace,
                          #'use_namespace': use_namespace,
                          'slam': "1",
                          'map': 'map.yaml',
                          #'use_sim_time': use_sim_time,
                          'params_file': nav2_params_path,
                          #'autostart': autostart}.items()
                        }.items()
        )



        # ros2 launch nav2_bringup bringup_launch.py slam:=1 map:=blank.yaml

    # # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )

    car = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            # os.path.join(pkg_sim_car, 'launch', 'spawn_red_crash.launch.py'),
            os.path.join(pkg_sim_car, 'launch', 'spawn_car.launch.py'),
        )
    )

    joy = Node(
            package='joy', executable='joy_node', output='screen')
    teleop_twist = Node(
            package='teleop_twist_joy', executable='teleop_node', output='screen', parameters=[os.path.join(pkg_sim_car, "config", "teleop_twist_joy.yaml")])

    ld = LaunchDescription()
    ld.add_action(world_config)
    ld.add_action(gazebo)
    # ld.add_action(start_gazebo_server_cmd)
    # ld.add_action(start_gazebo_client_cmd)
    ld.add_action(start_rviz2_cmd)
    ld.add_action(car)
    ld.add_action(joy)
    ld.add_action(teleop_twist)
    ld.add_action(nav_bringup_cmd)
    return ld
