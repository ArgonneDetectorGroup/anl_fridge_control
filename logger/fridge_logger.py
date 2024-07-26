# fridge_logger.py
#
# A logging script for the ANL fridge that records temperatures. The data is
# saved in a text file (or perhaps hdf5 file in the future) and can be accessed
# later by the plotting script or the fridge control script when it performs
# an automatic fridge cycle.
#
# Original code by:
# Adam Anderson
# adama@fnal.gov
# 12 September 2015
#
# Modified heavily by:
# Faustin Carter
# Feb. 4, 2016

import serial
import time
import numpy as np
import tables
import os.path
import shutil
import socket
import plotter
import pdb


# BASIC CONFIGURATION
# Specify mapping of {"interface" -> [list of channels]} here. The "interface"
# is simply the serial interface or IP address of the Lakeshore box.
# List of channels contains tuple of (channel name, channel number)
channel_map = {'/dev/ttyr13':   [('He4 IC Switch',  '1'),
                                 ('He3 IC Switch',  '2'),
                                 ('He3 UC Pump',    '3'),
                                 ('He3 UC Switch',  '4'),
                                 ('He3 IC Pump',    '5'),
                                 ('mainplate',      '6'),
                                 ('HEX',            '7'),
                                 ('He4 IC Pump',    '8')],

               '/dev/ttyr18':   [('UC Stage',        'A'),
                                 ('IC Stage',        'B'),
                                 ('PTC 50K Plate',  'C2'),
                                 ('PTC 4K Plate',   'C1'),
                                 ('4K Plate D1',       'D1'),
                                 ('SQUID D2',       'D2')],
               '10.10.10.217': [('4K Plate CX','A')]}
                                #('UC Stage','A'),
                                #('IC Stage','B')


# Specify the variables to be plotted in each subplot of the display. This
# should be a list of lists of (1 or 2) lists of strings, where each outer list contains the variables
# contained in one subplot, the collections of 1 or 2 lists indicated whether
# one or two y-axis scales should be used, and the variable names in the
# final lists are the names from 'channel_map' above which should be mapped to
# each y-axis scale.
plot_list = [[['He4 IC Pump', 'He3 IC Pump', 'He3 UC Pump'],
                ['He4 IC Switch', 'He3 IC Switch', 'He3 UC Switch']],
             [['HEX', 'mainplate']],
             [['PTC 4K Plate'], ['PTC 50K Plate']],
             [['UC Stage', 'IC Stage']],
             [['4K Plate D1', 'SQUID D2', '4K Plate CX']],
             [['IC Stage'], ['UC Stage']]]

# update frequency
dt_update = 2  # sec

base_path = os.path.dirname(os.path.abspath(__file__))

# convenience functions for adding and removing underscores
def underscoreify(string):
    return string.replace(' ', '_')
def deunderscoreify(string):
    return string.replace('_', ' ')

#A handy function to read one temperature point from one channel.
#This is less efficient than reading all channels at once, but much easier
#to recover from when something goes wrong.
def read_temp_LS(interface, channel, num_trys = 10, delay = 0.1):
    """First attempt at making a reader that does a little bit of data validation"""
    for num in range(num_trys):
        #flush the I/O buffers
        interface.flushInput()
        interface.flushOutput()

        #Ask for the temperature
        interface.write(('KRDG? ' + channel + '\r\n').encode())

        #Wait a hot tenth of a second
        time.sleep(delay)

        #Read all the bytes that are at the port
        raw_output = interface.read(interface.inWaiting())
        if type(raw_output)==bytes:
            raw_output=raw_output.decode('utf-8')
        
        #Check that the string ends with the terminator. If not, try again
        if raw_output[-2:] == '\r\n':
            #If the data is bad or incomplete, float conversion may fail
            try:
                #Strip off the term char (usually '\r\n'))
                #and convert to float
                temp = float(raw_output.strip())
            except ValueError:
                pass
            else:
                return temp

        #Welp, that didn't work, try again!
        print('Problem reading from: ' + interface.name + ':' + channel)
        print('Raw output is: ' + repr(raw_output))
        print('Will try ' + str(num_trys - 1 - num) + ' more times before aborting.')
        time.sleep(delay)

    raise NameError("Lost communication with: " + interface)

# file name
data_filename = input('Enter relative path to data file (must end in .h5, and should include no dots except the one in .h5). NB: If enter an existing filename, the script will attempt to append that file, by default: ')
if os.path.isfile(data_filename) == True:
    print(data_filename + ' already exists. Attempting to append data to end of file. If thermometer names differ in the existing file, this may fail.')
    pytables_mode = 'a'
else:
    print('Attempting to create data file ' + data_filename)
    pytables_mode = 'w'

# create output file
f_h5 = tables.open_file(data_filename, mode=pytables_mode, title='fridge data') # append file, by default
try:
    group_all_data = f_h5.get_node('/data')
except tables.NoSuchNodeError:
    group_all_data = f_h5.create_group('/', 'data', 'all data')
tables_list = dict()

for interface in channel_map:
    for channel_name, channel_num in channel_map[interface]:
        try:
            # try pulling table from the file, which should work if it exists
            tables_list[channel_name] = f_h5.get_node('/data/' + underscoreify(channel_name))
        except tables.NoSuchNodeError:
            # otherwise, the file presumably doesn't exist and we need new tables
            table_columns = {'time': tables.Time32Col(), channel_name: tables.Float32Col()}
            tables_list[channel_name] = f_h5.create_table(group_all_data, underscoreify(channel_name), table_columns, channel_name)
        print(channel_name)

serial_interface_address = [name for name in channel_map.keys() if '/dev' in name]
tcp_interface_address = [name for name in channel_map.keys() if '10.10' in name]

# check that we didn't miss interfaces in the split
if set(serial_interface_address + tcp_interface_address) != set(channel_map.keys()):
    print("WARNING: Could not parse all interface addresses as either serial or TCP. " + \
          "Some devices may not be read!")


# set up the serial interfaces
serial_interfaces = dict()
#for interface_address in channel_map.keys():
for interface_address in serial_interface_address:
    serial_interfaces[interface_address] = serial.Serial(port=interface_address,
                                                         baudrate=9600,
                                                         bytesize=serial.SEVENBITS,
                                                         parity=serial.PARITY_ODD,
                                                         stopbits=serial.STOPBITS_ONE)
                       
tcp_interfaces = dict()
for interface_address in tcp_interface_address:
    tcp_interfaces[interface_address] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_interfaces[interface_address].connect((interface_address, 7777))
    tcp_interfaces[interface_address].settimeout(1.0)


# main data acquisition loop
try:
    while True:
        current_time = time.time()
        for interface_address, serial_interface in serial_interfaces.items():
            for channel_name, channel_num in channel_map[interface_address]:
                #Fill up the columns of a table row with data
                tables_list[channel_name].row[channel_name] = read_temp_LS(serial_interface, channel_num)
                tables_list[channel_name].row['time'] = current_time

                #Send data to I/O buffer
                tables_list[channel_name].row.append()

                #Write data to disk and clear buffer
                tables_list[channel_name].flush()

        
        for interface_address in tcp_interfaces:
            tcp_interfaces[interface_address].sendto(('KRDG? 0\r\n').encode(), (interface_address, 7777))
        # wait for devices to issue a response
        time.sleep(0.1)
        raw_output_temp = dict()
        
        for interface_address in tcp_interfaces:
            tmp_data=tcp_interfaces[interface_address].recvfrom(2048)
            
            raw_output_temp[interface_address]=tmp_data[0]
            if type(raw_output_temp[interface_address])==bytes: #py3 compatibility
                raw_output_temp[interface_address]=raw_output_temp[interface_address].decode('utf-8')
  
            
            for jValue in range(len(channel_map[interface_address])):
                channel_name=channel_map[interface_address][jValue][0]
                tables_list[channel_name].row[channel_name]=float(raw_output_temp[interface_address].split(',')[jValue])        
                tables_list[channel_name].row['time'] = current_time
                tables_list[channel_name].row.append()
                tables_list[channel_name].flush()

        # update the plots
        plotter.update_plot(base_path + '/../website/img/temperature_plot.png' ,tables_list, plot_list)
        plotter.write_table(base_path + '/../website/datatable.html', tables_list, plot_list)

        # make a copy of the data file; useful for other processes that need
        # access to the latest data since we cannot do simultaneous read/write
        # of pytables files
        shutil.copyfile(data_filename, data_filename + str('.lock'))
        shutil.move(data_filename + str('.lock'), data_filename.split('.')[-2] + '_read.h5')

        # wait before reading again
        time.sleep(dt_update)

except KeyboardInterrupt:
    print("\nStopping data acquisition")

# close the connections
for interface_address in serial_interface_address:
    serial_interfaces[interface_address].close()

