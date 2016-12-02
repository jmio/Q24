##coding: utf-8

import socket
import sys

DEVICECODE = {
	'SM':(0x91,2), 
	'SD':(0xA9,2), 
	'D' :(0xA8,2), 
	'W' :(0xB4,2), 
	'M' :(0x90,2), 
	'X' :(0x9C,2),
	'Y' :(0x9D,2),
	'L' :(0x92,2),
	'F' :(0x93,2),
	'V' :(0x94,2),
	'B' :(0xA0,2),
	'TS':(0xC1,2),
	'TC':(0xC0,2),
	'TN':(0xC2,2),
	'SS':(0xC7,2),
	'SC':(0xC6,2),
	'SN':(0xC8,2),
	}

def sendandrecv(host,port,data,minlen=1):
	try:
		sock = socket.create_connection((host, port),1)
	except:
		print "Can't create socket."
		return None 
	try:
		# Send 
		sock.sendall(str(bytearray(data)))
		received = 0
		while received < minlen:
			data = bytearray(sock.recv(4096))
			received += len(data)
	finally:
		sock.close()
	return data

def mcpWriteBit(host,port,addr,data,datatype="M") :
	#.             0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,
	cmdBytes = [0x50,0x00,0x00,0xFF,0xFF,0x03,0x00,0x0C,0x00,0x10,0x00,0x02,0x14,0x01,0x00]
	# Bit Access Points
	cmdBytes.append(0x01)
	# Address
	cmdBytes.append((addr & 0x0000FF) >> 0)
	cmdBytes.append((addr & 0x00FF00) >> 8)
	cmdBytes.append((addr & 0xFF0000) >> 16)
	# DataType 0xA8="D"
	wordlen = DEVICECODE[datatype][1]
	cmdBytes.append(DEVICECODE[datatype][0])
	# Set/Reset
	cmdBytes.append(data)
	#
	d = sendandrecv(host,port,cmdBytes,minlen=1)
	if (d and (len(d) < 11)) :
		return None
	return data


def mcpWrite(host,port,addr,data,datatype="D") :
	datalen = (len(data) * 2) + 0x0C
	#.             0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,
	cmdBytes = [0x50,0x00,0x00,0xFF,0xFF,0x03,0x00,0x0C,0x00,0x10,0x00,0x01,0x14,0x00,0x00]
	# Set Data Length
	cmdBytes[7] = (datalen & 0x00FF) >> 0
	cmdBytes[8] = (datalen & 0xFF00) >> 8
	# Address
	cmdBytes.append((addr & 0x0000FF) >> 0)
	cmdBytes.append((addr & 0x00FF00) >> 8)
	cmdBytes.append((addr & 0xFF0000) >> 16)
	# DataType 0xA8="D"
	wordlen = DEVICECODE[datatype][1]
	cmdBytes.append(DEVICECODE[datatype][0])
	# Length
	cmdBytes.append((len(data) & 0x0000FF) >> 0)
	cmdBytes.append((len(data) & 0x00FF00) >> 8)
	for i in data :
		mask = 0xFF
		for j in xrange(wordlen) :
			cmdBytes.append(i & mask)
			i = i >> 8
	#
	d = sendandrecv(host,port,cmdBytes,minlen=1)
	if (d and (len(d) < 11)) :
		return None
	return len(data)

def mcpRead(host,port,addr,datalen,datatype="D") :
	#.             0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,
	cmdBytes = [0x50,0x00,0x00,0xFF,0xFF,0x03,0x00,0x0C,0x00,0x10,0x00,0x01,0x04,0x00,0x00]
	# Address
	cmdBytes.append((addr & 0x0000FF) >> 0)
	cmdBytes.append((addr & 0x00FF00) >> 8)
	cmdBytes.append((addr & 0xFF0000) >> 16)
	# DataType 0xA8="D"
	wordlen = DEVICECODE[datatype][1]
	cmdBytes.append(DEVICECODE[datatype][0])
	# DataLength
	cmdBytes.append((datalen & 0x0000FF) >> 0)
	cmdBytes.append((datalen & 0x00FF00) >> 8)
	#
	d = sendandrecv(host,port,cmdBytes,minlen=1)
	#      0,1,2,3,4,5,6,7.8.9.A .B.C.
	#res="D00000FFFF0300xxxx0000/vvvv/...";(xxxx=data_len+2,vvvv=data)
	if d == None : return None 
	datalen = int(d[7]) + int(d[8]*0x100) - 2
	result = []
	for q in xrange(0x0B,0x0B+datalen,wordlen) :
		databyte = 0
		factor = 1
		for p in xrange(wordlen) :
			databyte += int(d[q+p] * factor)
			factor *= 0x100
		result.append(databyte)
	return result

if __name__=='__main__':
	mcpWrite("192.168.1.171",5010,1000,[41,2,3,5])
	res = mcpRead("192.168.1.171",5010,1000,4)
	print res
