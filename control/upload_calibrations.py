import os, time
calfile_path='/home/spt3g/anl_fridge_control/control/thermo_calibrations'

##### For talking to LS 340 #######
import anl_fridge_control.lakeshore as LS
ChaseLS=LS.TempControl('/dev/ttyr18', ['A','B','C1','C2'])
curve_index=26   # IC Stage
thermo_serial='X98650'
thermo_series='CX-1030-CU'
curve_format='3'   # 1= mV/K, 2= V/K, 3= Ohms/K, 4= log10Ohm/K, 5=log10Ohm/log10K
curve_limit='325'   # curve temp limit in kelvin
curve_coefficient='1'  # 1=negative, 2=positive
calfile_path='/home/spt3g/anl_fridge_control/control/thermo_calibrations'

hdr_str='CRVHDR '+str(curve_index)+', '+thermo_series+', '+thermo_serial+','+curve_format+','+curve_limit+','+curve_coefficient+'\r\n'
ChaseLS.connex.write(hdr_str)
ChaseLS.connex.write('CRVHDR? '+str(curve_index)+'\r\n'); ChaseLS.connex.readline()

curve_data=np.loadtxt(os.path.join(calfile_path, thermo_serial+'.txt'),dtype=np.str)

temps=curve_data[:,0]
res=curve_data[:,1]


for ptindex in range(1,len(temps)+1):
    set_str='CRVPT '+str(curve_index)+', '+str(ptindex)+','+res[ptindex-1]+','+temps[ptindex-1]+'\r\n'
    ChaseLS.connex.write(set_str)
    time.sleep(2)

ChaseLS.connex.write('CRVSAV \r\n') # this hopefully helps with vanishing curves



##############################3
#Lakeshore 350
### to get the UC /IC thermos to work, they have to be log ohm/K

import socket
import numpy as np
tcp_interface=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcp_interface.connect(('10.10.10.217',7777))

upload_ic=False
upload_uc=False
configure_ic=False
configure_uc=False

if upload_ic:
    curve_index=26   # IC Stage                                                                                   
    thermo_serial='X98650'
    thermo_series='CX-1030-CU'
    curve_format='4'   # 1= mV/K, 2= V/K, 3= Ohms/K, 4= log10Ohm/K, 5=log10Ohm/log10K                             
    curve_limit='325'   # curve temp limit in kelvin                                                              
    curve_coefficient='1'  # 1=negative, 2=positive                                                               
    calfile_path='/home/spt3g/anl_fridge_control/control/thermo_calibrations'
    curve_data=np.loadtxt(os.path.join(calfile_path, thermo_serial+'.txt'),dtype=np.str)

    temps=curve_data[:,0]
    res=curve_data[:,1]
    #note this data is in ohms/K, so have to convert to log 
    res=np.float32(res)
    res_log=np.log10(res)
    hdr_str='CRVHDR '+str(curve_index)+', '+thermo_series+', '+thermo_serial+','+curve_format+','+curve_limit+','+curve_coefficient+'\r\n'

    tcp_interface.sendto(hdr_str+' \r\n',('10.10.10.217',7777))   # first setup the user curve header
    tcp_interface.sendto('CRVHDR? '+str(curve_index)+'\r\n',('10.10.10.217',7777)) # verify that the data is entered correctly
    data=tcp_interface.recvfrom(1024); print data
    # now enter the individual points in the calibration curve
    for ptindex in range(1,len(temps)+1):
        set_str='CRVPT '+str(curve_index)+', '+str(ptindex)+','+np.str(res_log[ptindex-1])+','+temps[ptindex-1]+'\r\n'
        tcp_interface.sendto(set_str+' \r\n',('10.10.10.217',7777))
        time.sleep(2)

if upload_uc:
    curve_index=22   # UC Stage                                                                                    
    thermo_serial='GR29933'
    thermo_series='GRT'
    curve_format='4'   # 1= mV/K, 2= V/K, 3= Ohms/K, 4= log10Ohm/K, 5=log10Ohm/log10K                              
    curve_limit='375'   # curve temp limit in kelvin                                                               
    curve_coefficient='1'  # 1=negative, 2=positive                                                                
    calfile_path='/home/spt3g/anl_fridge_control/control/thermo_calibrations'
    hdr_str='CRVHDR '+str(curve_index)+', '+thermo_series+', '+thermo_serial+','+curve_format+','+curve_limit+','+curve_coefficient+'\r\n'

    tcp_interface.sendto(hdr_str+' \r\n',('10.10.10.217',7777))   # first setup the user curve header
    tcp_interface.sendto('CRVHDR? '+str(curve_index)+'\r\n',('10.10.10.217',7777)) # verify that the data is entered correctly
    data=tcp_interface.recvfrom(1024); print data
    curve_data=np.loadtxt(os.path.join(calfile_path, thermo_serial+'.txt'),dtype=np.str)

    temps=curve_data[:,1]
    res=curve_data[:,0]

    #this data is already in logohms/K so no conversion is necessary
    # now enter the individual points in the calibration curve
    for ptindex in range(1,len(temps)+1):
        set_str='CRVPT '+str(curve_index)+', '+str(ptindex)+','+np.str(res[ptindex-1])+','+np.str(temps[ptindex-1])+'\r\n'
        tcp_interface.sendto(set_str+' \r\n',('10.10.10.217',7777))
        time.sleep(2)
        print np.str(res[ptindex-1])+','+temps[ptindex-1]

if upload_X83081:
    curve_index=23   # Cernox X83081
    thermo_serial='X83081'
    thermo_series='CX-1010-SD-HT-0.1L'
    curve_format='4'   # 1= mV/K, 2= V/K, 3= Ohms/K, 4= log10Ohm/K, 5=log10Ohm/log10K                              
    curve_limit='330'   # curve temp limit in kelvin                                                               
    curve_coefficient='1'  # 1=negative, 2=positive                                                                
    calfile_path='/home/spt3g/anl_fridge_control/control/thermo_calibrations'
    hdr_str='CRVHDR '+str(curve_index)+', '+thermo_series+', '+thermo_serial+','+curve_format+','+curve_limit+','+curve_coefficient+'\r\n'
    
    tcp_interface.sendto((hdr_str+' \r\n').encode(),('10.10.10.217',7777))   # first setup the user curve header
    tcp_interface.sendto(('CRVHDR? '+str(curve_index)+'\r\n').encode(),('10.10.10.217',7777)) # verify that the data is entered correctly
    data=tcp_interface.recvfrom(1024); print(data)
    curve_data=np.loadtxt(os.path.join(calfile_path, thermo_serial+'.dat'),dtype=np.str)

    temps=curve_data[2:,0]
    res=curve_data[2:,1]
    temps=np.float64(np.flipud(temps))
    res=np.flipud(res)
    #note this data is in ohms/K, so have to convert to log 
    res=np.float64(res)
    res_log=np.log10(res)
    temps=np.around(temps,5)
    res_log=np.around(res_log,5)
    
    # now enter the individual points in the calibration curve
    for ptindex in range(1,len(temps)+1):
        set_str='CRVPT '+str(curve_index)+', '+str(ptindex)+','+np.str(res_log[ptindex-1])+','+np.str(temps[ptindex-1])+'\r\n'
        tcp_interface.sendto((set_str+' \r\n').encode(),('10.10.10.217',7777))
        time.sleep(3)
        print(np.str(res_log[ptindex-1])+','+np.str(temps[ptindex-1]))     
        tcp_interface.sendto(('CRVPT? '+str(curve_index)+','+str(ptindex)+'\r\n').encode(),('10.10.10.217',7777))
        data=tcp_interface.recvfrom(1024); print(data)
        print('.')
        
if configure_ic:
    tcp_interface.sendto(b'INTYPE B,3,1,9,1,3,1\r\n',('10.10.10.217',7777))
    tcp_interface.sendto(b'INCRV B, 26\r\n',('10.10.10.217',7777))

if configure_uc:
    tcp_interface.sendto(b'INTYPE A,3,1,9,1,3,1\r\n',('10.10.10.217',7777))
    tcp_interface.sendto(b'INCRV A, 22\r\n',('10.10.10.217',7777))

if configure_X83081:
    tcp_interface.sendto(b'INTYPE A,3,1,9,1,3,1\r\n',('10.10.10.217',7777))
    tcp_interface.sendto(b'INCRV A, 23\r\n',('10.10.10.217',7777))
