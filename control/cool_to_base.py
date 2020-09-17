import sys
sys.path.append('/home/spt3g/')
import he10_fridge_control.control.gettemp as gt
import anl_fridge_control.control.serial_connections as sc
import time
import datetime

def get_temp(logfile,therm):
    return float(gt.gettemp(logfile,therm))

def cool_to_base():
    # set the power supplies to remote mode
    sc.He4p.remote_set()
    sc.He3ICp.remote_set()
    sc.He3UCp.remote_set()
    
    
    sc.ChaseLS.set_PID_temp(1,0.000)
    time.sleep(1)
    sc.ChaseLS.set_heater_range(0)
                            

    print('Turning off inter pump and ultra pump.')
    print(datetime.datetime.now())    
    sc.He3ICp.set_voltage(0.00)
    sc.He3UCp.set_voltage(0.00)
    
    time.sleep(60)
    
    print('Turning on inter switch.')
    print(datetime.datetime.now())
    sc.He3ICs.set_voltage(4.00)
    time.sleep(240)

    print('Turning on ultra switch.')
    print(datetime.datetime.now())
    sc.He3UCs.set_voltage(3.00)

    return
