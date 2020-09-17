import sys
import time
sys.path.append('/home/spt3g/')

import he10_fridge_control.control.gettemp as gt
import serial
import numpy as np
import anl_fridge_control.control.serial_connections as sc


def bring_stage_above_tc(logfile,set_temp=0.65):
    # set voltages to 0, let the switches cool
    print('Setting the switches to zero to cool.')
    sc.He3ICp.remote_set()
    sc.He3UCp.remote_set()
    
    sc.He3ICp.set_voltage(0)
    sc.He3ICs.set_voltage(0)
    sc.He3UCp.set_voltage(0)
    sc.He3UCs.set_voltage(0)
    gt.gettemp(logfile, 'He3 IC Switch'); gt.gettemp(logfile, 'He3 UC Switch')

    while float(gt.gettemp(logfile, 'He3 UC Switch'))>5:
        while float(gt.gettemp(logfile, 'He3 IC Switch'))>5:
            gt.gettemp(logfile, 'He3 UC Switch'); gt.gettemp(logfile, 'He3 IC Switch')
            time.sleep(10)

    time.sleep(2)
    print('Setting ultra pump to 3.50 V.')
    sc.He3UCp.set_voltage(3.50)  #3.5
    time.sleep(60)
    print('Setting the heater to 500 mK at 15 mW.')
    sc.ChaseLS.set_PID_temp(1, 0.500)
    time.sleep(3)
    sc.ChaseLS.set_PID_temp(1, 0.500) #try again because sometimes it silently fails the first time (AEL 8/17)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(2)
    time.sleep(1)
    gt.gettemp(logfile, 'UC Stage')
    while float(gt.gettemp(logfile, 'UC Stage'))<0.500:
        time.sleep(10)
        gt.gettemp(logfile, 'UC Stage')
    time.sleep(1)

    print('Setting the heater to '+str(set_temp)+' K at 15 mW')
    sc.ChaseLS.set_PID_temp(1, set_temp)
    time.sleep(1)
    sc.ChaseLS.set_PID_temp(1, set_temp)#try again because sometimes it silently fails the first time (AEL 8/17)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(2)
    time.sleep(1)

    print('Setting the ultra pump to 3 V')
    sc.He3UCp.set_voltage(3.0) #3.5
    while float(gt.gettemp(logfile, 'UC Stage'))<set_temp:
        time.sleep(20)
        gt.gettemp(logfile, 'UC Stage')
        print(gt.gettemp(logfile, 'UC Stage'))

    print('Setting the ultra pump to 1.9 V')
    sc.He3UCp.set_voltage(1.9)  #2.1
    print('Waiting...')
    time.sleep(300)


    return

def pid_stage_temp_with_pump(logfile,set_temp=0.65):
    
    #array is min temp, max temp, uc pump heating voltage, uc pump maintenance voltage, ic pump heating voltage, ic pump maintenance voltage
    ucpump_settings=np.array([[0.5, 0.55 ,3, 2,0,0],
                              [0.55, 0.65, 3, 2.2,0,0,0],
                              [0.65, 0.7,  4.0, 2.5,0,0],  #uc pump temp is ~ 27.7 K for this to work
                              [0.7, 0.75, 4.0, 2.7,0.5,0.5]])
    
    ginds=np.intersect1d(np.where(ucpump_settings[:,0]<= set_temp)[0],np.where(ucpump_settings[:,1]>set_temp)[0])[0]
    sc.He3UCp.set_voltage(ucpump_settings[gind,2])
    print('He3 UC pump to heating voltage: '+str(ucpump_settings[gind,2])+'V')
    time.sleep(120)
    while float(gt.gettemp(logfile, 'UC Stage')) < (set_temp - 0.01):
        time.sleep(60)
        print(gt.gettemp(logfile, 'UC Stage'))
    sc.ChaseLS.set_PID_temp(1, set_temp)
    sc.ChaseLS.set_heater_range(2)
    print('Turning on PID on Heater, reducing pump temp to maintenance voltage, waiting 5 min for stability')
    sc.He3UCp.set_voltage(ucpump_settings[gind,3])
    print(time.datetime())
    time.sleep(60*5)
    iter=True
    while iter:
        if float(sc.ChaseLS.get_HTR_output()) > 95:
            print('adjusting pump up to help heater')
            sc.He3UCP.set_voltage(float(sc.He3UCp.read_voltage())+.1)
        elif float(sc.ChaseLS.get_HTR_output())<5:
            print('adjusting pump down to prevent runaway')
            sc.He3UCP.set_voltage(float(sc.He3UCp.read_voltage())-0.1)
        else:
            iter=False
        time.sleep(60*5)
    return

'''
def monitor_pid_and_pump(logfile,set_temp=0.65):
    iter=True
    while iter:
        cur_temp=gt.gettemp(logfile,'UC Stage')
        if cur_temp- set_temp > 0.0:

    return
'''
        

