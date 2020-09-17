# powersupply.py
#
# Python class for power supplies.

import serial
import time
import math
import re, pdb

class PowerSupply(object):

    def __init__(self, driver):
        driver_dict = self.driver_parser(driver)
        
        
        if driver_dict['parity']=='odd':
            parit=serial.PARITY_ODD
        if driver_dict['parity']=='none':
            parit=serial.PARITY_NONE
        if driver_dict['parity']=='even':
            parit=serial.PARITY_EVEN
        if driver_dict['stopbits']=='2':
            stopbit=serial.STOPBITS_TWO
        if driver_dict['bytesize']=='7':
            bytesiz=serial.SEVENBITS
        if driver_dict['bytesize']=='8':
            bytesiz=serial.EIGHTBITS
            
        
        
            
        self.serial_connex=serial.Serial(port=str(driver_dict['port']), baudrate=int(driver_dict['baudrate']), parity=parit, stopbits=stopbit, bytesize=bytesiz, timeout=float(driver_dict['timeout']))
        self.v_apply=str(driver_dict['v_apply'])
        self.v_ask=str(driver_dict['v_ask'])
        self.idn=str(driver_dict['idn'])
        self.term=driver_dict['term']
        self.output_on=str(driver_dict['output_on'])
        self.remote=str(driver_dict['remote'])
        self.select=str(driver_dict['select'])
        self.error_ask=str(driver_dict['error_ask'])
        self.vmin=float(driver_dict['vmin'])
        self.vmax=float(driver_dict['vmax'])
        self.sep=str(driver_dict['sep'])

    # Identification command
    def who_am_i(self):     
        self.serial_connex.write((self.idn + self.term).encode())       
        return self.serial_connex.readline().decode()
       
    # Set the power supply to operate remotely
    def remote_set(self):
        if self.remote is not 'None':
            self.serial_connex.write((self.remote + self.term).encode())
        else:
            pass

    # Ask the power supply for an error message
    def error(self):
        err_list=[]
        timeout = False
        while timeout is False:
            self.serial_connex.write((self.error_ask + self.term).encode())
            msg = self.serial_connex.readline().decode()
            if msg.find('No error')>-1:
                timeout = True
            err_list.append(msg)
        return err_list



    # Read voltages from the power supply
    def read_voltage(self):
        if self.select == 'None':
            self.serial_connex.write((self.v_ask+self.term).encode())
        else:
            self.serial_connex.write((self.select + self.sep + self.v_ask + self.term).encode())
        x = self.serial_connex.readline().decode()
        return x

    # Set voltages
    def set_voltage(self, voltage):
        if not (voltage>=self.vmin and voltage<=self.vmax):
            print('Voltage out of range!')
            return
        if self.output_on is not 'None':
            if self.select == 'None':
                self.serial_connex.write((self.output_on+self.term).encode())
            else:
                self.serial_connex.write((self.select + self.sep + self.output_on + self.term).encode())
        self.serial_connex.write((self.v_apply + ' ' + str(voltage) + self.term).encode())

    def set_vi(self,voltage,current):
        self.serial_connex.write((self.v_apply + ' ' + str(voltage) + ', ' + str(current) + self.term).encode())

    def driver_parser(self, driverfile):
        out = {}
        with open('/home/spt3g/anl_fridge_control/control/'+str(driverfile),'rb') as f:
            for line in f:
                try: #py2
                    listedline = line.strip().decode('unicode-escape').split('=')
                except: #py3
                    
                    #listedline = line.strip().split('=') #TODO: does not capture unicode-escape handling of '\', which messes up 'term' command

                    listedline=line.strip()
                    #print(listedline)
                    #pdb.set_trace()
                    listedline=re.split('=',listedline)
                    
                if len(listedline)>1:
                    out[listedline[0]] = listedline[1]
            f.close()
            #print(out)
            return out
