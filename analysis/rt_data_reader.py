import pickle
import tables
import numpy as np
import math
import scipy
from netCDF4 import Dataset
from pydfmux.core.utils.transferfunctions import convert_TF


#def make_ob_dict(overbias_dir):

flex_to_mezzmods = {'0137':{'w169':'21', 'w169_lc425a':'22', 'w169_lc433a':'14'}}

def make_cfp_dict(overbias_dir):
    '''
    Makes a dictionary of calibration factors mapped to bolometer name.

    overbias_dir: the full path to the directory containing overbias files.  Ends with 'data/'
    board: the iceboard you are looking at
    '''
    cfp_dict = {}
    for board in flex_to_mezzmods:
        for fc in flex_to_mezzmods[board]:
            f=open(overbias_dir+'IceBoard_'+str(board)+'.Mezz_'+flex_to_mezzmods[board][fc][0]+'.ReadoutModule_'+flex_to_mezzmods[board][fc][1]+'_OUTPUT.pkl', 'r')
            ob = pickle.load(f)
            f.close()

            for ix in ob['subtargets']:
                freq = ob['subtargets'][ix]['frequency']
                bolo = ob['subtargets'][ix]['bolometer']
                cfp = convert_TF(15, 'nuller', unit='RAW', frequency=freq)
                cfp_dict[bolo] = cfp
    return cfp_dict

#cfp = convert_TF(15, 'carrier',unit='RAW')

def load_times(time_pkl):
    '''
    Loads in the start and end times to find the right place in the logfile.

    time_pkl: the pickle of starttime and endtime produced at the end of take_rt_mini.py
    '''
    f=open(time_pkl, 'r')
    start_end = pickle.load(f)
    f.close()

    starttime = start_end['start_time']
    endtime = start_end['end_time']

    return starttime, endtime

def read_temps(tempfile, starttime, endtime, sensor='UC Head'):
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

        data_i[var]=i_comp*cfp_dict[str(var).replace('_','/')]#cal_factor_pa
        data_q[var]=q_comp*cfp_dict[str(var).replace('_','/')]#cal_factor_pa

    return data_i, data_q, time_sec


def model_temps(temp_vals, time_vals):
    '''
    Makes a function modeling the relationship between time and temperature

    temp_vals: Output of read_temps
    time_vals: Output of read_temps
    '''
    new_time_vals = np.array(time_vals)-time_vals[0]
    tempfit = scipy.interpolate.interp1d(new_time_vals, temp_vals)
    return tempfit

def downsample_data(time_sec, data_i, data_q, tempfit):
    '''
    Cuts the data down to help with transfer, and adds the i and q components in quadrature.

    time_sec: Output of read_netcdf_fast()
    data_i: Output of read_netcdf_fast()
    data_q: Output of read_netcdf_fast()
    tempfit: Output of model_temps()
    '''
    interp_temps = tempfit(time_sec[0:-3])

    ixs = []
    ix0 = 0
    while ix0 < len(time_sec):
        ixs.append(ix0)
        ix0 += 2
    ixs.remove(ixs[-1])
    ds_data = dict()
    for key in data_i.keys():
        ds_data[key] = []
        for ix in ixs:
            ds_data[key].append(math.sqrt(data_i[key][ix]**2+data_q[key][ix]**2))
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
    pickle.dump({"temps":ds_temps, "data":ds_data}, f)
    f.close()

def convert_i2r(ds_data, board, overbias_dir):
    data_r = dict()
    for fc in flex_to_mezzmods[board]:
        f=open(overbias_dir+'IceBoard_'+str(board)+'.Mezz_'+flex_to_mezzmods[board][fc][0]+'.ReadoutModule_'+flex_to_mezzmods[board][fc][1]+'_OUTPUT.pkl', 'r')
        ob = pickle.load(f)
        f.close()

        for ky in ds_data:
            for key in ob['subtargets'].keys():
                if ob['subtargets'][key]['bolometer'].replace('/','_')==str(ky):
                    ds_div=[]
                    for point in ds_data[ky]:
                        if key in ob['overbiased'].keys():
                            ds_div.append(ob['overbiased'][key]['V']/point)
                    data_r[ky] = ds_div

    return data_r

def make_data_dict(data_r):
	data_dict = {}
	for bolo in data_r.keys():
		if data_r[bolo] != []:
			data_dict[str(bolo)] = {}
	return data_dict

def find_r_normal(data_r, ds_temps, temp_min, data_dict):
	for bolo in data_dict.keys():
		rnorms = []
		for ix in range(len(ds_temps)):
			if ds_temps[ix] > float(temp_min):
				rnorms.append(data_r[bolo][ix])
		rnorm_mean = mean(rnorms)
		data_dict[bolo]['rnormal'] = rnorm_mean
	return data_dict

def find_r_parasitic(data_r, ds_temps, temp_range, data_dict):
	for bolo in data_dict.keys():
		rpars = []
		for ix in range(len(ds_temps)):
			if float(temp_range[0]) < ds_temps[ix] < float(temp_range[1]):
				rpars.append(data_r[bolo][ix])
		rpars_mean = mean(rpars)
		data_dict[bolo]['rpar'] = rpars_mean
	return data_dict

bad_bolos = []
def plot_each_bolo(ds_temps, data_r, data_dict):
	for bolo in data_dict.keys():
		plt.figure()
		plt.plot(ds_temps, data_r[bolo], color='C0')
		plt.axhline(data_dict[bolo]['rnormal'], color='C2')
		plt.axhline(data_dict[bolo]['rpar'], color='C2')
		plt.title(str(bolo))
		plt.ylabel('Resistance ($\Omega$)')
		plt.xlabel('Temperature (K)')
		plt.show()

def find_tc(data_r, ds_temps, temp_range, data_dict):
    for bolo in data_dict.keys():
        if bolo not in bad_bolos:
            points = []
            for ix in range(len(ds_temps)):
                if float(temp_range[0]) < ds_temps[ix] < float(temp_range[1]):
                    if 1.2*float(data_dict[bolo]['rpar']) < data_r[bolo][ix] < 0.9*float(data_dict[bolo]['rnormal']):
                        points.append(ds_temps[ix])
        try:
            data_dict[bolo]['tc']=mean(points)
        except:
            print bolo
    return data_dict

def tc_plots(ds_temps, data_r, data_dict):
    for bolo in data_dict.keys():
        if bolo not in bad_bolos:
            plt.figure()
            plt.plot(ds_temps, data_r[bolo], color='C0')
            plt.axhline(data_dict[bolo]['rnormal'], color='C2')
            plt.axhline(data_dict[bolo]['rpar'], color='C2')
            plt.axvline(data_dict[bolo]['tc'], color='C3')
            plt.title(str(bolo))
            plt.ylabel('Resistance ($\Omega$)')
            plt.xlabel('Temperature (K)')
            plt.show()
