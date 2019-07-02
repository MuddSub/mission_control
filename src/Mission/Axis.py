import numpy as np
import rospy
import rospkg
from mission_control.srv import *
from std_msgs.msg import String, Float64

class Axis:
    _axis = ""
    _enabled = False
    _inputs = {"IMU_POS" : 0, "IMU_ACCEL" : 1, "DEPTH" : 2, "CAM_FRONT": 3, "CAM_BOTTOM" : 4, "LOCALIZE": 5}
    _zeros = {"IMU_POS" : 0, "IMU_ACCEL" : 0, "DEPTH" : 0, "CAM_FRONT": 0, "CAM_BOTTOM" : 0, "LOCALIZE": 0}
    plantState = 0
    _input = ""

    def __init__(self, name):
        self._axis = name
        paramName = "/TOPICS/"
        paramName +=  name.upper()
        self._sub = rospy.Subscriber("/none", Float64, self.plantStateCallback)

    def plantStateCallback(self, data):
        self.plantState = data

    def updatePlantTopic(self):
        self._sub.unregister()
        paramName = "/TOPICS/"
        paramName += self._axis.upper()
        self.plantTopic = rospy.get_param(paramName)
        rospy.logwarn("THE TOPIC IS {}".format(self.plantTopic))
        self._sub = rospy.Subscriber(self.plantTopic, Float64, self.plantStateCallback)

    def setEnabled(self, val=True):
        self._enabled = val
        rospy.wait_for_service('EnabledService')
        try:
            enabledServiceProxy = rospy.ServiceProxy('EnabledService', EnabledService)
            res = enabledServiceProxy(self._axis, val)
            return res.success
        except rospy.ServiceException, e:
            print "Service call failed: %s" %e

    def setControlEffort(self, val=0):
        rospy.loginfo("Disabling %s control loop", self._axis)
        self.setEnabled(False);
        self._enabled = False
        rospy.wait_for_service('ThrustOverrideService')
        try:
            enabledServiceProxy = rospy.ServiceProxy('ThrustOverrideService', ThrustOverrideService)
            res = enabledServiceProxy(self._axis, val)
            return res.success
        except rospy.ServiceException, e:
            print "Service call failed: %s" %e


    def setSetpoint(self, val=0):
        if(not self._enabled):
            rospy.logwarn("Make sure the loop is enabled")
        rospy.wait_for_service('SetpointService')
        try:
            enabledServiceProxy = rospy.ServiceProxy('SetpointService', SetpointService)
            res = enabledServiceProxy(self._axis, val)
            return res.success
        except rospy.ServiceException, e:
            print "Service call failed: %s" %e


    def setZero(self, zero=None):
        sum = 0.0
	rospy.logwarn("HEREHEREHERHE {}".format(self.plantTopic))
        for i in range(10):
            sum += rospy.wait_for_message(self.plantTopic, Float64).data
        avg = sum / 10
        rospy.loginfo("Setting heave zero on {} to {}".format(self._input, avg))
        self._zeros[self._input] = avg

    def goTo(self, target, delay = 1):
        self.setSetpoint(target + self._zeros[_input])
        tStart = rospy.get_time()
        while(rospy.get_time() - tStart < 1000*delay):
            rospy.spinOnce()
            rospy.sleep(0.1)

    def increment(self, target, delay = 1):
        self.setSetpoint(target + self.plantState)
        tStart = rospy.get_time()
        while(rospy.get_time() - tStart < 1000*delay):
            rospy.spinOnce()
            rospy.sleep(0.1)


    def setInput(self, val):
        rospy.loginfo(self._inputs[val])

        if(not self._enabled):
            rospy.logwarn("Make sure the loop is enabled")
        rospy.wait_for_service('InputTypeService')
        try:
            enabledServiceProxy = rospy.ServiceProxy('InputTypeService', InputService)
            res = enabledServiceProxy(self._axis, self._inputs[val])
            self._input = val
        except rospy.ServiceException, e:
            print "Service call failed: %s" %e
	    return False
        self.updatePlantTopic()
        return res.success