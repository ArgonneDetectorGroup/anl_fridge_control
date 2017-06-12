# measure_RofT.py
#
# A script for automating R(T) measurements.
#
# Adam Anderson
# adama@fnal.gov
# 27 April 2016
#
# Modified for ANL by Lauren Saunders
# ljsaunders@uchicago.edu
# 12 June 2017


import anl_fridge_control.serial_connections as sc
import he10_fridge_control.control.gettemp as gt
import pydfmux
import pydfmux.spt3g.northern_tuning_script as nts
import time
import cPickle as pickle
import subprocess

'''
This is a Python script that takes the data necessary for
resistance vs. temperature measurements. It heats the UC
stage, overbiases bolometers, and takes a downward sweep
and an upward sweep.

Before beginning, check the settings for logfile, hwm_file,
and the data and time paths. If you do not check these, they
may be incorrect, and may either prevent the script from
properly completing, or may accidentally write over data that
you have previously taken.

Definitions:
------------
logfile: the file outputted by the temperature logger

hwm_file: the hardware map you are using

ledgerman_path: the path to ledgerman.py. Do not change this.

R_down_path: the output file for the timestream data on the
             downward sweep (.nc)

down_times: the output file to store time data for the downward
            sweep for analysis (.pkl)

R_up_path: the output file for the timestream data on the
           upward sweep (.nc)

up_times: the output file to store time data for the upward sweep
          for analysis (.pkl)

wafer_high_temp: the high temperature for heating the stage to,
                 usually 0.650

wafer_low_temp: the low temperature for cooling the stage to,
                usually 0.400
'''

# user params
logfile = '/home/spt3g/he10_logs/log03302017b_read.h5'
hwm_file = '/home/spt3g/hardware_maps/hwm_anl_20170306_W169_and_Rboards/hwm.yaml'
ledgerman_path = '/home/spt3g/spt3g_software/dfmux/bin/ledgerman.py'
R_down_path = '/home/spt3g/ledgerman_output/20161208/down1.nc'
down_times = '/home/spt3g/ledgerman_output/20161208/down_times.pkl'
R_up_path = '/home/spt3g/ledgerman_output/20161208/up1.nc'
up_times = '/home/spt3g/ledgerman_output/20161208/up_times.pkl'

wafer_high_temp = 0.650
wafer_low_temp = 0.400
K_per_sec = 1e-4
update_time = 10

#######################################################################
print 'Starting R(T) script.'

# unlatch the switches
print('Turning off switches...')
sc.He3UCs.set_voltage(0.0)
sc.He3ICs.set_voltage(0.0)

# wait for switches to cool
while float(gt.gettemp(logfile, 'He3 UC Switch'))>2.00:
	time.sleep(10)
while float(gt.gettemp(logfile, 'He3 IC Switch'))>2.00:
	time.sleep(10)

# heat the fridge to the high temperature
print('Heating up fridge...')
sc.He3UCp.set_voltage(2.0)
sc.He3ICp.set_voltage(2.0)
time.sleep(3*60)
sc.ChaseLS.set_PID_temp(1, 0.500)
time.sleep(1)
sc.ChaseLS.set_heater_range(2)

time.sleep(1)

while float(gt.gettemp(logfile, 'UC Stage')) < 0.500:
	print gt.gettemp(logfile, 'UC Stage')
	time.sleep(5)

sc.He3ICp.set_voltage(0.50)
sc.He3UCp.set_voltage(1.00)
sc.ChaseLS.set_PID_temp(1, wafer_high_temp)
time.sleep(5)

while float(gt.gettemp(logfile, 'UC Stage')) < wafer_high_temp:
	print gt.gettemp(logfile, 'UC Stage')
	time.sleep(5)

time.sleep(600)

# zero combs
nts.run_do_zero_combs()
# overbias bolos
nts.run_overbias_bolos()

time.sleep(60)

# start ledgerman
proc_ledgerman = subprocess.Popen(['python', ledgerman_path, hwm_file, R_down_path])
# record start time
down_start = time.time()

# start letting temperature drop
print('Starting ramp down...')
current_temp = wafer_high_temp
sc.ChaseLS.set_heater_range(2)
time.sleep(1)
sc.ChaseLS.set_PID_temp(1,current_temp)
time.sleep(2)

while current_temp > wafer_low_temp:
	time.sleep(update_time)
	current_temp = current_temp - (update_time * K_per_sec)
	sc.ChaseLS.set_PID_temp(1, current_temp)
	print('Setting PID to %3.fmK'%(current_temp*1e3))
	time.sleep(10)

sc.ChaseLS.set_PID_temp(1, wafer_low_temp - 0.050)

while float(gt.gettemp(logfile, 'UC Stage')) > wafer_low_temp:
	time.sleep(update_time)

# terminate ledgerman
proc_legerman.terminate()
# record the end time
down_end = time.time()
# save start and end times to a pkl file
f=open(down_times, 'w')
pickle.dump({'starttime':down_start, 'endtime':down_end}, f)
f.close()

# re-set the PID to wafer_low_temp
sc.ChaseLS.set_PID_temp(1, wafer_low_temp)

# start ledgerman
proc_ledgerman = subprocess.Popen(['python', ledgerman_path, hwm_file, R_up_path])
# record the start time
up_start = time.time()
print('Starting ramp up...')

# start increasing the temperature
sc.ChaseLS.set_PID_temp(1,wafer_low_temp)
time.sleep(1)
sc.ChaseLS.set_heater_range(2)
time.sleep(1)
current_temp=wafer_low_temp
time.sleep(1)
while current_temp < wafer_high_temp:
	time.sleep(update_time)
	current_temp = current_temp + (update_time * K_per_sec)
	sc.ChaseLS.set_PID_temp(1, current_temp)
	print('Setting PID to %3.fmK'%(current_temp*1e3))

while float(gt.gettemp(logfile, 'UC Stage')) < wafer_high_temp:
	time.sleep(update_time)

# end ledgerman data taking
proc_ledgerman.terminate()
# record the end time
up_end=time.time()
# write start and end times to a pkl file
f=open(up_times, 'w')
pickle.dump({'starttime':up_start, 'endtime':up_end},f)
f.close()

print 'Finished R vs T'
