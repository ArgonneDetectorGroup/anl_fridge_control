from anl_fridge_control.analysis.analyze_GofT import *
import os
import pdb

def match_temps_drops(date, temps=[], drop_dirs=[], mezzmods=[], board='0137'):
    datafiles = {}
    for mm in mezzmods:
        datafiles[mm]={}
    for temp in temps:
        ix = temps.index(temp)
        for mm in mezzmods:
            datafiles[mm][temps[ix]]=os.path.join('/home/spt3g/output/2017/2017_07/20170725/w187_iv_vs_t/',drop_dirs[ix],'data','IceBoard_'+board+ '.Mezz_'+mm[0]+'.ReadoutModule_'+mm[1]+'_OUTPUT.pkl')
    return datafiles

def make_gparams(datafiles, rpars, mezzmods=[]):
    gparams = {}
    for mm in mezzmods:
        gparams[mm]={}
        gparams[mm]['name']='Mezz '+mm[0]+' Mod '+mm[1]
        fit_params, fit_errs, PsatVtemp = find_G_params(datafiles[mm],Rp=rpars)
        gparams[mm]['fit_params']=fit_params
        gparams[mm]['fit_errs']=fit_errs
        gparams[mm]['PsatVtemp']=PsatVtemp
    return gparams
