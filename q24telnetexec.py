#
# Q24 Util. for Pythonista
# 2014/12/23 : First Release
#
##############################################################################################################

import sys
import telnetlib
import time
import os
#import subprocess
from ftplib import FTP

##################################################################
#ftp = FTP("192.168.1.150","target","password","",3)
#ftp.retrlines('LIST')
#ftp.retrbinary('RETR README', open('README', 'wb').write)
#ftp.abort()
#ftp.quit()

HOST = "192.168.1.172"
user = "target"
password = "password"
EXECCOMMAND = "ls"

tn = telnetlib.Telnet(HOST)
v = tn.read_until("login: ",1)
tn.write(user + "\r\n")
time.sleep(0.3)
if password:
	v = tn.read_until("Password: ",1)
	tn.write(password + "\r\n")
	time.sleep(0.3)

print "Connect"
v = tn.read_until(">",1)
print ""
print "Execute"
tn.write(EXECCOMMAND+"\r\n")
r = tn.read_until("->",20)
tn.close()
a = [i.strip("\n") for i in r.split("\r")[1:]]
print "-- Result from "+HOST+" --"
for i in a:
	print i
print "-- END --"
