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

def mcpRead(host,port,addr,len) :
	#.             0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,
	cmdBytes = [0x50,0x00,0x00,0xFF,0xFF,0x03,0x00,0x0C,0x00,0x10,0x00,0x01,0x04,0x00,0x00]
	# Address
	cmdBytes.append((addr & 0x0000FF) >> 0)
	cmdBytes.append((addr & 0x00FF00) >> 8)
	cmdBytes.append((addr & 0xFF0000) >> 16)
	# DataType 0xA8="D"
	cmdBytes.append(0xA8)
	# Length
	cmdBytes.append((len & 0x0000FF) >> 0)
	cmdBytes.append((len & 0x00FF00) >> 8)
	#
	d = sendandrecv(host,port,cmdBytes,minlen=1)
	return d

res = bytearray(mcpRead("192.168.1.171",5010,1000,1))
for i,j in enumerate(res):
	print i,"=","%02X"%int(j)
