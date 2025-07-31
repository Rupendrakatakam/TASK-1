#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_industrial_warehouse_gazebo = get_package_share_directory('industrial_warehouse_gazebo')
    world_path = os.path.join(pkg_industrial_warehouse_gazebo, 'worlds', 'industrial_warehouse.world')

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'),
        ),
        launch_arguments={'world': world_path}.items()
    )

    # Static transform publisher (optional)
    static_transform_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        arguments=['0', '0', '1.941', '0', '3.14', '0', 'world', 'camera_link']
    )

    # RViz2 (optional)
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2'
    )

    return LaunchDescription([
        gazebo,
        static_transform_publisher,
        rviz2
    ])
