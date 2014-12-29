##coding: utf-8

import socket
import sys

def sendandrecv(host,port,data,minlen=1):
	try:
		sock = socket.create_connection((host, port),100)
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
		print 'received %d bytes' % received
	finally:
		print 'closing socket'
		sock.close()
	return data

def mcpRead(host,port,addr,len,datatype="D") :
	#.             0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,
	cmdBytes = [0x50,0x00,0x00,0xFF,0xFF,0x03,0x00,0x0C,0x00,0x10,0x00,0x01,0x04,0x00,0x00]
	# Address
	cmdBytes.append((addr & 0x0000FF) >> 0)
	cmdBytes.append((addr & 0x00FF00) >> 8)
	cmdBytes.append((addr & 0xFF0000) >> 16)
	# DataType 0xA8="D"
	if (datatype == "D") :
		cmdBytes.append(0xA8)
	else:
		cmdBytes.append(0xA8)
	# Length
	cmdBytes.append((len & 0x0000FF) >> 0)
	cmdBytes.append((len & 0x00FF00) >> 8)
	#
	d = sendandrecv(host,port,cmdBytes,minlen=1)
	#      0,1,2,3,4,5,6,7.8.9.A .B.C.
	#res="D00000FFFF0300xxxx0000/vvvv/...";(xxxx=data_len+2,vvvv=data)
	len = int(d[7]) + int(d[8]*0x100) - 2
	if (datatype == "D") :
		wordlen = 2
	else:
		wordlen = 1
	print "datacount=",len / wordlen
	result = []
	for q in xrange(0x0B,0x0B+len,wordlen) :
		databyte = 0
		factor = 1
		for p in xrange(wordlen) :
			print q+p,"*",factor
			databyte += int(d[q+p] * factor)
			factor *= 0x100
		result.append(databyte)
		print "*"
	return result

res = mcpRead("192.168.1.171",5010,1000,4)
print res
