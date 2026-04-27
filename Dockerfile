FROM ros:jazzy

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    git \
    curl \
    lsb-release \
    gnupg \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    "ros-jazzy-nav2-minimal-tb*" \
 && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc

WORKDIR /root
CMD ["/bin/bash"]

