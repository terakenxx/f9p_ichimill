#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy

import base64
import socket
import serial

from nmea_msgs.msg import Sentence
from std_msgs.msg import String


def calcultateCheckSum(stringToCheck):
	xsum_calc = 0
	for char in stringToCheck:
		xsum_calc = xsum_calc ^ ord(char)
	return "%02X" % xsum_calc


# init ---------------------------------
rospy.init_node('f9p_driver')

serial_port = rospy.get_param('~port', '/dev/ttyACM0')
serial_baud = rospy.get_param('~baud', 230400)

debug = rospy.get_param('~debug', False)

seqGGA = 0
pubGGA = rospy.Publisher('nmea_gga', Sentence, queue_size=60)
seqNmeaSeq = 0
pubNmea = rospy.Publisher('nmea_sentence', Sentence, queue_size=60)

#print("Header sending... \n")
rtcmData = ""

def cb_RtcmData(data):
	global rtcmData
	rtcmData = data.data


# Main
if __name__ == '__main__':

	rospy.Subscriber("/softbank/rtcm_data", String, cb_RtcmData)
	try:
		rospy.loginfo("serial port Open...")
		GPS = serial.Serial(port=serial_port, baudrate=serial_baud, timeout=2)

		rospy.loginfo("Ok")
		gps_str_nmea = []

		try:
			while not rospy.is_shutdown():
				gps_datas = GPS.readline().split()
				for gps_data in gps_datas:
					gps_str = ""
					try:
						gps_str = gps_data.decode('ascii')
						if debug:
							rospy.loginfo(gps_str)
					except UnicodeError:
						pass
					
					# GGA Sentence publish
					if "GGA" in gps_str:
						if "$GNGGA" in gps_str:
							ggaString = gps_str.replace('$GNGGA', 'GPGGA')
							ggaString = ggaString[:-3]
							checksum = calcultateCheckSum(ggaString)
							sendData = bytes(("$%s*%s\r\n" % (ggaString, checksum)).encode('ascii'))
						else:
							sendData = gps_str

						ggaSentence = Sentence()
						ggaSentence.header.stamp = rospy.get_rostime()
						ggaSentence.header.frame_id = 'gps'
						ggaSentence.header.seq = seqGGA
						ggaSentence.sentence = sendData
						pubGGA.publish(ggaSentence)
						seqGGA = seqGGA + 1

						ggaSentence = Sentence()
						ggaSentence.header.stamp = rospy.get_rostime()
						ggaSentence.header.frame_id = 'gps'
						ggaSentence.header.seq = seqNmeaSeq
						ggaSentence.sentence = gps_str
						pubNmea.publish(ggaSentence)
						seqNmeaSeq = seqNmeaSeq + 1
				
				# nstrip casterからのデータを受信していれば、レシーバーに送信 
				if len(rtcmData) > 0:
					GPS.write(rtcmData)
					rtcmData = ""
				
				#rospy.Rate(10).sleep()
				rospy.sleep(0)

		except serial.SerialException as ex:
			rospy.logerr( "SerialException error({0}): {1}".format(ex.errno, ex.strerror))
		except rospy.ROSInterruptException:
			pass
		finally:
			GPS.close()  # Close GPS serial port
			rospy.loginfo("serial port Closed.")

	except serial.SerialException as ex:
		rospy.logerr( "SerialException port open error({0}): {1}".format(ex.errno, ex.strerror))
