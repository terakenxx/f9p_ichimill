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

username = rospy.get_param('~username', '')
password = rospy.get_param('~password', '')
port = rospy.get_param('~port', 2101)

host_url = rospy.get_param('~host', "ntrip.ales-corp.co.jp")
mountpoint = rospy.get_param('~mountpoint', "32M7NHS")

mutex_server = False

def cb_GGA(data):
	global tcpip
	global pub
	global debug
	global host_url
	global mutex_server
	sendData = data.sentence

	if( sendData.split(',').count('') > 1 ):
		# 必要なデータが欠けている
		rospy.logwarn("Missing the necessary elements GGA sentence:" + sendData)
		return

	if debug:
		rospy.loginfo("Send ichimill server :" + sendData)

	if mutex_server:
		# サーバ待ち状態なのでリクエストしない
		return

	mutex_server = True
	try:
		tcpip.send(sendData)
		sendTime = rospy.Time.now()

		time.sleep(0.25) # 250 msec

		rtk_datas = tcpip.recv(4096)
		if debug:
			rospy.loginfo( "NTRIP data receive:" + str(len(rtk_datas)) )

		responceDelay = (rospy.Time.now() - sendTime)
		if  responceDelay > rospy.Duration(3.0):
			rospy.logwarn( "NTRIP Caster Responce　Delay 3.0Sec Over! : " + str(responceDelay) + "nsec / host:" + host_url )

		pub.publish(rtk_datas)

	except socket.timeout as ex:
		rospy.logwarn( "NTRIP Caster  timeout")
	except Exception as ex:
		rospy.logerr( "exception error : " + ex)
	finally:
		mutex_server = False


# Main
if __name__ == '__main__':
	pwd = base64.b64encode("{}:{}".format(username, password).encode('ascii')).decode('ascii')

	header =\
		"GET /" + mountpoint +" HTTP/1.1\r\n" +\
		"Authorization: Basic {}\r\n\r\n".format(pwd)


	try:
		rospy.loginfo("NTRIP Caster connecting...")
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
			rospy.logerr("Caster ResponseError!! : " + data)

	except socket.error as ex:
		rospy.logerr( "NTRIP Caster connect error({0}): {1}".format(ex.errno, ex.strerror))
	except Exception as ex:
		rospy.logerr( "exception error : " + ex)
	except rospy.ROSInterruptException:
		pass
	finally:
		tcpip.close() # close tcpip
		rospy.loginfo("NTRIP Caster disconnect")


