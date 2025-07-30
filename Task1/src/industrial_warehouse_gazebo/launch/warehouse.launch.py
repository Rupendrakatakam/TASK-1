#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    
    pkg_industrial_warehouse_gazebo = get_package_share_directory('industrial_warehouse_gazebo')

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'),
        ),
        launch_arguments={'world': os.path.join(pkg_industrial_warehouse_gazebo, 'worlds', 'industrial_warehouse.world')}.items()
    )

    return LaunchDescription([
        gazebo
    ])