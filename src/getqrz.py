#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Copyright 2022 Shinji (kobie) Kobayashi, JF1KKM
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# This is a Python program that recreates QSO ADIF data by adding
# Name, grid, QHT, state and country of QRZ.com to QSO ADIF data sent
# by multicast from JTDX.
#
# The log file output by this program is If you specify it
# in the JTAlert log file on the decoder setting tab of JT_Linker,
# the information of QRZ.com will also be reflected in JT_Linker.

#{
#  "name": "getqrz",
#  "description": "Recreates QSO ADIF data with QRZ.com data base.",
#  "author": "Shinji (kobie) Kobayashi <jf1kkm@gmail.com>",
#  "license": "Apache-2.0",
#  "repository": "https://github.com/jf1kkm/getqrz",
#  "dependencies": {
#    "request": "python>=3.8"
#  }   
#}

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import socket
import re
import rcv_mc
import signal
import sys
import os.path

# If set to "1", the file will not be written
DEBUG_seq = 0

# QRZ.com username password
username = "username"
pw = "password"

# output ADIF file setting
filename = "/full_path/log.adi"

# same as the QTH size of hamlog
size_qth = 32

adi_init = """<BAND:3>15m <STATION_CALLSIGN:6>XXXXXX <MY_GRIDSQUARE:6>XXXXxx <CALL:6>XXXXXX <FREQ:9>00.000000 <MODE:3>XXX <QSO_DATE:8>00000000 <TIME_ON:6>000000 <QSO_DATE_OFF:8>00000000 <TIME_OFF:6>000000 <RST_SENT:3>-00 <RST_RCVD:3>-00 <TX_PWR:3>00w <NAME:7>ABCDEFG <GRIDSQUARE:6>XXXXyy <COUNTRY:5>XXXXX <QTH:6>XXXxxx <EOR>
"""

adifheader = """<ADIF_VER:5>2.2.7
<ProgramID:6>getqrz
<ProgramVersion:3>0.1
<APP_getqrz_Created:23>2022/08/12 01:02:59 UTC
<EOH>
"""

args = sys.argv

def main():

	rcvadif = rcv_mc.rcv_adif()
	callsign = rcvadif[0]
	gridadif = rcvadif[1]
	rpladif = rcvadif[2].replace("<EOR>",'')

	url = 'https://xmldata.qrz.com/xml/current/?username=' + username + ';password=' + pw + ';agent=q5.0'
#	print(url)

	req = urllib.request.Request(url)

	with urllib.request.urlopen(req) as response:
		xmls = response.read()

	root = ET.fromstring(xmls)

	skey = ""
	for child in root.iter():
#		print(child.tag, child.attrib, child.text)
		if child.tag == '{http://xmldata.qrz.com}Key':
			skey = child.text
#			print(skey)


	url = 'https://xmldata.qrz.com/xml/current/?s=' + skey + ';callsign=' + callsign
#	print(url)

	req = urllib.request.Request(url)
	with urllib.request.urlopen(req) as response:
		xmls = response.read()

	root = ET.fromstring(xmls)
	print("qrz:\n", xmls)

	call = ""
	fname = ""
	name = ""
	addr2 = ""
	qth = ""
	grid = ""
	state = ""
	country =""
	for child in root.iter():
#		print(child.tag, child.attrib, child.text)
		if child.tag == '{http://xmldata.qrz.com}call':
			call = child.text
		if child.tag == '{http://xmldata.qrz.com}fname':
			fname = child.text
		if child.tag == '{http://xmldata.qrz.com}name':
			name = child.text
		if child.tag == '{http://xmldata.qrz.com}addr2':
			addr2 = child.text
		if child.tag == '{http://xmldata.qrz.com}qth':
			qth = child.text
		if child.tag == '{http://xmldata.qrz.com}grid':
			grid = child.text
		if child.tag == '{http://xmldata.qrz.com}state':
			state = child.text
		if child.tag == '{http://xmldata.qrz.com}country':
			country = child.text

	#generate QTH
	lst_qth = re.split('[ ]',addr2)
	cnt_qth = 0
	len_qth = len(state) + len(country)

	for lq in reversed(lst_qth):
		print("lq:", lq)
		if re.match('(.*[0-9]{4}+.*|.*:+.*)', lq):
			print("addr2 include number:", re.match('.*[0-9]{4}.*|.*:+.*', lq))
			print("addr2:", lq)
		else:
			if (len(qth) + len(lq)) <= size_qth:
				if cnt_qth:
					qth = lq + ' ' + qth
				else:
					qth = lq
			cnt_qth = cnt_qth + 1
		if cnt_qth > 1:
			break

	#generate QSO ADIF
	dat = adifheader
	dat = dat + rpladif
	if fname != "" and name != "":
		dat = dat + "<NAME:" + str((len(fname)+len(name)+1)) + ">"
		dat = dat + fname + " " + name + " "
	if gridadif != "":
		dat = dat + "<GRIDSQUARE:" + str(len(gridadif)) + ">" + gridadif + ' '
	elif grid != "":
		dat = dat + "<GRIDSQUARE:" + str(len(grid)) + ">" + grid + ' '
	if state != "":
		dat = dat + "<STATE:" + str(len(state)) + ">" + state + ' '
		qth = qth + ' ' + state
	if country != "":
		dat = dat + "<COUNTRY:" + str(len(country)) + ">" + country + ' '
		qth = qth + ' ' + country
	if qth != "":
		dat = dat + "<QTH:" + str(len(qth)) + ">" + qth + ' '
		print("qth:", qth)
	dat = dat + "<EOR>\n"
	if DEBUG_seq != 1:
		fd = open(filename, 'w')
		fd.write(dat)
		fd.close()
	print(dat)

	return

def handler(signal, frame):
	print('\nexit getqrz')
	sys.exit(0)

signal.signal(signal.SIGINT, handler)

if __name__ == '__main__':

	# initialize log file
	if not os.path.isfile(filename):
		print("create log file")
		fd = open(filename, 'w')
		fd.write(adifheader)
		fd.write(adi_init)
		fd.close()

	while(True):
		main()

