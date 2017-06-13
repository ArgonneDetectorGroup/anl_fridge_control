# measure_GofT.py
#
# Script for using PID control feature of Lakeshore 350 in order to automatically take G(T)
# measurements (Psat as a function of T). This script isn't totally cryostat-independent,
# but it should be nearly so if you are using a heater close to your UC head to PID control
# the stage temperature, wait for a separate thermometry near the wafer to stabilize between
# measurements.
#
# Adam Anderson
# adama@fnal.gov
# 27 April 2016
#
# Modified for ANL by Lauren Saunders
# ljsaunders@uchicago.edu
# 13 June 2017


import pydfmux
import os,time
import datetime
import numpy as np
import cPickle as pickle
import pydfmux.spt3g.northern_tuning_script as nts
import anl_fridge_control.serial_connections as sc

import sys
sys.path.append('/home/spt3g/')
import he10_fridge_control.control.gettemp as gt

###### user parameters ######
logfile = '/home/spt3g/he10_logs/20170302_again_read.h5'
setpoints = np.linspace(0.300, 0.600, 12)
wafertemps_filename = '/home/spt3g/output/20170406/GofT_temps.pkl'

###### THIS IS THE PART WHERE IT DOES THINGS ########
print 'Starting G(T)'

sc.He3ICp.set_voltage(0)
sc.He3UCp.set_voltage(0)
sc.He3ICs.set_voltage(0)
sc.He3UCs.set_voltage(0)
sc.ChaseLS.set_PID_temp(1, 0.500)
time.sleep(1)
sc.ChaseLS.set_heater_range(2)
while float(gt.gettemp(logfile, 'UC Stage'))<0.450:
    time.sleep(10)
sc.ChaseLS.set_PID_temp(1,0.650)
time.sleep(1)
sc.ChaseLS.set_heater_range(3)
time.sleep(1)
while float(gt.gettemp(logfile, 'UC Stage'))<0.650:
    time.sleep(20)
time.sleep(300)

print 'Zeroing combs'
nts.run_do_zero_combs()

print 'Overbiasing'
nts.run_overbias_bolos()

waferstarttemps = np.zeros(len(setpoints))
measurestarttimes = np.zeros(len(setpoints))
waferstoptemps = np.zeros(len(setpoints))
measurestoptimes = np.zeros(len(setpoints))

sc.He3ICp.set_voltage(0)
sc.He3ICs.set_voltage(0)
sc.He3UCp.set_voltage(0)
sc.He3UCs.set_voltage(0)

for jtemp in range(len(setpoints)):
    print setpoints[jtemp]
    print('Setting UC head to %f mK.' % (setpoints[jtemp]*1e3))

    sc.ChaseLS.set_PID_temp(1, setpoints[jtemp])
    time.sleep(1)
    sc.ChaseLS.set_heater_range(2)
    time.sleep(1)
    sc.He3UCs.set_voltage(3.00)
    sc.He3ICs.set_voltage(4.00)
    while float(gt.gettemp(logfile, 'UC Stage'))>(setpoints[jtemp]+0.1):
	time.sleep(60)
    sc.He3UCs.set_voltage(0.00)
    sc.He3ICs.set_voltage(0.00)
    time.sleep(5*60)

    # wait until the wafer holder temperature is stable up to 1mK;
    # give up after waiting 15 minutes
    recenttemps = [-4, -3, -2, -1]
    nAttempts = 0
    while np.abs(recenttemps[-1] - recenttemps[-4]) > 0.001 and nAttempts < 45:
        time.sleep(20)
        recenttemps.append((float(gt.gettemp(logfile, 'UC Stage')))
        nAttempts += 1
        print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        print('Wafer holder drifted %f mK.' % 1e3*np.abs(recenttemps[-1] - recenttemps[-4]))
    if nAttempts == 45:
        sc.ChaseLS.set_heater_range(0)
        sys.exit('UC Head failed to stabilize! Zeroed heater and quitting now.')

    waferstarttemps[jtemp] = gt.gettemp(logfile, 'UC Stage')
    measurestarttimes[jtemp] = time.time()
    print waferstarttemps

    time.sleep(300)

    alive = bolos.find_alive_bolos()
    noise_results_before = alive.dump_info()

    drop_bolos_results =  bolos.drop_bolos(monotonic=True,A_STEP_SIZE=0.000015,TOLERANCE=0.05)
    waferstoptemps[jtemp] = gt.gettemp(logfile, 'UC Stage')
    measurestoptimes[jtemp] = time.time()
    print waferstoptemps

    # save the data to a pickle file, rewriting after each acquisition
    f = file(wafertemps_filename, 'w')
    pickle.dump([waferstarttemps, measurestarttimes, waferstoptemps, measurestoptimes], f)
    f.close()

    alive = bolos.find_alive_bolos()
    noise_results_after = alive.dump_info()

    nts.run_do_zero_combs()

    print 'Raising temperature for overbias.'
    sc.ChaseLS.set_PID_temp(1, 0.500)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(2)
    while float(gt.gettemp(logfile, 'UC Stage'))<0.480:
        time.sleep(20)

    sc.ChaseLS.set_PID_temp(1,0.650)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(3)
    time.sleep(1)
    while float(gt.gettemp(logfile, 'UC Stage'))<0.640:
	time.sleep(10)
    time.sleep(300)

    nts.run_overbias_bolos()


sc.ChaseLS.set_heater_range(0)
time.sleep(1)
sc.ChaseLS.set_PID_temp(1, 0.000)
print waferstarttemps
print measurestarttimes
print waferstoptemps
print measurestoptimes

#zero_everything()
