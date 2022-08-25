#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Copyright 2022 Shinji Kobayashi, JF1KKM
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

# This is a Python program for receiving ADIF sent by multicast from JTDX.

# Call and grid, all received ADIF data excluding grid are passed to
# the upper layer.


from __future__ import print_function
import socket
from contextlib import closing
import netifaces

import re
import adif


multicast_group = '224.0.0.1' # same multicast address as JTDX to send
PORT = 2333 # same as JTDX destination port number

local_address = '127.0.0.1'
MAX_BUFFER = 4096

#def main():
def rcv_adif():

	with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('', PORT))
		sock.setsockopt(socket.IPPROTO_IP,
		socket.IP_ADD_MEMBERSHIP,
		socket.inet_aton(multicast_group) + socket.inet_aton(local_address))
        
		temp = sock.recv(MAX_BUFFER)
		txt = str(temp)
		txt = txt.replace("b'",'')
		txt = txt.replace("<EOR>'",'<EOR>')
		print("input ADIF:")
		print(txt)

		qsos = adif.read_from_string(txt)
		print("QSOs:\n {}\n".format(qsos))

		oqso = qsos[0]

		sock.close()

		if 'GRIDSQUARE' in oqso.keys():
			print("GRID:", oqso['GRIDSQUARE'])
			grid = oqso['GRIDSQUARE']
			txt = re.sub("<GRIDSQUARE:.>.{0,6}¥s<", "<", txt)
			print("rcvout:\n", txt)
		else:
			print("NO GRID:")
			grid = ""

	return [oqso['CALL'], grid, txt]

#if __name__ == '__main__':
#	main()


