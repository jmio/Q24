# coding: utf-8

import ui
import sys
import telnetlib
import time
import os
#import subprocess
from ftplib import FTP
import ui
import mcprotocol

def addbutton_touch(sender) :
	memoryview.data_source.items.append(addtext.text)
	memoryview.reload_data()

def updatebutton_touch(sender) :
  port = int(porttext.text)
  host = hosttext.text
  contentview.data_source.items = []
  for i in memoryview.data_source.items :
    addr = int(i)
    r = mcprotocol.mcpRead(host,port,addr,1)
    contentview.data_source.items.append({'accessory_type': u'none', 'title': str(r[0])} )
    
v = ui.load_view('MemoryEdit')
porttext= v["porttext"]
hosttext = v["hosttext"]
memoryview = v["memoryview"]
memoryview.data_source = ui.ListDataSource(items=[])
contentview = v["contentview"]
addtext=v['addtext']

v.present(orientations=['portrait','landscape'])


