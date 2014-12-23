# coding: utf-8
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
import ui

HOST = "192.168.1.172"
user = "target"
password = "password"
#EXECCOMMAND = "ls"

def connect(execcmd):
	tn = telnetlib.Telnet(HOST)
	v = tn.read_until("login: ",1)
	tn.write(user + "\r\n")
	time.sleep(0.3)
	if password:
		v = tn.read_until("Password: ",1)
		tn.write(password + "\r\n")
		time.sleep(0.3)
	printtext("Connect")
	v = tn.read_until(">",1)
	printtext("Execute")
	print execcmd
	tn.write(execcmd.encode('utf-8'))
	tn.write('\r\n')
	r = tn.read_until("->",20)
	tn.close()
	a = [i.strip("\n") for i in r.split("\r")[1:]]
	printtext( "-- Result from "+HOST+" --")
	for i in a:
		printtext(i)
	printtext("-- END --")

def printtext(s):
	l = len(textview.text)
	textview.begin_editing()
	textview.replace_range((l,l),s+'\n')
	l = len(textview.text)
	textview.selected_range=(l-1,l-1)
	cmd.begin_editing()

def button_pushed(sender):
	#printtext(cmd.text)
	connect(cmd.text)
	cmd.text=''
	cmd.begin_editing()

v = ui.load_view('q24uitest')
textview = v['textview1']
cmd = v['commandtext']
if ui.get_screen_size()[1] >= 768:
	# iPad
	v.present('popover')
else:
	# iPhone
	v.present(orientations=['portrait'])

