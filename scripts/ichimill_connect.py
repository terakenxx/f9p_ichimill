#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy

import time
import base64
import socket

from nmea_msgs.msg import Sentence
from std_msgs.msg import String


# init ---------------------------------
rospy.init_node('ichimill_connect')

pub = rospy.Publisher('/softbank/rtcm_data', String, queue_size=10)
tcpip = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

debug = rospy.get_param('~debug', False)

def cb_GGA(data):
	global tcpip
	global pub
	global debug
	sendData = data.sentence

	if debug:
		print("Send  :" + sendData)

	tcpip.send(sendData)
	time.sleep(0.25) # 250 msec

	rtk_datas = tcpip.recv(4096)
	if debug:
		print( "Ntrip receive:" + str(len(rtk_datas)) )

	pub.publish(rtk_datas)

# Main
if __name__ == '__main__':
	username = rospy.get_param('~username', '')
	password = rospy.get_param('~password', '')
	port = rospy.get_param('~port', 2101)

	host_url = rospy.get_param('~host', "ntrip.ales-corp.co.jp")
	mountpoint = rospy.get_param('~mountpoint', "32M7NHS")

	pwd = base64.b64encode("{}:{}".format(username, password).encode('ascii')).decode('ascii')

	header =\
		"GET /" + mountpoint +" HTTP/1.1\r\n" +\
		"Authorization: Basic {}\r\n\r\n".format(pwd)


	try:
		rospy.loginfo("ntrip caster connecting...")
		tcpip.connect((host_url,int(port)))
		rospy.loginfo("ok")

		rospy.loginfo("Header sending...")
		tcpip.send(header.encode('ascii'))

		data = tcpip.recv(1024).decode('ascii')
		print(data)
		if( data.strip() == "ICY 200 OK" ):
			rospy.Subscriber("/nmea_gga", Sentence, cb_GGA)
			rospy.spin()
		else:
			rospy.logerr("ServerResponseError!! : " + data)

	except rospy.ROSInterruptException:
		pass
	finally:
		tcpip.close() # close tcpip


