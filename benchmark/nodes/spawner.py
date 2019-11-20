#!/usr/bin/env python

""" --------------------------------------------------------------
@author:    Johann Schmidt
@date:      November 2019
@brief:     Script used to spawn a turtlebot in a generic position
@todo:
------------------------------------------------------------- """

import sys
import roslib
from gazebo_msgs.srv import SpawnModel, DeleteModel, DeleteModelRequest, SpawnModelRequest
import rospy
import os
from geometry_msgs.msg import *
import tf.transformations as tft
from std_msgs.msg import Empty as EmptyMsg
from geometry_msgs.msg import Quaternion
import math
import ros_utils


NODE_NAME = "spawning_controller"


class RobotSpawner:
    """ Robot spawner.
    """

    def __init__(self, world):
        """ Init. method.
        :param world
        """
        self._world = world
        self._create_node()

    @staticmethod
    def _get_file_location(model_name, model_type, model_format="sdf"):
        """ Returns the file location path.
        :param model_name:
        :param model_type:
        :param model_format:
        :return: path
        """
        package, package_dir, file_name = "", "", ""
        if model_format == "sdf":
            package = 'turtlebot3_gazebo'
            file_name = '/models/' + model_name + '_' + model_type + "model.sdf"
        elif model_format == "urdf.xacro":
            package = 'turtlebot3_description'
            file_name = '/urdf/' + model_name + "_" + model_type + ".urdf.xacro"
        else:
            rospy.logerr("Model format " + model_format + " not supported!")
        try:
            package_dir = roslib.packages.get_pkg_dir(package)
        except:
            rospy.logerr("Package ({}) not found!".format(package))
        return package_dir + file_name

    @staticmethod
    def _load_model(file_path, model_format="sdf"):
        """ Call gazebo service to spawn model (see http://ros.org/wiki/gazebo).
        :param file_path:
        :param model_format:
        :return: srv_model, xml_string
        """
        srv_spawn_model, xml_string = None, None
        if model_format == "urdf":
            srv_spawn_model = rospy.ServiceProxy('/gazebo/spawn_urdf_model', SpawnModel)
            file_xml = open(file_path)
            xml_string = file_xml.read()
        elif model_format == "urdf.xacro":
            p = os.popen("rosrun xacro --inorder " + file_path)
            xml_string = p.read()
            p.close()
            srv_spawn_model = rospy.ServiceProxy('/gazebo/spawn_urdf_model', SpawnModel)
        elif model_format == "sdf":
            srv_spawn_model = rospy.ServiceProxy('/gazebo/spawn_gazebo_model', SpawnModel)
            file_xml = open(file_path)
            xml_string = file_xml.read()
        else:
            rospy.logerr('Model type not know. model_type = ' + model_format)
        return srv_spawn_model, xml_string

    @staticmethod
    def _delete_robot(model_name):
        """ Deletes the robot.
        :param model_name
        :return: request
        """
        srv_delete_model = rospy.ServiceProxy('gazebo/delete_model', DeleteModel)
        req = DeleteModelRequest()
        req.model_name = model_name
        exists = True
        try:
            res = srv_delete_model(model_name)
        except rospy.ServiceException as e:
            exists = False
            rospy.logdebug("Model %s does not exist in gazebo.", model_name)
        if exists:
            rospy.loginfo("Model %s already exists in gazebo. Model will be updated.", model_name)
        return req

    def _spawn_model(self, xml_string, name, namespace, pose):
        """ Spawns a model in a simulation world.
        :param name:
        :param namespace:
        :param model:
        :param pose:
        :param world:
        """
        rospy.wait_for_service('gazebo/spawn_sdf_model')
        spawn_model_prox = rospy.ServiceProxy('gazebo/spawn_sdf_model', SpawnModel)
        spawn_model_prox(name, xml_string, namespace, pose, self._world)

    def spawn(self, name, model_name, namespace, model_type,
              position, orientation, update_if_exist=False,
              use_launch_file=False, model_format="sdf"):
        """ Spawns a robot.
        :param name:
        :param model_name:
        :param namespace:
        :param model_type:
        :param position:
        :param orientation:
        :param update_if_exist:
        :param use_launch_file
        :param model_format:
        """
        if use_launch_file:
            self._call_spawn_launch(name, position, 0.0)
        else:
            pose = ros_utils.get_obj_pose(position, orientation)
            file_path = self._get_file_location(model_name, model_type, model_format)
            srv_spawn_model, xml_string = self._load_model(file_path, model_format)

            if update_if_exist:
                self._delete_robot(name)

            self._spawn_model(xml_string=xml_string, name=name, namespace=namespace, pose=pose)
            self._pub_sim_spawned()

    @staticmethod
    def _call_spawn_launch(name, position, yaw):
        """ Spawns a robot using a spawning launch file.
        """
        os.system("roslaunch benchmark spawn.launch model:=burger name:=tb3_" + name
                  + "pos_x:=" + str(position[0])
                  + "pos_y:=" + str(position[1])
                  + "pos_z:=" + str(position[2])
                  + "yaw:=" + str(yaw))

    @staticmethod
    def _pub_sim_spawned():
        """ Publishes an empty msg to sim_spawned if sim_time is used.
        """
        sim = rospy.get_param('/use_sim_time')
        if sim is True:
            rospy.loginfo('Running in simulation, publishing to /sim_spawned topic')
            pub = rospy.Publisher('/sim_spawned', EmptyMsg,
                                  latch=True, queue_size=10)
            pub.publish(EmptyMsg())
            pub.publish(EmptyMsg())
            pub.publish(EmptyMsg())

    @staticmethod
    def _create_node():
        """ Creates a node.
        """
        rospy.init_node(NODE_NAME, anonymous=True)
        rospy.sleep(5)
        rospy.wait_for_service("/gazebo/spawn_urdf_model")

