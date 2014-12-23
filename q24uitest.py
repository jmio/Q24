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

@ui.in_background
def connect(execcmd):
	tn = telnetlib.Telnet(HOST)
	v = tn.read_until("login: ",1)
	tn.write(user + "\r\n")
	time.sleep(0.3)
	if password:
		v = tn.read_until("Password: ",1)
		tn.write(password + "\r\n")
		time.sleep(0.3)
	v = tn.read_until(">",1)
	tn.write(execcmd.encode('utf-8'))
	tn.write('\r\n')
	r = tn.read_until("->",20)
	tn.close()
	a = [i.strip("\n") for i in r.split("\r")[1:]]
	for i in a:
		printtext(i)
	cmd.text=''
	cmd.begin_editing()

def printtext(s):
	textview.begin_editing()
	l = len(textview.text)
	if not(l==0):
		textview.selected_range=(l-1,l-1)
	textview.replace_range((l,l),s+'\n')
	l = len(textview.text)
	textview.selected_range=(l-1,l-1)

def button_pushed(sender):
	#for i in xrange(30):
	#printtext(cmd.text)
	connect(cmd.text)
	#cmd.text=''
	#cmd.begin_editing()

v = ui.load_view('q24uitest')
textview = v['textview1']
cmd = v['commandtext']
v.present('popover')

