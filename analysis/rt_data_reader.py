import matplotlib.pyplot as plt
import pickle
import tables
import numpy as np
import math,pdb,os
import scipy
from netCDF4 import Dataset
from pydfmux.core.utils.transferfunctions import convert_TF
import matplotlib.pyplot as plt
import pandas as pd
import pydfmux
import os
import yaml
import pdb



#flex_to_mezzmods = {'0137':{'w169':'21', 'w169_lc425a':'22'}, '0135':{'w169_lcnbberka':'24', 'w169_lcnbberkb':'23'}}
#flex_to_mezzmods={'0137':{'LC68.v4.b8.c6':'13','LC68.v4.b10.c12':'14','LC68.v4.b13.c8':'21','LC68.v4.b11.c8':'22'}}
#flex_to_mezzmods = {'0137':{'LC68.v4.b14.c5':'24'}}
#flex_to_mezzmods = {'0135':{{'LC68.v4.b14.c24':'13'}, {'LC68.v3.b4.c28':'12'},{'LC68.v3.v4.c26':'24'}, {'LC68.v4.b13.c22':'23'}}}
#flex_to_mezzmods = {'0135':{'LC68.v4.b14.c24':'13', 'LC68.v3.b4.c28':'12', 'LC68.v3.b4.c26':'24', 'LC68.v4.b14.c22':'23', 'LC68.v4.b14.c19':'11', 'LC68.v3.b4.c23':'14', 'LC68.v3.b4.c24':'22', 'LC68.v4.b14.c20':'21'}, '0137':{'LC68.v3.b4.c21':'24', 'LC68.v3.b6.c26':'21', 'LC68.v3.b6.c25':'11', 'LC68.v3.b4.c19':'14'}}
#flex_to_mezzmods = {'0137':{'SPTpol':'24'}}
#flex_to_mezzmods = {'0137':{'SPTpol1':'11', 'SPTpol2': '14', 'SPTpol3': '21', 'SPTpol4': '24'}
#flex_to_mezzmods = {'0137':{'LC68.v4.b10.c11':'24', 'LC68.v4.b13.c8':'21', 'LC68.v4.b11.c8':'22','LC68.v4.b10.c12':'14', 'LC68.v4.b8.c5':'12'}}
#flex_to_mezzmods = {'0137':{'LC68.v4.b10.c11':24', 'LC68.v4.b13.c8':'21', 'LC68.v4.b11.c8':'22','LC68.v4.b10.c12':'14', 'LC68.v4.b8.c5':'12', 'LC68.v4.13.c16':'11', 'LC68.v4.b8.c6':'13', 'LC68.v4.b13.c16':'23'}}
#flex_to_mezzmods = {'0135':{'LC68.v4.b10.c11':'24', 'LC68.v4.b11.c8':'22', 'LC68.v4.b8.c5':'12'}}
#flex_to_mezzmods = {'0135':{'LC68.v3.b6.c27':'11'}}
#flex_to_mezzmods = {'0137':{'LC68.v4.b13.c8':'21'}}
#flex_to_mezzmods = {'0137':{'LC68.v4.b10.c11':'24', 'LC68.v4.b13.c8':'21', 'LC68.v4.b11.c8':'22','LC68.v4.b10.c12':'14', 'LC68.v4.b8.c5':'12', 'LC68.v4.13.c16':'11', 'LC68.v4.b8.c6':'13', 'LC68.v4.b13.c16':'23'}}



def make_cfp_dict(flex_to_mezzmods=None, overbias_dir=None, gain=0, drop_dir=None, skip_dropped=False):
    

    '''
    Makes a dictionary of calibration factors mapped to bolometer name.

    overbias_dir: the full path to the directory containing overbias files.  Ends with 'data/'
    board: the iceboard you are looking at
    '''

    cfp_dict = {}


    for board in flex_to_mezzmods:
        for fc in flex_to_mezzmods[board]:
            if overbias_dir:
                f=open(overbias_dir+'/data/IceBoard_'+str(board)+'.Mezz_'+flex_to_mezzmods[board][fc][0]+'.ReadoutModule_'+flex_to_mezzmods[board][fc][1]+'_OUTPUT.pkl', 'r')
            if drop_dir:
                f=open(drop_dir+'/data/IceBoard_'+str(board)+'.Mezz_'+flex_to_mezzmods[board][fc][0]+'.ReadoutModule_'+flex_to_mezzmods[board][fc][1]+'_OUTPUT.pkl', 'r')
            ob = pickle.load(f)
            f.close()

            for ix in ob['subtargets']:

                # option to skip channels that did not overbias
                if skip_dropped:
                    if overbias_dir:
                        if ix not in ob['overbiased'].keys():
                            continue
                    if drop_dir:
                        if ob['subtargets'][ix]['state'] != 'tuned':
                            continue

                freq = ob['subtargets'][ix]['frequency']
                bolo = ob['subtargets'][ix]['bolometer'].replace('_', '/') # hopefully works? -AHHH
                cfp = convert_TF(gain, 'nuller', unit='RAW', frequency=freq)
                cfp_dict[bolo] = cfp

    return cfp_dict


def load_times(time_pkl):
    '''
    Loads in the start and end times to find the right place in the logfile.

    time_pkl: the pickle of starttime and endtime produced at the end of take_rt_mini.py
    '''
    f=open(time_pkl, 'r')
    start_end = pickle.load(f)
    f.close()

    starttime = start_end['starttime']
    endtime = start_end['endtime']

    return starttime, endtime

def read_temps(tempfile, starttime, endtime, sensor='UC Stage'):
    '''
    Reads temperature data from the logfile.

    tempfile: The logfile used when taking the R(T) data
    starttime: Output of load_times()
    endtime: Output of load_times()
    sensor: The correct item in the logfile (usually UC Head)
    '''
    dataread = tables.open_file(tempfile, 'r')
    datatable = dataread.get_node('/data/' + sensor.replace(' ', '_'))

    temp_vals = [row[sensor] for row in datatable.iterrows() if row['time'] > starttime-1 and row['time'] < endtime+1]
    time_vals = [row['time'] for row in datatable.iterrows() if row['time'] > starttime-1 and row['time'] < endtime+1]

    dataread.close()

    return temp_vals, time_vals


def read_netcdf(ledgerman_filename,cfp_dict=[]):
    '''
    Read in the ledgerman data and separate data into i and q components.

    ledgerman_filename: the .nc file output by ledgerman when take_rt_mini is run
    cfp_dict: dictionary of calibration factors from make_cfp_dict()

    # non-downsampling reader function added 20180423, AHHH
    '''
    data=Dataset(ledgerman_filename,'r',format='NETCDF4')
    datavars=[var.rstrip('_I') for var in data.variables if '_I' in var]

    time_sec=data.variables['Time']
    time_sec=time_sec-time_sec[0]

    data_i={}
    data_q={}
    for var in datavars:
        i_comp=data.variables[var+'_I']
        q_comp=data.variables[var+'_Q']

        if str(var) in cfp_dict.keys():
            data_i[var]=i_comp*cfp_dict[str(var)]#cal_factor_pa
            data_q[var]=q_comp*cfp_dict[str(var)]#cal_factor_pa
            
        elif str(var).replace('_','/') in cfp_dict.keys():
            data_i[var]=i_comp*cfp_dict[str(var).replace('_','/')]#cal_factor_pa
            data_q[var]=q_comp*cfp_dict[str(var).replace('_','/')]#cal_factor_pa

    return data_i, data_q, time_sec



def read_netcdf_fast(ledgerman_filename,cfp_dict=[]):
    '''
    Read in the ledgerman data and separate data into i and q components.

    ledgerman_filename: the .nc file output by ledgerman when take_rt_mini is run
    cfp_dict: dictionary of calibration factors from make_cfp_dict()
    '''
    data=Dataset(ledgerman_filename,'r',format='NETCDF4')
    datavars=[var.rstrip('_I') for var in data.variables if '_I' in var]

    ixs = np.arange(len(data.variables['Time']), step=215)

    time_sec=data.variables['Time'][ixs]
    time_sec=time_sec-time_sec[0]

    data_i={}
    data_q={}
    for var in datavars:
        i_comp=data.variables[var+'_I'][ixs]
        q_comp=data.variables[var+'_Q'][ixs]

        if str(var) in cfp_dict.keys():
            data_i[var]=i_comp*cfp_dict[str(var)]#cal_factor_pa
            data_q[var]=q_comp*cfp_dict[str(var)]#cal_factor_pa

        elif str(var).replace('_','/') in cfp_dict.keys():
            data_i[var]=i_comp*cfp_dict[str(var).replace('_','/')]#cal_factor_pa
            data_q[var]=q_comp*cfp_dict[str(var).replace('_','/')]#cal_factor_pa

    return data_i, data_q, time_sec


def model_temps(temp_vals, time_vals):
    '''
    Makes a function modeling the relationship between time and temperature

    temp_vals: Output of read_temps
    time_vals: Output of read_temps
    '''
    new_time_vals = np.array(time_vals)-time_vals[0] #shift the times to start from 0
    tempfit = scipy.interpolate.interp1d(new_time_vals, temp_vals)
    return tempfit

def downsample_data(time_sec, data_i, data_q, tempfit, add_type):
    '''
    Cuts the data down to help with transfer, and adds the i and q components in quadrature.

    time_sec: Output of read_netcdf_fast()
    data_i: Output of read_netcdf_fast()
    data_q: Output of read_netcdf_fast()
    tempfit: Output of model_temps()
    add_type: choose from 'quadrature', 'I', 'Q'
    '''
    #time_sec[-16]=time_sec[-17]
    interp_temps = tempfit(time_sec[0:-15]) 

    ixs = []
    ix0 = 0
    while ix0 < len(time_sec)-1: 
        ixs.append(ix0)
        ix0 += 1
    ixs.remove(ixs[-1])
    ds_data = dict()
    for key in data_i.keys():
        ds_data[key] = []
        for ix in ixs:
            if add_type=='quadrature':
                ds_data[key].append(math.sqrt(data_i[key][ix]**2+data_q[key][ix]**2))
            elif add_type=='I':
                ds_data[key].append(data_i[key][ix])
            elif add_type=='Q':
                ds_data[key].append(data_q[key][ix])
    ds_temps = []
    for ix in ixs:
        ds_temps.append(interp_temps[ix])

    return ds_temps, ds_data

def pickle_data(ds_temps, data_r, filename):
    '''
    Pickles the final data to be saved and transferred

    ds_temps: Output of downsample_data()
    data_r: Output of convert_i2r()
    filename: The file you want to write this information to
    '''
    f=open(filename, 'w')
    pickle.dump({"temps":ds_temps, "data":data_r}, f)
    f.close()

def convert_i2r(ds_data, board, overbias_dir, flex_to_mezzmods):
    '''
    converts current magnitudes (calculated from ledgerman i and q) into resistances using the voltage from overbias_and_null

    '''
    
    data_r = dict()
    for fc in flex_to_mezzmods[board]: #for each LC chip
        f=open(os.path.join(overbias_dir,'data','IceBoard_'+str(board)+'.Mezz_'+flex_to_mezzmods[board][fc][0]+'.ReadoutModule_'+flex_to_mezzmods[board][fc][1]+'_OUTPUT.pkl'), 'r') #open the overbias_and_null data for the matching mezzanine and module
        ob = pickle.load(f)
        f.close()
        
        for ky in ds_data: #for each bolometer in ds_data
            for chan in ob['subtargets'].keys(): #for each LC channel in the HWM
                if ob['subtargets'][chan]['bolometer'].replace('/','_')==str(ky): #look until you find the bolo that matches the one in ds_data
                    ds_div=[]
                    for point in ds_data[ky]: #for each data point (signal magnitude) 
                        if chan in ob['overbiased'].keys(): #if that bolo was actually overbiased
                            ds_div.append(ob['overbiased'][chan]['V']/point) #overbias voltage / ledgerman magnitude = R
                    data_r[ky] = ds_div

    return data_r

def make_data_dict(data_r):
	data_dict = {}
	for bolo in data_r.keys():
		if data_r[bolo] != []:
			data_dict[str(bolo)] = {}
	return data_dict

def find_r_total(data_r, ds_temps, temp_min, data_dict):
	for bolo in data_dict.keys():
		rnorms = []
		for ix in range(len(ds_temps)):
			if ds_temps[ix] > float(temp_min):
				rnorms.append(data_r[bolo][ix])
                rnorms = [res for res in rnorms if res != np.inf and res!= np.nan] # check for infs, nans

                rnorm_mean = np.mean(rnorms)
                data_dict[bolo]['rnormal'] = rnorm_mean

        return data_dict


def find_r_parasitic(data_r, ds_temps, temp_range, data_dict):
	for bolo in data_dict.keys():
		rpars = []
		for ix in range(len(ds_temps)):
			if float(temp_range[0]) < ds_temps[ix] < float(temp_range[1]):
				rpars.append(data_r[bolo][ix])
                rpars = [res for res in rpars if res != np.inf and res!= np.nan] # check for infs, nans

                rpars_mean = np.mean(rpars)
                data_dict[bolo]['rpar'] = rpars_mean
	return data_dict




def plot_each_bolo(ds_temps, data_r, data_dict):

    bad_bolos=[]
    for bolo in data_dict.keys():
        plt.clf()                                      
        plt.plot(ds_temps, data_r[bolo], color='C0')   
        plt.axhline(data_dict[bolo]['rnormal'], color='C2')
        plt.axhline(data_dict[bolo]['rpar'], color='r')
        plt.title(str(bolo))
        plt.ylabel('Resistance ($\Omega$)')
        plt.xlabel('Temperature (K)')
        plt.show()
        plt.pause(0.01)
        kstr=raw_input('is bolo good? ')
        if kstr =='n':
            bad_bolos.append(bolo)
    return bad_bolos


def find_tc(data_r, ds_temps, temp_range, data_dict, bad_bolos):
    for bolo in data_dict.keys():
        if bolo not in bad_bolos:
            points = []
            for ix in range(len(ds_temps)):
                if float(temp_range[0]) < ds_temps[ix] < float(temp_range[1]):
                    if 1.2*float(data_dict[bolo]['rpar']) < data_r[bolo][ix] < 0.9*float(data_dict[bolo]['rnormal']):
                        points.append(ds_temps[ix])

        try:
            data_dict[bolo]['tc']=np.mean(points)
        except:
            data_dict[bolo]['tc']=np.nan
    return data_dict

def tc_plots(ds_temps, data_r, data_dict, bad_bolos):
    for bolo in data_dict.keys():
        if bolo not in bad_bolos:
            if data_dict[bolo]['tc']!=np.nan:
                plt.clf()
                plt.plot(ds_temps, data_r[bolo], color='C0')
                plt.axhline(data_dict[bolo]['rnormal'], color='C2')
                plt.axhline(data_dict[bolo]['rpar'], color='r')
                plt.axvline(data_dict[bolo]['tc'], color='C3')
                plt.title(str(bolo))
                plt.ylabel('Resistance ($\Omega$)')
                plt.xlabel('Temperature (K)')
                plt.show()
            elif data_dict[bolo]['tc']==np.nan:
                plt.clf()
                plt.plot(ds_temps, data_r[bolo], color='C0')
                plt.axhline(data_dict[bolo]['rnormal'], color='C2')
                plt.axhline(data_dict[bolo]['rpar'], color='r')
                plt.title(str(bolo))
                plt.ylabel('Resistance ($\Omega$)')
                plt.xlabel('Temperature (K)')
                plt.show()



def get_bolo_info(wafer_file,data_dict):
    bolos=data_dict.keys()
    wafer_info=pd.read_csv(wafer_file,sep='\t')
    for bb in bolos:
        search_str={'name':[bb.split('_')[1]]}
        tmp_search=wafer_info.isin(search_str)
        rowkey=wafer_info[tmp_search['name']].index[0]
        data_dict[bb]['band']=wafer_info['observing_band'][rowkey]
    return data_dict
