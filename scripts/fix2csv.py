#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy

import roslib.packages
import os

from datetime import datetime
from sensor_msgs.msg import NavSatFix

seq=0
default_stamp_delay = 1.0

homeDir = roslib.packages.get_pkg_dir('f9p_ichimill')
if homeDir is None or len(homeDir) == 0:
	homeDir = os.environ['HOME']

fname = homeDir + "/fix{0:%Y%m%d_%H%M}.csv".format(datetime.now())
f = open( fname, "w" )

old_time = rospy.Time.from_sec(0.0)

def cb_fix(dt):
	global seq
	global f
	global old_time
	global stamp_delay

	# 時間経過またはステータス変化 
	if ( (dt.header.stamp - old_time).to_sec() > stamp_delay ):
		seq = seq + 1
		logtime = datetime.fromtimestamp(dt.header.stamp.to_time())
		linestr = str(seq) + "," + str(dt.latitude) + "," + str(dt.longitude) + ",status=" + str(dt.status.status) + ",service=" + str(dt.status.service) + ",stamp=" + str(logtime) + "\n"
		f.write( linestr )
		old_time = dt.header.stamp

rospy.init_node("fix2csv")

stamp_delay = rospy.get_param('~delay', default_stamp_delay)

subJyr = rospy.Subscriber('/fix', NavSatFix, cb_fix)

rospy.loginfo ("Start GPS /fix topic to csv file")
rospy.loginfo ("  delay = %5.2fsec", stamp_delay)

try:
	while not rospy.is_shutdown():
		rospy.spin()
finally:
	f.close()
	rospy.loginfo ("close " + fname)

