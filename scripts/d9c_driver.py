#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy

import base64
import socket
import serial

from nmea_msgs.msg import Sentence
from std_msgs.msg import String



# init ---------------------------------
rospy.init_node('f9p_driver')

serial_port = rospy.get_param('~port', '/dev/ttyACM1')
#serial_baud = rospy.get_param('~baud', 230400)
serial_baud = rospy.get_param('~baud', 115200)

debug = rospy.get_param('~debug', False)

rtcmData = ""


# Main
if __name__ == '__main__':

	pub = rospy.Publisher('/caster/rtcm_data', String, queue_size=10)

	try:
		rospy.loginfo("serial port Open...")
		receiver = serial.Serial(port=serial_port, baudrate=serial_baud, timeout=2)

		rospy.loginfo("Ok")

		try:
			while not rospy.is_shutdown():
				rtk_datas = receiver.readline()
				pub.publish(base64.b64encode(rtk_datas))

				if debug:
					rospy.loginfo(rtk_datas)
				rospy.sleep(0)

		except serial.SerialException as ex:
			rospy.logerr( "SerialException error({0}): {1}".format(ex.errno, ex.strerror))
		except rospy.ROSInterruptException:
			pass
		finally:
			receiver.close()  # Close GPS serial port
			rospy.loginfo("serial port Closed.")

	except serial.SerialException as ex:
		rospy.logerr( "SerialException port open error({0}): {1}".format(ex.errno, ex.strerror))
