# sinusoidal.py
#
# 2016-09-08 LJS
#
# Tells a power supply to set voltages that vary sinusoidally
#
# UPDATE 2016-09-09: Now takes a resistance R to control the
# current.  This is to correct for the current maxing out when
# no current is chosen.  LJS

<<<<<<< Updated upstream
import anl_fridge_control.powersupply as PS
import time
from math import *

def sinuvolt(driverfile, A, tint, tf, R, freq=0.01, y=0, t0=0):
	power=PS.PowerSupply(driverfile)
	if t0!=0:
		time.sleep(t0)
	t=0
	while t<tf:
		v=-0.5*A*cos(2*pi*freq*t)+(0.5*A)+y
		name.set_vi(v,v/R)
		time.sleep(tint)
		t=t+tint
	name.set_vi(0,0)
=======
import anl_fridge_control.control.powersupply as PS
from math import cos
import time
import pickle
import subprocess
import datetime
import pydfmux
from math import pi

time_savefile = '/home/spt3g/output/20170607/al_transition_Bvert_far_time.pkl'
savefile_0135 = '/home/spt3g/output/20170607/al_transition_Bvert_far_0135.nc'
savefile_0137 = '/home/spt3g/output/20170607/al_transition_Bvert_far_0137.nc'

ledgerman_path = '/home/spt3g/spt3g_software/dfmux/bin/ledgerman.py'

hwm_0135 = '/home/spt3g/hardware_maps/hwm_anl_20170402_w169/hwm_nb.yaml'
hwm_0137 = '/home/spt3g/hardware_maps/hwm_anl_20170402_w169/hwm_al.yaml'

def sinuvolt(driverfile, A, tint, tf, R=3.00, freq=0.01, y=0, t0=0):
	try:
		power=PS.PowerSupply(driverfile)
		t=t0
		while t<tf:
			v=-0.5*A*cos(2*pi*freq*t)+(0.5*A)+y
			power.set_vi(v,v/R)
			print v
			time.sleep(tint)
			t=t+tint
		power.set_vi(0,0)
	except KeyboardInterrupt:
		power.set_vi(0,0)
		

def helmholtz_test(driverfile, A, tint, tf):
	proc_ledgerman_0135 = subprocess.Popen(['python', ledgerman_path, hwm_0135, savefile_0135, '-s'])
	proc_ledgerman_0137 = subprocess.Popen(['python', ledgerman_path, hwm_0137, savefile_0137, '-s'])
	starttime = time.time()
	sinuvolt(driverfile, A, tint, tf)
	endtime = time.time()
	proc_ledgerman_0135.terminate()
	proc_ledgerman_0137.terminate()
	f=open(time_savefile, 'w')
	pickle.dump({'starttime':starttime, 'endtime':endtime}, f)
	f.close()
>>>>>>> Stashed changes
