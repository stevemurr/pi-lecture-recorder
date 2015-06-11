import lirc
import os
from time import sleep

sockid = lirc.init("myprogram")
flip = False
while(True):
	lirc.nextcode()
	sleep(1)
	if(flip == False):
		os.system('touch hooks/start_record')
		print "Working"
		flip = True
	else:
		os.system('touch hooks/stop_record')
		print "Stopping"
		flip = False
