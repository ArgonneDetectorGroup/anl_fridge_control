# basic_functions.py
#
# Automated codes to start things at the beginning of the day, run an automatic
# fridge cycle, and turn all power supplies and heaters to zero volts.
#
# LJS 2016-10-14

import datetime
import numpy as np
import os,time
#import pydfmux.spt3g.northern_tuning_script as nts
import sys
sys.path.append('/home/spt3g/')

import he10_fridge_control.control.gettemp as gt
import anl_fridge_control.control.serial_connections as sc

###############################################################################
##### Items below do not need to be changed after setting for your fridge #####
###############################################################################

def start_of_day(logfile, heating_type, set_squid_feedback=False, set_gain=False):
    '''
    Starts things for you by heating the UC Stage, initializing the board, tuning squids, and taking a rawdump.
    '''
    # set voltages to 0, let the switches cool
    print('Setting the switches to zero to cool.')
    sc.He3ICp.remote_set()
    sc.He3UCp.remote_set()

    sc.He3ICp.set_voltage(0)
    sc.He3ICs.set_voltage(0)
    sc.He3UCp.set_voltage(0)
    sc.He3UCs.set_voltage(0)


    while float(gt.gettemp(logfile, 'He3 UC Switch'))>1:
        while float(gt.gettemp(logfile, 'He3 IC Switch'))>1:
            gt.gettemp(logfile, 'He3 UC Switch'); gt.gettemp(logfile, 'He3 IC Switch')
            time.sleep(10)
    if heating_type=='PID':
        # set UC pump voltage and start the heater to get above Tc
        print('Setting ultra pump to 3.00 V.')
        sc.He3UCp.set_voltage(3.00)
        time.sleep(60)
        print('Setting the heater to 500 mK at 1.5 mW.')
        sc.ChaseLS.set_PID_temp(1,0.500)
        time.sleep(1)
        sc.ChaseLS.set_heater_range(2)
        time.sleep(1)
        gt.gettemp(logfile, 'UC Head')
        while float(gt.gettemp(logfile, 'UC Head'))<0.500:
            time.sleep(20)
            gt.gettemp(logfile, 'UC Head')
        time.sleep(1)
        print('Setting the heater to 650 mK at 15 mW.')
        sc.ChaseLS.set_PID_temp(1, 0.650)
        time.sleep(1)
        sc.ChaseLS.set_heater_range(3)
        time.sleep(1)

        print('Setting the ultra pump to 1.50 V')
        sc.He3UCp.set_voltage(1.00)
        while float(gt.gettemp(logfile, 'UC Head'))<0.650:
            time.sleep(20)
            gt.gettemp(logfile, 'UC Head')

        sc.He3UCp.set_voltage(1.50)
        print('Waiting...')
        time.sleep(300)

    elif heating_type=='pumps':
        print('Setting the He3 UC pump to 3.00 V')
        sc.He3UCp.set_voltage(3.00)
        print('Setting the He3 IC pump to 3.00 V')
        sc.He3ICp.set_voltage(3.00)

        print('Waiting for IC Head temperature to rise')
        while float(gt.gettemp(logfile, 'IC Head'))<0.650:
            time.sleep(20)
        print('Setting He3 IC pump to 0.50 V')
        sc.He3ICp.set_voltage(0.50)

        print('Waiting for UC Head temperature to rise')
        while float(gt.gettemp(logfile, 'UC Head'))<0.650:
            time.sleep(20)
        print('Setting He3 UC pump to 1.80 V')
        sc.He3UCp.set_voltage(1.80)

        print('Waiting 5 minutes...')
        time.sleep(300)

    # initialize the board
    print('Initializing the board.')
    try:
        nts.run_initialize()
    except URLError:
        print('Could not initialize because the power is not on!  Waiting...')
        initboard = input("Type 'done' when the power is set to 17 V.    ")
        if initboard == 'done':
            nts.run_initialize()

    # zero combs
    print('Zeroing combs')
    nts.run_do_zero_combs()

    # heat the squids
    print('Heating SQUIDs.')
    nts.run_heat_squids()

    # tune the squids
    print('Tuning SQUIDs.')
    nts.run_tune_squids()

    # squid feedback (optional)
    if set_squid_feedback:
        print('Setting SQUID feedback.')
        nts.run_enable_feedback()

    # set gain (optional)
    if set_gain:
        print('Setting gain.')
        nts.run_set_gain()

    # take a rawdump
    print('Taking a rawdump.')
    nts.run_take_rawdump()

    print('Startup is complete!')


def zero_everything():
    '''
    Sets UC and IC voltages on pumps and switches to 0, sets the heater temperature and range to 0.  A good safety measure for not accidentally blowing the cycle.
    '''
    sc.He3ICp.set_voltage(0.00)
    time.sleep(1)
    sc.He3UCp.set_voltage(0.00)
    time.sleep(1)
    sc.He3ICs.set_voltage(0.00)
    time.sleep(1)
    sc.He3UCs.set_voltage(0.00)
    time.sleep(1)
    sc.He4p.set_voltage(0.00)
    time.sleep(1)
    sc.He4s.set_voltage(0.00)
    sc.ChaseLS.set_PID_temp(1,0.000)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(0)

def finish_cycle(hex_filename):
    print('Beginning the hex_watcher_3000 program to finish the cycle......')
    print(gt.gettemp(hex_filename,'HEX'))
    while float(gt.gettemp(hex_filename,'HEX'))<1.06:
        time.sleep(120)
        print(str(datetime.datetime.now()) + ' HEX temp: ' + str(gt.gettemp(hex_filename,'HEX')))
    time.sleep(60)

    print('Turning off inter pump and ultra pump. ' + str(datetime.datetime.now()))

    sc.He3ICp.set_voltage(0.00)
    time.sleep(1)
    sc.He3UCp.set_voltage(0.00)

    time.sleep(60)

    print('Turning on inter switch. ' + str(datetime.datetime.now()))
    sc.He3ICs.set_voltage(4.00)
    time.sleep(240)

    print('Turning on ultra switch. ' + str(datetime.datetime.now()))
    sc.He3UCs.set_voltage(3.00)

    print('Waiting 30 min for cooling... ' + str(datetime.datetime.now()))
    time.sleep(1800)

    print('The hex_watcher_3000 has done its duty. ' + str(datetime.datetime.now()))

def blow_cycle():

    sc.He4p.remote_set()
    sc.He3ICp.remote_set()
    sc.He3UCp.remote_set()
    sc.He4s.remote_set()
    sc.He3ICs.remote_set()
    sc.He3UCs.remote_set()

    print('Setting switches to 0.')
    sc.He4s.set_voltage(0.00)
    sc.He3ICs.set_voltage(0.00)
    sc.He3UCs.set_voltage(0.00)
    time.sleep(120)

    print('Setting pumps to 2.5 V')
    sc.He4p.set_voltage(2.50)
    sc.He3ICp.set_voltage(2.50)
    sc.He3UCp.set_voltage(2.50)

    return
    
def get_state():
    '''
    reads the voltage on all of the switches and pumps and reads the percentage of the heater, and prints them to the termal all together.  Useful for a quick check of the fridge state.  

    written by AEL 5/2019.  lowitz@uchicago.edu
    '''

    #read in all the things
    He3ICp=sc.He3ICp.read_voltage()
    He3UCp=sc.He3UCp.read_voltage()
    He4p=sc.He4p.read_voltage()
    He3ICs=sc.He3ICs.read_voltage()
    He3UCs=sc.He3UCs.read_voltage()
    He4s=sc.He4s.read_voltage()
    heat=sc.ChaseLS.get_HTR_output()
    
    #make them pretty
    print(He3ICp[:-2])
    print(type(He3ICp))
    He3ICp=round(float(He3ICp[:-2]),2)
    He3UCp=round(float(He3UCp[:-2]),2)
    He4p=round(float(He4p[:-2]),2)
    He3ICs=round(float(He3ICs[:-2]),2)
    He3UCs=round(float(He3UCs[:-2]),2)
    He4s=round(float(He4s[:-2]),2)
    heat=round(float(heat[:-2]),0)
    
    #print them out
    print('IC pump: ' + str(He3ICp) + ' V')
    print('UC pump: ' + str(He3UCp) + ' V')
    print('He4 pump: ' + str(He4p) + ' V')
    print('')
    print('IC switch: ' + str(He3ICs) + ' V')
    print('UC switch: ' + str(He3UCs) + ' V')
    print('He4 switch: ' + str(He4s) + ' V')
    print('')
    print('heater: ' + str(heat) + '%')
    
    
    
    
    

