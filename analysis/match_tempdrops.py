from pydfmux.analysis.analyze_GofT import *

def match_temps_drops(date, temps=[], drop_dirs=[], mezzmods=[]):
    datafiles = {}
    for mm in mezzmods:
        datafiles[mm]={}
    for temp in temps:
        ix = temps.index(temp)
        for mm in mezzmods:
            datafiles[mm][temps[ix]]='/home/spt3g/output/'+str(date)+drop_dirs[ix]+'/data/IceBoard_0137.Mezz_'+mm[0]+'.ReadoutModule_'+mm[1]+'_OUTPUT.pkl'
    return datafiles

def make_gparams(datafiles, rpars, mezzmods=[]):
    gparams = {}
    for mm in mezzmods:
        gparams[mm]={}
        gparams[mm]['name']='Mezz '+mm[1]+' Mod '+mm[3]
        fit_params, fit_errs, PsatVtemp = find_G_params(datafiles[mm],Rp=rpars)
        gparams[mm]['fit_params']=fit_params
        gparams[mm]['fit_errs']=fit_errs
        gparams[mm]['PsatVtemp']=PsatVtemp
    return gparams
