# ROS2 Failure Detection and Recovery

This project implements a real-time failure detection and recovery system for robotic navigation using ROS2 and the Navigation2 (Nav2) stack.

## Overview
The system monitors robot telemetry (pose and velocity) to detect when navigation fails (e.g., oscillation or lack of progress) and automatically triggers recovery actions.

## Features
- Real-time failure detection using /amcl_pose and /cmd_vel
- Offline analysis of CSV telemetry data
- Automated recovery via costmap clearing and goal retry
- Closed-loop detection → recovery pipeline

## Project Structure
failure_project/
  realtime_failure_detector.py
  smart_recovery_controller.py
  analyze_runs.py
  plot_results.py
  run_*.csv

## How to Run
1. Launch Nav2:
   ros2 launch nav2_bringup tb3_simulation_launch.py

2. Run detection:
   python3 realtime_failure_detector.py

3. Run recovery:
   python3 smart_recovery_controller.py

## Results
- Successful runs: high displacement, consistent forward motion
- Failed runs: low displacement, high rotation (oscillation)
- Recovery works for transient failures but not unreachable goals

## Author
Rhea Modey  
NC State University – CSC591
