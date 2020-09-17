# measure_RofT.py
# A script for automating R(T) measurements.
#
# Adam Anderson
# adama@fnal.gov
# 27 April 2016
#
# Modified for ANL by Lauren Saunders
# ljsaunders@uchicago.edu
# 12 June 2017


# TO DO:
# handle file IO errors -AHHH

import anl_fridge_control.serial_connections as sc
import he10_fridge_control.control.gettemp as gt
import pydfmux
#import pydfmux.spt3g.northern_tuning_script as nts
import time
import cPickle as pickle
import subprocess
import os
import datetime


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
logfile = '/home/spt3g/he10_logs/20181027_read.h5'
hwm_file = '/home/spt3g/hardware_maps/hwm_anl_20181113_w148_lctest_0135/hwm.yaml'
ledgerman_path = '/home/spt3g/spt3g_software/dfmux/bin/ledgerman.py'
R_down_path = '/home/spt3g/ledgerman_output/20181128/down.nc'
down_times = '/home/spt3g/ledgerman_output/20181128/down_times.pkl' 
R_up_path = '/home/spt3g/ledgerman_output/20181128/up.nc'
up_times = '/home/spt3g/ledgerman_output/20181128/up_times.pkl'


wafer_high_temp = 0.6
wafer_low_temp = 0.300
K_per_sec = 4e-4 #1e-4
update_time = 10
setup_fridge=False
setup_bolos=False
take_down_sweep=False
take_up_sweep=True

#######################################################################
print 'Starting R(T) script.'

if setup_fridge:
    # unlatch the switches
    print('Turning off switches...')
    sc.He3UCs.set_voltage(0.0)
    sc.He3ICs.set_voltage(0.0)

    print('wait for switches to cool')
    while float(gt.gettemp(logfile, 'He3 UC Switch'))>4.00:
            time.sleep(10)
    while float(gt.gettemp(logfile, 'He3 IC Switch'))>4.00:
            time.sleep(10)

    # heat the fridge to the high temperature
    print('Heating up fridge...')
    sc.He3UCp.set_voltage(3.0) 
    sc.He3ICp.set_voltage(0.0) # change back to 1V ?
    time.sleep(7*60)
    print('PID to 500 mk')
    sc.ChaseLS.set_PID_temp(1, 0.500)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(2)
    
    time.sleep(1)

    print('wait to reach 500 mK')
    while float(gt.gettemp(logfile, 'UC Stage')) < 0.500:
            print gt.gettemp(logfile, 'UC Stage')
            time.sleep(5)

    sc.He3ICp.set_voltage(0.00)
    sc.He3UCp.set_voltage(1.00)
    sc.ChaseLS.set_PID_temp(1, wafer_high_temp)
    time.sleep(5)

    print 'waiting for stage to reach high temp'
    while float(gt.gettemp(logfile, 'UC Stage')) < wafer_high_temp:
            print gt.gettemp(logfile, 'UC Stage')
            time.sleep(5)

    print('wait 5 minutes')
    time.sleep(300)

if setup_bolos:
    time.sleep(20*60)
    # zero combs
    run_do_zero_combs()
    # overbias bolos
    run_overbias_bolos()

    time.sleep(60)

if take_down_sweep:
    print('start ledgerman')

    # make ledgerman directory
    ledgerman_dir = os.path.dirname(R_down_path)
    if not os.path.exists(ledgerman_dir):
        os.makedirs(ledgerman_dir)
    
    # record start time
    print('record start time')
    down_start = time.time()
    time.sleep(1)    
    print('starting ledgerman')
    proc_ledgerman = subprocess.Popen(['python', ledgerman_path, hwm_file, R_down_path])
    

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

    print('wait to actually hit wafer_low_temp')
    while float(gt.gettemp(logfile, 'UC Stage')) > wafer_low_temp:
        time.sleep(update_time)

    # record the end time
    down_end = time.time()
    time.sleep(1)
    # terminate ledgerman
    proc_ledgerman.terminate()
    
    # save start and end times to a pkl file
    
    f=open(down_times, 'w')
    pickle.dump({'starttime':down_start, 'stoptime':down_end}, f)
    f.close()

if take_up_sweep:
        
    # re-set the PID to wafer_low_temp
    sc.ChaseLS.set_PID_temp(1, wafer_low_temp)

    print 'waiting for stage to reach low temp'
    while float(gt.gettemp(logfile, 'UC Stage')) > wafer_low_temp or float(gt.gettemp(logfile, 'UC Stage')) < (wafer_low_temp - .010):
        print gt.gettemp(logfile, 'UC Stage') 
        time.sleep(5)

    # wait to stabilize if only doing upsweep
    if take_down_sweep == False:
        print 'temperature stabilization, 5 mins   ' + str(datetime.datetime.now())
        time.sleep(300)
        
    # start ledgerman
    ledgerman_dir = os.path.dirname(R_up_path)
    if not os.path.exists(ledgerman_dir):
        os.makedirs(ledgerman_dir)
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
	current_temp = current_temp + (update_time * K_per_sec/2.)
	sc.ChaseLS.set_PID_temp(1, current_temp)
        print('Setting PID to %3.fmK'%(current_temp*1e3))
                
    while float(gt.gettemp(logfile, 'UC Stage')) < wafer_high_temp:
	time.sleep(update_time)

    # end ledgerman data taking
    proc_ledgerman.terminate()
    # record  the end time
    up_end=time.time()
    # write start and end times to a pkl file

    
    ledgerman_dir = os.path.dirname(ledgerman_path)
    if not os.path.exists(ledgerman_dir):
        os.makedirs(ledgerman_dir)

    f=open(up_times, 'w')
    pickle.dump({'starttime':up_start, 'stoptime':up_end},f)
    f.close()


print 'Finished R vs T'
