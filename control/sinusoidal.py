# sinusoidal.py
#
# 2016-09-08 LJS
#
# Tells a power supply to set voltages that vary sinusoidally
#
# UPDATE 2016-09-09: Now takes a resistance R to control the
# current.  This is to correct for the current maxing out when
# no current is chosen.  LJS

#notes from AEL 04/2018:
# Currently the Helmholtz.txt driver works with the "noisy" Keysight E3647A
# the old driver, which works with an unknown power supply, is saved as Helmholtz_old.txt
# to get started manually, 
#   import anl_fridge_control.serial_connections as sc
#   import anl_fridge_control.powersupply as PS
#   driverfile = 'Helmholtz.txt'
#   sin=PS.PowerSupply(driverfile)
#   sin.remote_set()
#   sin.set_voltage(1)
# etcetera ....

import anl_fridge_control.control.powersupply as PS
from math import cos
import time
import pickle
import subprocess
import datetime
from math import pi
import cPickle as pkl



ledgerman_path = '/home/spt3g/spt3g_software/dfmux/bin/ledgerman.py'
driverfile = 'Helmholtz.txt'


def sinuvolt(driverfile, A=.1, tint=1, tf=10, R=3.10, freq=0.01, y=0, t0=0):
    '''
    - Parameters:

        - driverfile: the driver file ('Helmholtz.txt')

        - A: the amplitude, or maximum voltage, that you want to reach

        - tint: the time interval that the code will wait before setting a new voltage
        and current

        - tf: the final time, at which the power supply will be reset to 0.0 V and 0.0 A

        - R: the resistance of the power resistor, used to calculate the correct current

        - freq: the frequency in radians/sec of the oscillation. Preset to 0.01  ### Hz? -AHHH

        - y: the offset of the initial voltage value from 0. Preset to 0

        - t0: the wait time at the beginning of the code before the voltage starts
        varying. Preset to 0
    '''

    try:
        power=PS.PowerSupply(driverfile)
        power.remote_set()
        if t0!=0:
            power.set_vi(0,0)
            time.sleep(t0)
        t=t0
        while t<tf:
            v=-0.5*A*cos(2*pi*freq*t)+(0.5*A)+y
            power.set_vi(v,v/R)
            print v
            time.sleep(tint)
            t=t+tint
        if t==tf:
            power.set_vi(0,0)

    except KeyboardInterrupt:
        power.set_vi(0,0)
        print('set to zero')
		

def helmholtz_test(driverfile, A, tint, tf, freq=0.1, hwm_location=''):
    proc_ledgerman = subprocess.Popen(['python', ledgerman_path, hwm_location, resp_savefile, '-s'])
    time.sleep(1)
    starttime = time.time()
    sinuvolt(driverfile, A, tint, tf, freq=freq)
    endtime = time.time()
    proc_ledgerman.terminate()
    f=open(time_savefile, 'w')
    pickle.dump({'starttime':starttime, 'endtime':endtime}, f)
    f.close()


if __name__ == '__main__':   
    
    ### added 20180423, AHHH <3
    
    hwm_location = '/home/spt3g/hardware_maps/hwm_anl_20180518_w142_0137/hwm_0137.yaml'
    output_dir = '/home/spt3g/output/20180521/sinusoidal_ahhh/'
    
    SQs = ['8']
    pstrings = ['0137/2/4/*']
    
    for pp, pstring in enumerate(pstrings):
        
        run_do_zero_combs()
        time.sleep(1)

        # overbias one comb
        selectbolos = hwm.bolos_from_pstring(pstring)
        bolos = build_hwm_query(selectbolos)
        run_overbias_bolos()
        time.sleep(1)
    
        # save SQ transimpedance
        sqtrans = squids.calc_Z_analytic()
        print sqtrans
        pkl.dump(sqtrans, open(output_dir + 'SQ' + SQs[pp] + '_transoverbiased_x.pkl', 'w'))
        time.sleep(1)
        
        volts = [0.5, 3.0, 6.0]
        voltlabels = ['05', '3', '6']
        freqs = [0.05, 0.1]
        freqlabels = ['005', '01']

        tint = 1   
        tf = 120 + tint
        
        for aa, A in enumerate(volts):
            for ff, freq in enumerate(freqs):

                print 'running test on', pstring
                print 'A =', A
                print 'freq =', freq

                time_savefile = output_dir + 'SQ' + SQs[pp] + 'overbiased_times_' + voltlabels[aa] +'_' + freqlabels[ff] + '_x.pkl'
                resp_savefile = output_dir + 'SQ' + SQs[pp] + 'overbiased_sinusoid_' + voltlabels[aa] +'_' + freqlabels[ff] + '_x.nc'
                #time_savefile = output_dir + 'tuned_times_' + voltlabels[aa] +'_' + freqlabels[ff] + '_z.pkl'
                #resp_savefile = output_dir + 'tuned_sinusoid_' + voltlabels[aa] +'_' + freqlabels[ff] + '_z.nc'
    

                
                helmholtz_test(driverfile, A, tint, tf, freq=freq, hwm_location=hwm_location)
                time.sleep(1)


