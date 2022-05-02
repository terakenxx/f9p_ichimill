#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy

import time
import base64
import socket

#from nmea_msgs.msg import Sentence
from std_msgs.msg import String


# init ---------------------------------
rospy.init_node('ntripcaster_connect')

pub = rospy.Publisher('/caster/rtcm_data', String, queue_size=10)
tcpip = None

debug = rospy.get_param('~debug', False)

username = rospy.get_param('~username', '')
password = rospy.get_param('~password', 'BETATEST')
port = rospy.get_param('~port', 2101)

host_url = rospy.get_param('~host', "rtk2go.com")
mountpoint = rospy.get_param('~mountpoint', "MIE_UNIV")

CLIENT_ARGENT = "ros_ntripcaster_connect_kt"

BUF_SIZE = 4096

# Main
if __name__ == '__main__':
	idpwd = base64.b64encode("{}:{}".format(username, password).encode('ascii')).decode('ascii')

	header =\
		"GET /" + mountpoint +" HTTP/1.1\r\n" + \
		"User-Agent: " + CLIENT_ARGENT + "\r\n" + \
		"Authorization: Basic {}\r\n".format(idpwd) + \
		"\r\n"

	# rospy.loginfo(header)
	r = rospy.Rate( 1.0 ) # 1Hz

	try:
		while not rospy.is_shutdown():
			tcpip = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			rospy.loginfo("NTRIP Caster connecting...")
			tcpip.connect((host_url,int(port)))
			rospy.loginfo("ok")

			rospy.loginfo("Header sending...")
			tcpip.send(header.encode('ascii'))

			data = tcpip.recv(BUF_SIZE).decode('ascii')

			if len(data) <= 0:
				rospy.loginfo("Header Response Fail...")
				rospy.loginfo( "NTRIP Caster retry Connecting...")
				continue
			else:
				print(data)
				response_header = data.strip()
				if( response_header == "ICY 200 OK" or \
					response_header == "HTTP/1.1 200 OK" ):
					rospy.loginfo("Header Response ok")
					pass
				else:
					rospy.logerr("NTRIP Caster ResponseError!! : " + data)
					exit(-1)

			rtk_datas = b''
			while not rospy.is_shutdown():
				try:
					#tcpip.send(sendData)
					sendTime = rospy.Time.now()
					#time.sleep(0.25) # 250 msec

					ntrip_response = tcpip.recv(BUF_SIZE)

					rtk_datas += ntrip_response
					if len(ntrip_response) >= BUF_SIZE:
						continue

					if len(rtk_datas) <= 0:
						# 切断検知
						rospy.logwarn( "NTRIP Caster Disconnect!")
						rospy.loginfo( "NTRIP Caster retry Connecting...")
						break

					# 応答遅延計測
					responceDelay = (rospy.Time.now() - sendTime)
					if  responceDelay > rospy.Duration(3.0):
						rospy.logwarn( "NTRIP Caster Responce Delay 3.0Sec Over! : " + str(responceDelay) + "nsec / host:" + host_url )

					if debug:
						rospy.loginfo( "NTRIP data receive:" + str(len(rtk_datas)) )

					pub.publish(rtk_datas)
					rtk_datas = b''

				except socket.timeout as ex:
					rospy.logwarn( "NTRIP Caster  timeout")
				except Exception as ex:
					rospy.logerr( "exception error : " + ex)
					tcpip.close()
					break

				r.sleep()

	except socket.error as ex:
		rospy.logerr( "NTRIP Caster connect error({0}): {1}".format(ex.errno, ex.strerror))
	except Exception as ex:
		rospy.logerr( "exception error : " + ex)
	except rospy.ROSInterruptException:
		pass
	finally:
		tcpip.close() # close tcpip
		rospy.loginfo("NTRIP Caster disconnect")


