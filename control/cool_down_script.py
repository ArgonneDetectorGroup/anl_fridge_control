import sys
sys.path.append('/home/spt3g/')
import he10_fridge_control.control.gettemp as gt
import anl_fridge_control.control.serial_connections as sc
import time
import datetime
from anl_fridge_control.control.autocycle import autocycle
from anl_fridge_control.control.autocycle_short import autocycle_short
from anl_fridge_control.control.basic_functions import zero_everything

'''
run_cooldown can be called from an interactive or command line python session

e.g., 
python /home/spt3g/anl_fridge_control/control/cool_down_script.py  /home/spt3g/he10_logs/20171011_read.h5

or in ipython:
from anl_fridge_control.control.cool_down_script import run_cooldown
run_cooldown(logfile='/home/spt3g/he10_logs/20171011_read.h5')

This script should be called during the initial cooldown of the cryostat. It regulates the pump temperatures to ensure a thermal link between the cold stages and speed the cooldown. 

'''


def run_cooldown(logfile='', set_temp=39, cycle_type='short'):

    '''
    speeds up cooldown by heating switches and pumps for improved thermal conductivity until IC and UC are reasonably cold
    
    logfile = path to fridge logging file where function can read current fridge temps
    set_temp = temperature in K to which we heat the pumps
    cycle_type = "short" or "long".  "long" takes ~7-8 hours and gives a ~80 hour hold time.  "short" takes ~5 hours and gives a ~50 hour hold time.
    
    '''
    sc.He4p.remote_set()
    sc.He3ICp.remote_set()
    sc.He3UCp.remote_set()
    zero_everything()
    if len(logfile)==0:
        raise ValueError('No logfile specified')
                    
    if gt.gettemp(logfile,'He3 UC Pump')<25 or gt.gettemp(logfile,'He3 IC Pump')<25 or gt.gettemp(logfile,'He4 IC Pump')<25:
        sc.He4p.set_voltage(4)
        sc.He3ICp.set_voltage(4)
        sc.He3UCp.set_voltage(4)
        print('Heating pumps, waiting 5 min')
        time.sleep(300)
    i=True
    while i is True:
        if (gt.gettemp(logfile,'mainplate') < 9.2):
            if gt.gettemp(logfile,'IC Stage')>10 :
                if gt.gettemp(logfile,'He3 UC Pump')<40 and gt.gettemp(logfile,'He3 IC Pump')<40 and gt.gettemp(logfile,'He4 IC Pump')<40:
                    print('main plate is cool, heating pumps a little bit: '+ str(datetime.datetime.now()))
                    heat_pumps(logfile,heat_temp=set_temp,voltage=5,stable_voltage=2.0)
                    print('Heated pumps, waiting a bit '+str(datetime.datetime.now()))
                    time.sleep(120) #240
                else:
                    print('pumps are already hot, waiting')
                    sc.He4p.set_voltage(1.9)
                    sc.He3ICp.set_voltage(1.9)
                    sc.He3UCp.set_voltage(1.8)
                    time.sleep(300)
            else:
                print('IC Stage is below 10K')
                i=False

        else:
            print('Mainplate is still hot: '+ str(datetime.datetime.now()) + ' ' + str(gt.gettemp(logfile,'mainplate')))
            time.sleep(300)

    #time.sleep(3600)
    time.sleep(60)

    i=True
    while i is True:
        print('IC Stage below 10K. Keeping main plate cold')
        if gt.gettemp(logfile,'mainplate') < 6:
            print('heating pumps')
            heat_pumps(logfile,heat_temp=set_temp,voltage=5,stable_voltage=2)
            time.sleep(120)
        if gt.gettemp(logfile,'mainplate') > 9:
            print('Mainplate>9.  Zeroing pumps')
            sc.He4p.set_voltage(0)
            sc.He3ICp.set_voltage(0)
            sc.He3UCp.set_voltage(0)
            while gt.gettemp(logfile,'mainplate') > 9:
                time.sleep(60)
        if gt.gettemp(logfile,'He3 IC Pump')>40:
            print('IC pump > 40, zeroing pumps')
            sc.He4p.set_voltage(0)
            sc.He3ICp.set_voltage(0)
            sc.He3UCp.set_voltage(0)
            while gt.gettemp(logfile,'He3 IC Pump') >40:
                time.sleep(100)
        if gt.gettemp(logfile,'UC Stage') < 6:
            print('UC Stage < 6, zeroing pumps')
            sc.He4p.set_voltage(0)
            sc.He3ICp.set_voltage(0)
            sc.He3UCp.set_voltage(0)
            i=False
        else:
            print('UC Stage is at '+ str(gt.gettemp(logfile,'UC Stage'))+'. Waiting a little longer')
            time.sleep(300)
    sc.He4p.set_voltage(0)
    sc.He3ICp.set_voltage(0)
    sc.He3UCp.set_voltage(0)


    time.sleep(360)                            
    print('Starting the He10 cycle: '+str(datetime.datetime.now()))
    
    if cycle_type=="long":
        autocycle(logfile=logfile)
    elif cycle_type=="short":
        autocycle_short(logfile=logfile)
    elif cycle_type=="skip":
        print('contnuing without cycle')
    else:
        print('WARNING: incorrect cycle_type: ' + str(cycle_type) + '. Aborting.')
    return
                                                






def heat_pumps(logfile,heat_temp=30,voltage=5,stable_voltage=3):
    sc.He4p.set_voltage(voltage)
    sc.He3ICp.set_voltage(voltage)
    sc.He3UCp.set_voltage(voltage)
    heating=True
    He4=0
    He3I=0
    He3U=0
    while heating is True:
        if He4 !=1:
            temp=gt.gettemp(logfile,'He4 IC Pump')
            if temp > heat_temp:
                print('He4 pump has reached heat_temp.  Stabalizing.')
                sc.He4p.set_voltage(stable_voltage)
                He4 =1
        if He3I !=1:
            temp=gt.gettemp(logfile,'He3 IC Pump')
            if temp > heat_temp:
                print('IC pump has reached heat_temp.  Stabalizing.')
                sc.He3ICp.set_voltage(stable_voltage)
                He3I =1
        if He3U !=1:
            temp=gt.gettemp(logfile,'He3 UC Pump')
            if temp > heat_temp:
                print('UC pump has reached heat_temp.  Stabalizing.')
                sc.He3UCp.set_voltage(stable_voltage)
                He3U =1
        if  (He4+He3I+He3U)==3:
            heating=False
            print('done heating')
        else:
            time.sleep(60)
    return                 

if __name__=='__main__':
    import argparse as ap
    import os
    parser=ap.ArgumentParser(description =' Process the logfile')
    parser.add_argument('logfile',action='store',default='',help='fridge logfile')
    args=parser.parse_args()
    if  os.path.isfile(args.logfile):
        print(args.logfile)
        run_cooldown(logfile=args.logfile)
    else:
        raise NameError('Logfile does not exist, Exiting')
                                                            
