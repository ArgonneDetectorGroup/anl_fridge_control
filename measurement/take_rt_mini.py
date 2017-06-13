import anl_fridge_control.control.serial_connections as sc
import he10_fridge_control.control.gettemp as gt
import pydfmux
import time
import datetime
import subprocess
import pickle


PID_high_temp = 0.650
PID_low_temp = 0.400
#sleeptime = 60

logfile = '/home/spt3g/he10_logs/log03302017b_read.h5'

ledgerman_path = '/home/spt3g/spt3g_software/dfmux/bin/ledgerman.py'
data_dir = '/home/spt3g/output/20170518/'
R_data_path = data_dir + 'test_0135.nc'
#R_data_path_0135 = data_dir + 'rt0135.nc'

hwm = '/home/spt3g/hardware_maps/hwm_anl_04122017_w169/hwm_m2m1.yaml'
#hwm_0135 = '/home/spt3g/hardware_maps/hwm_anl_20170306_W169_and_Rboards/hwm_0135.yml'

#sc.ChaseLS.set_heater_range(2)
#sc.ChaseLS.set_PID_temp(1, PID_high_temp)

#while float(gt.gettemp(logfile, 'UC Head'))<0.650:
#while float(gt.gettemp(logfile, 'UC Head'))<PID_low_temp:
#	print "UC Head temp is " + str(gt.gettemp(logfile, 'UC Head'))
#	time.sleep(10)
def direction():
    upordown=raw_input('Upward sweep or downward sweep? ')
    if upordown in ['up', 'Up', 'UP', 'upward', 'UPWARD']:
        upward_sweep(PID_high_temp)
    elif upordown in ['down', 'Down', 'DOWN', 'downward', 'DOWNWARD']:
        downward_sweep(PID_low_temp)

def upward_sweep(hightemp):
    print 'Running an upward sweep'
    starttime = time.time()
    print "start time: " + str(starttime)

    proc_ledgerman = subprocess.Popen(['python', ledgerman_path, hwm, R_data_path, '-s'])
#proc_ledgerman_0135 = subprocess.Popen(['python', ledgerman_path, hwm_0135, R_data_path_0135, '-s'])

#settemp = PID_high_temp

#while settemp > PID_low_temp:
#    sc.ChaseLS.set_PID_temp(1, settemp)
#    time.sleep(sleeptime)
#    settemp -= 0.010

#while float(gt.gettemp(logfile, 'UC Head'))>0.420:
#	time.sleep(10)

#sc.ChaseLS.set_PID_temp(1, 0.000)
#time.sleep(1)
#sc.ChaseLS.set_heater_range(0)

    while float(gt.gettemp(logfile, 'UC Head'))<hightemp:
        time.sleep(10)

#time.sleep(60)

    proc_ledgerman.terminate()
#proc_ledgerman_0135.terminate()

    endtime=time.time()
    print "end time: " + str(endtime)

    startendtime = {'start_time':starttime, 'end_time':endtime}
    f=open(data_dir + 'rt_m2m1_times.pkl', 'w')
    pickle.dump(startendtime, f)
    f.close()

def downward_sweep(lowtemp):
    print 'Running a downward sweep'
    starttime = time.time()
    print "start time: " + str(starttime)

    proc_ledgerman = subprocess.Popen(['python', ledgerman_path, hwm, R_data_path, '-s'])

    while float(gt.gettemp(logfile, 'UC Head'))>lowtemp:
        time.sleep(10)

    proc_ledgerman.terminate()

    endtime=time.time()
    print "end time: " + str(endtime)

    startendtime = {'start_time':starttime, 'end_time':endtime}
    f=open(data_dir + 'rt_m2m1_up_times.pkl', 'w')
    pickle.dump(startendtime, f)
    f.close()

if __name__=='__main__':
    direction()
