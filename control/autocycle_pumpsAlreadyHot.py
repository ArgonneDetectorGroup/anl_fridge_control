import sys
sys.path.append('/home/spt3g/')

import serial
import pydfmux
import os, time

import sys
import he10_fridge_control.control.gettemp as gt
from anl_fridge_control.control.basic_functions import finish_cycle
from anl_fridge_control.control.basic_functions import zero_everything
import anl_fridge_control.serial_connections as sc
import datetime



def autocycle_alreadyHot(logfile=''):
    '''
    This is a function to run a fridge cycle.  Note that it takes 6+ hours to run.
    '''
    try:                          
        
        print('beginning cycle ' + str(datetime.datetime.now()))
        
        sc.He4p.remote_set()
        sc.He3ICp.remote_set()
        sc.He3UCp.remote_set()

        print 'Setting the heater, switches, and pumps to 0.'

        zero_everything()

        print 'Waiting for switches to cool.'

        while float(gt.gettemp(logfile, 'He3 IC Switch'))>5.00:
            time.sleep(10)
        while float(gt.gettemp(logfile, 'He3 UC Switch'))>5.00:
            time.sleep(10)
        while float(gt.gettemp(logfile, 'He4 IC Switch'))>5.00:
            time.sleep(10)
        print 'Switches are cool, beginning heating.'

        print ''

        print 'Turning He4 pump to 10.00 V.'
        sc.He4p.set_voltage(10.00)

        print 'Turning inter pump to 5.10 V.'
        sc.He3ICp.set_voltage(5.1)

        print 'Turning ultra pump to 5.30 V.'
        sc.He3UCp.set_voltage(5.30)

                
        print 'Waiting for He4 pump temperature to reach 43 K.'
        while float(gt.gettemp(logfile, 'He4 IC Pump'))<43: #43:
            time.sleep(10)

        print 'Turning He4 pump to 3.0 V.'
        sc.He4p.set_voltage(3.00)

        print 'Waiting 100s.'
        time.sleep(100)

        print 'Setting He4 pump to 0.0 V.'
        sc.He4p.set_voltage(0.00)

        print 'Sleeping for 3 minutes.'
        time.sleep(180)
                
        print 'Setting He4 switch to 4.00 V.'
        sc.He4s.set_voltage(4.00)

        print 'Sleeping for 2 minutes.'
        time.sleep(120)

        print 'Setting IC pump to 5.1 V and UC pump to 6.3.'
        sc.He3UCp.set_voltage(6.30)
        time.sleep(3)
        sc.He3ICp.set_voltage(5.10)

        print 'Waiting for He3 IC Pump temperature to exceed 52K.'
        while float(gt.gettemp(logfile, 'He3 IC Pump'))<52:
            time.sleep(10)
        
        print('Setting inter pump to 3.0 V.')
        sc.He3ICp.set_voltage(3.00)

        print('Waiting for He3 UC Pump temperature to exceed 52K.')
        while float(gt.gettemp(logfile, 'He3 UC Pump'))<52:
            time.sleep(10)

        print('Setting ultra pump to 5.00 V.')
        sc.He3UCp.set_voltage(5.00)
    
        print('waiting for HEX to drop below 1K')
        while float(gt.gettemp(logfile, 'HEX'))>1:
            print('HEX is ' + str(gt.gettemp(logfile, 'HEX')) + ' K.')
            time.sleep(120)
        
        time.sleep(60)

        finish_cycle(logfile)

        print 'Cycle is complete.'
        return

    except:
        print 'Crashed!'
        print datetime.datetime.now()
        print 'Zeroing everything for safety.'
        zero_everything()

if __name__=='__main__':
	import argparse as ap
        parser=ap.ArgumentParser(description =' Process the logfile')
        parser.add_argument('logfile',action='store',default='',help='fridge logfile')
        args=parser.parse_args()
        if  os.path.isfile(args.logfile):
                
                # check mezzanines are off
                #hwm_location = '/home/spt3g/hardware_maps/hwm_anl_forautocycle/hwm.yaml'
                #s      = pydfmux.load_session(file(hwm_location))
                #hwm    = s['hardware_map']
                #sqcbs  = hwm.query(pydfmux.SQUIDController)
                #for sqcb in sqcbs:
                #    if sqcb.mezzanine.get_mezzanine_power():
                #        sqcb.mezzanine.set_mezzanine_power(False)
                #    if sqcb.mezzanine.get_mezzanine_power():
                #        print 'Mezzanine on, autocycle failed to turn off.'
                
                print args.logfile
                autocycle(logfile=args.logfile)
        else:
                raise NameError('Logfile does not exist, Exiting')
