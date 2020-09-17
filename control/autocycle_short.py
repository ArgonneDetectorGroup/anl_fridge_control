import sys
sys.path.append('/home/spt3g/')
import serial
import pydfmux
import os, time
import sys
import he10_fridge_control.control.gettemp as gt
from anl_fridge_control.control.basic_functions import finish_cycle
from anl_fridge_control.control.basic_functions import zero_everything
import anl_fridge_control.control.serial_connections as sc
import datetime



def autocycle_short(logfile=''):
    '''
    This is a function to run a fridge cycle.  It runs in about 5 hours,
    and gives a fridge hold time of about 50 hours with no stage heating or 
    other extra loads.
    
    logfile = path to temperature logging file where the function can look up current fridge temps
    target_temp is the temperature in K the IC and UC pumps hit before moving on to the He4 pump
    condense_time is the time in seconds after the He4 pump is up to temperature and before hitting the He4 switch
    This script is based on autocycle.py, but was significantly edited by AEL in late 2018 
    to provide a shorter cycle time at the expense of hold time. It still holds for a couple 
    days under normal loading
    '''
    target_temp=35
    condense_time=70


    try:
        sc.He4p.remote_set()
        sc.He3ICp.remote_set()
        sc.He3UCp.remote_set()

        print('Setting the heater, switches, and pumps to 0. ' + str(datetime.datetime.now()))
        zero_everything()

        print('Waiting for switches to cool.')
        while float(gt.gettemp(logfile, 'He3 IC Switch'))>5.00:
            time.sleep(10)
        while float(gt.gettemp(logfile, 'He3 UC Switch'))>5.00:
            time.sleep(10)
        while float(gt.gettemp(logfile, 'He4 IC Switch'))>5.00:
            time.sleep(10)
        print('Switches are cool, begin pump heating. '+ str(datetime.datetime.now()))

        #start pre-warming IC and UC pumps
        print('Turning inter pump to 10 V.')
        sc.He3ICp.set_voltage(10.0)
        print('Turning ultra pump to 7.50 V.')
        sc.He3UCp.set_voltage(7.50)
        time.sleep(2)
        #watch IC and UC pump temps, when one reaches 35K, turn down the voltage
        print('Waiting for IC and UC pumps to reach 35 K')

        print(gt.gettemp(logfile, 'He3 UC Pump'))
        while float(gt.gettemp(logfile, 'He3 UC Pump'))<target_temp or float(gt.gettemp(logfile, 'He3 IC Pump'))<target_temp:     #if either IC or UC is still below target_temp
            if float(gt.gettemp(logfile, 'He3 UC Pump'))>target_temp and float(sc.He3UCp.read_voltage())>6.11:               #if UC over target_temp and the pump voltage is still high
                print('Turning UC pump to 6.10 V.')
                sc.He3UCp.set_voltage(6.10)
                time.sleep(3)
            if float(gt.gettemp(logfile, 'He3 IC Pump'))>target_temp and float(sc.He3ICp.read_voltage())>5.51:                 #if IC over target_temp and pump voltage is still high
                print('Turning IC pump to 5.50 V.')
                sc.He3ICp.set_voltage(5.50)
                time.sleep(3)
            time.sleep(20)         
            
        #make sure both UC and IC pumps got turned down
        print('Turning IC pump to 5.20 V.')
        sc.He3ICp.set_voltage(5.20)
        time.sleep(3)
        print('Turning UC pump to 6.10 V. ' + str(datetime.datetime.now()))
        sc.He3UCp.set_voltage(6.10)
      
        time.sleep(3)
        
        #Start heating He4 pump       
        print('Turning He4 pump to 12.0 V.')
        sc.He4p.set_voltage(12.0)
        time.sleep(1)
        #wait for He4 to hit 37.  If IC or UC hit 52 while waiting, turn them down    
        print('Waiting for He4 pump temperature to reach 37 K. Monitoring IC and UC pumps')
        while float(gt.gettemp(logfile, 'He4 IC Pump'))<37: #43   38
            if float(gt.gettemp(logfile, 'He3 UC Pump'))>52 and float(sc.He3UCp.read_voltage())>6.0:   #if UC over temp and the pump voltage is still high
                print('Turning UC pump to 5.2 V.')
                sc.He3UCp.set_voltage(5.2)
                time.sleep(3)
            if float(gt.gettemp(logfile, 'He3 IC Pump'))>52 and float(sc.He3ICp.read_voltage())>5.1:    #if IC over temp and pump voltage is still high
                print('Turning IC pump to 4 V.')
                sc.He3ICp.set_voltage(4.0)
                time.sleep(3)
            time.sleep(10)
        time.sleep(1)
        #turn off He4 pump in two steps
        print('Turning He4 pump to 3.0 V. ' + str(datetime.datetime.now()))
        sc.He4p.set_voltage(3.00)
        time.sleep(10) #300 #180
        print('Setting He4 pump to 0.0 V.')
        sc.He4p.set_voltage(0.00)

        #condense He4 for a short time and then hit the He4 switch
        #this condense time is the domanint parameter in setting the
        #cycle time and the hold time
        print('Sleeping for ' + str(condense_time) + ' seconds.')
        time.sleep(condense_time) #70 #100 #80        
        print('Setting He4 switch to 4.00 V.')
        sc.He4s.set_voltage(4.00)
        time.sleep(2)
        
        #turn IC and UC pumps back up incase temps are sagging
        print('turning IC and UC pumps back up')
        sc.He3ICp.set_voltage(5.2)
        time.sleep(2)
        sc.He3UCp.set_voltage(6.1)
        time.sleep(2)
        
        #wait for the IC to slowly work its way up to 52 and then turn down to equilibrium voltage
        #watch IC and UC pump temps, when one reaches 52K, turn down the voltage
        target_temp=52
        ICtargetReached=False  
        UCtargetReached=False 
        print('Waiting for IC and UC pumps to reach 52 K')
        while ICtargetReached==False or UCtargetReached==False:     #if either IC or UC hasn't yet hit target_temp
            if float(gt.gettemp(logfile, 'He3 UC Pump'))>target_temp:        #if UC over target_temp
                UCtargetReached=True
                if float(sc.He3UCp.read_voltage())>5.2: #if the pump is still high
                    print('Turning UC pump to 5.1 V. '  + str(datetime.datetime.now()))
                    sc.He3UCp.set_voltage(5.1)
                    time.sleep(3)
            if float(gt.gettemp(logfile, 'He3 IC Pump'))>target_temp:        #if IC over target_temp
                ICtargetReached=True
                if float(sc.He3ICp.read_voltage())>3.1: #if the pump is still high
                    print('Turning IC pump to 3 V. '  + str(datetime.datetime.now()))
                    sc.He3ICp.set_voltage(3.0)
                    time.sleep(3)
            time.sleep(20)         
            
        #make sure both UC and IC pumps got turned down
        print('Turning IC pump to 3 V.')
        sc.He3ICp.set_voltage(3.0)
        time.sleep(2)
        print('Turning UC pump to 5.1 V.')
        sc.He3UCp.set_voltage(5.1)
        time.sleep(2)
        
        #Make sure the He4 pump has dropped before moving to the HEX watcher 
        #this ensures you don't move on when the HEX hasn't yet dropped below 1K
        print('Waiting for the He4 Pump to cool below 4 K ' + str(datetime.datetime.now()))
        while float(gt.gettemp(logfile, 'He4 IC Pump'))>4:
            time.sleep(30)
        
        #waits for the HEX to go above 1 K and then does final UC switch throw                
        finish_cycle(logfile)

        print('Cycle is complete. '+ str(datetime.datetime.now()))
        return

    except:
        print('Crashed!')
        print(datetime.datetime.now())
        print('Zeroing everything for safety.')
        zero_everything()



if __name__=='__main__':
    import argparse as ap
    
    parser=ap.ArgumentParser(description =' Process the logfile')
    parser.add_argument('logfile',action='store',default='',help='fridge logfile')
    args=parser.parse_args()
    if  os.path.isfile(args.logfile):                
        print(args.logfile)
        autocycle_short(logfile=args.logfile)
    else:
        raise NameError('Logfile does not exist, Exiting')
        

