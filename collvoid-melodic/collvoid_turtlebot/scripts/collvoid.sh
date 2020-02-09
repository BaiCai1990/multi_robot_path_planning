#!/usr/bin/env bash

#################################################
# @author:  Nele Traichel
# @date:    2020/01/30
# @brief:   Executes the collvoid multi-robot navigation.
# @todo: * how to work with params???
#	 * how to send goal?
#################################################

# source
source ~/.bashrc

# script parameters
SESSION_NAME="collvoid"
NUM=0
MAPPING=${MAPPING:=amcl}
WORLD=""
NUM_ROBOT=2

# start tmux
tmux new-session -s $SESSION_NAME -d

# #### roscore
# NUM=$((++NUM))
# tmux new-window -t $SESSION_NAME -n "roscore"
# tmux send-keys -t $SESSION_NAME:$NUM "roscore" C-m
# read -t 3

# #### rqt
# NUM=$((++NUM))
# tmux new-window -t $SESSION_NAME -n "rqt"
# tmux send-keys -t $SESSION_NAME:$NUM "rqt" C-m
# read -t 3

#### simulation incl. spawn
NUM=$((++NUM))
tmux new-window -t $SESSION_NAME -n "world_and_spawn"
tmux send-keys -t $SESSION_NAME:$NUM "roslaunch collvoid_turtlebot simulation_simple.launch" C-m
read -t 3


##### map & amcl
X=0
while [ $X -le $NUM_ROBOT ]; do
  X=$((X + 1))

  # amcl
  NUM=$((++NUM))
  tmux new-window -t $SESSION_NAME -n "amcl_${X}"
  tmux send-keys -t $SESSION_NAME:$NUM "roslaunch collvoid_turtlebot amcl_simple.launch robot:=tb3_${X}" C-m

  # move base
  NUM=$((++NUM))
  tmux new-window -t $SESSION_NAME -n "move_base_${X}"
  tmux send-keys -t $SESSION_NAME:$NUM "roslaunch collvoid_turtlebot move_base_dwa.launch robot:=tb3_${X}" C-m
  read -t 3
done

# goal ???
#NUM=$((++NUM))
#tmux new-window -t $SESSION_NAME -n "waypoints"
#tmux send-keys -t $SESSION_NAME:$NUM "roslaunch benchmark waypoints.launch use_settings_file:=$USE_SETTINGS_FILE" C-m

#### rviz
NUM=$((++NUM))
tmux new-window -t $SESSION_NAME -n "rviz"
tmux send-keys -t $SESSION_NAME:$NUM "roslaunch turtlebot3_gazebo turtlebot3_gazebo_rviz.launch" C-m
read -t 3


# attach to the tmux session
tmux attach