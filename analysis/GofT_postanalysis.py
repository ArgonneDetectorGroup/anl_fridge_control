# GofT_postanalysis.py


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import os,pdb,pickle

'''
Before running any of these codes, run the analyze_GofT
codes to get the G parameters.  You need to start with
a gparams dictionary indexed by mezzmod.

gparams = {'m1m4':{'name','PsatVtemp','fit_params','fit_errs'}}
'''



def make_param_dict(gparams,physical_name=False,hwm_wafer_file=''):
    params={}
    if not physical_name:
        wafer_mapping=pd.read_csv(hwm_wafer_file,sep='\t')
    for mezzmod in gparams:
        
        for bolo in gparams[mezzmod]['PsatVtemp']:
            fullname=gparams[mezzmod]['PsatVtemp'][bolo]['name']
            if bolo in gparams[mezzmod]['fit_params']:
                k = gparams[mezzmod]['fit_params'][bolo][0]
                tc = gparams[mezzmod]['fit_params'][bolo][1]
                n = gparams[mezzmod]['fit_params'][bolo][2]
                G = n*k*(tc**(n-1))
#                pdb.set_trace()

                if physical_name:
                
                    params[bolo]={'k':k*1e12, 'k_units':'pW/K^n', 'tc':tc*1e3, 'tc_units':'mK', 'n':n, 'band':bolo.split('.')[-2], 'G':G*1e12, 'G_units':'pW/K'}

                else:
#                    fullname=bolo.split('/')[-1]
                    search_str={'name':[fullname]}

                    tmp_search=wafer_mapping.isin(search_str)
                    row_key=wafer_mapping[tmp_search['name']].index
#                    pdb.set_trace()
                    params[fullname]={'k':k*1e12, 'k_units':'pW/K^n', 'tc':tc*1e3, 'tc_units':'mK', 'n':n, 'band':np.str(np.int32(wafer_mapping['observing_band'][row_key].values[0])), 'G':G*1e12, 'G_units':'pW/K','physical_name':wafer_mapping['physical_name'][row_key].values[0]}

#                    params[fullname]={'k':k*1e12, 'k_units':'pW/K^n', 'tc':tc*1e3, 'tc_units':'mK', 'n':n, 'band':np.str(np.int32(gparams[mezzmod]['PsatVtemp'][bolo]['name'].split('.')[-2])), 'G':G*1e12, 'G_units':'pW/K','physical_name':wafer_mapping['physical_name'][row_key].values[0]}  

                psat300 = k*(tc**n - 0.300**n)
                params[fullname]['psat300'] = psat300*1e12
                params[fullname]['psat_units']='pW'
                params[fullname]['pstring']=mezzmod[0]+'/'+mezzmod[1]+'/'+str(bolo)
    return params

def param_triangle(params, wafernumber):
    fig = plt.figure(figsize=(60,60))
    plt.suptitle('Wafer %s G Parameters'%(wafernumber), fontsize=40, weight='bold')

    ax1 = fig.add_subplot(4,4,1)
    plt.ylabel('Number of Bolometers')
    ax5 = fig.add_subplot(4,4,5)
    plt.ylabel('$T_c$ (mK)', weight='bold')
    ax9 = fig.add_subplot(4,4,9)
    plt.ylabel('n', weight='bold')
    ax13 = fig.add_subplot(4,4,13)
    plt.ylabel('G (pW/K)', weight='bold')
    plt.xlabel('k (pW/K^n)', weight='bold')
    ax6 = fig.add_subplot(4,4,6)
    plt.ylabel('Number of Bolometers')
    ax10 = fig.add_subplot(4,4,10)
    ax14 = fig.add_subplot(4,4,14)
    plt.xlabel('$T_c$ (mK)', weight='bold')
    ax11 = fig.add_subplot(4,4,11)
    plt.ylabel('Number of Bolometers')
    ax15 = fig.add_subplot(4,4,15)
    plt.xlabel('n', weight='bold')
    ax16 = fig.add_subplot(4,4,16)
    plt.ylabel('Number of Bolometers')
    plt.xlabel('G (pW/K)', weight='bold')

    k90=[]; k150=[]; k220=[]
    tc90=[]; tc150=[]; tc220=[]
    n90=[]; n150=[]; n220=[]
    G90=[]; G150=[]; G220=[]

    ps = ['k', 'tc', 'n', 'G']
    for bolo in params:

        # don't plot zero's         # AHHH 2018-02-01
        for p in ps:
            params[bolo][p] = float('nan') if params[bolo][p] == 0 else params[bolo][p]
        
        if params[bolo]['band']=='90':
            dot90=ax5.scatter(params[bolo]['k'], params[bolo]['tc'], alpha=0.5, marker='o', color='r')
            ax9.scatter(params[bolo]['k'], params[bolo]['n'], alpha=0.5, marker= 'o', color='r')
            ax10.scatter(params[bolo]['tc'], params[bolo]['n'], alpha=0.5, marker='o', color='r')
            ax13.scatter(params[bolo]['k'], params[bolo]['G'], alpha=0.5, marker='o', color='r')
            ax14.scatter(params[bolo]['tc'], params[bolo]['G'], alpha=0.5, marker='o', color='r')
            ax15.scatter(params[bolo]['n'], params[bolo]['G'], alpha=0.5, marker='o', color='r')
            k90.append(params[bolo]['k'])
            tc90.append(params[bolo]['tc'])
            n90.append(params[bolo]['n'])
            G90.append(params[bolo]['G'])
        if params[bolo]['band']=='150':
            dot150=ax5.scatter(params[bolo]['k'], params[bolo]['tc'], alpha=0.5, marker='o', color='c')
            ax9.scatter(params[bolo]['k'], params[bolo]['n'], alpha=0.5, marker= 'o', color='c')
            ax10.scatter(params[bolo]['tc'], params[bolo]['n'], alpha=0.5, marker='o', color='c')
            ax13.scatter(params[bolo]['k'], params[bolo]['G'], alpha=0.5, marker='o', color='c')
            ax14.scatter(params[bolo]['tc'], params[bolo]['G'], alpha=0.5, marker='o', color='c')
            ax15.scatter(params[bolo]['n'], params[bolo]['G'], alpha=0.5, marker='o', color='c')
            k150.append(params[bolo]['k'])
            tc150.append(params[bolo]['tc'])
            n150.append(params[bolo]['n'])
            G150.append(params[bolo]['G'])
        if params[bolo]['band']=='220':
            dot220=ax5.scatter(params[bolo]['k'], params[bolo]['tc'], alpha=0.5, marker='o', color='y')
            ax9.scatter(params[bolo]['k'], params[bolo]['n'], alpha=0.5, marker= 'o', color='y')
            ax10.scatter(params[bolo]['tc'], params[bolo]['n'], alpha=0.5, marker='o', color='y')
            ax13.scatter(params[bolo]['k'], params[bolo]['G'], alpha=0.5, marker='o', color='y')
            ax14.scatter(params[bolo]['tc'], params[bolo]['G'], alpha=0.5, marker='o', color='y')
            ax15.scatter(params[bolo]['n'], params[bolo]['G'], alpha=0.5, marker='o', color='y')
            k220.append(params[bolo]['k'])
            tc220.append(params[bolo]['tc'])
            n220.append(params[bolo]['n'])
            G220.append(params[bolo]['G'])

    # handle NANs                      added by Angi 2018-02-01
    k90 = [val for val in k90 if not math.isnan(val)]
    tc90 = [val for val in tc90 if not math.isnan(val)]
    n90 = [val for val in n90 if not math.isnan(val)]
    G90 = [val for val in G90 if not math.isnan(val)]
    k150 = [val for val in k150 if not math.isnan(val)]
    tc150 = [val for val in tc150 if not math.isnan(val)]
    n150 = [val for val in n150 if not math.isnan(val)]
    G150 = [val for val in G150 if not math.isnan(val)]
    k220 = [val for val in k220 if not math.isnan(val)]
    tc220 = [val for val in tc220 if not math.isnan(val)]
    n220 = [val for val in n220 if not math.isnan(val)]
    G220 = [val for val in G220 if not math.isnan(val)]
    
    # pdb.set_trace()

    hist90=ax1.hist(k90,alpha=0.5,color='r')
    ax6.hist(tc90,alpha=0.5,color='r')
    ax11.hist(n90,alpha=0.5,color='r')
    ax16.hist(G90,alpha=0.5,color='r')
    hist150=ax1.hist(k150,alpha=0.5,color='c')
    ax6.hist(tc150,alpha=0.5,color='c')
    ax11.hist(n150,alpha=0.5,color='c')
    ax16.hist(G150,alpha=0.5,color='c')
    hist220=ax1.hist(k220,alpha=0.5,color='y')
    ax6.hist(tc220,alpha=0.5,color='y')
    ax11.hist(n220,alpha=0.5,color='y')
    ax16.hist(G220,alpha=0.5,color='y')

    ax5.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax9.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax10.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax13.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax14.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax15.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax1.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax6.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax11.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    ax16.legend([dot90,dot150,dot220],['90 GHz','150 GHz','220 GHz'])
    return fig

def psat_hist(params, wafernumber):
    fig=plt.figure()
    ps90=[]; ps150=[]; ps220=[]
    for bolo in params:
        if params[bolo]['band'] == '90':
            ps90.append(params[bolo]['psat300'])
        elif params[bolo]['band']=='150':
            ps150.append(params[bolo]['psat300'])
        elif params[bolo]['band']=='220':
            ps220.append(params[bolo]['psat300'])
    plt.hist(ps90, 21,color='r', alpha=0.5, label='90 GHz')
    plt.hist(ps150, color='c', alpha=0.5, label='150 GHz')
    plt.hist(ps220, color='y', alpha=0.5, label='220 GHz')
    plt.legend()
    plt.ylabel('Number of Bolometers')
    plt.xlabel('Power (pW)')
    plt.title('Wafer %s Psat at 300mK'%(wafernumber))
    return fig

def psat_of_t(T,bolo,params):
    k = params[bolo]['k']
    tc = params[bolo]['tc']    
    if params[bolo]['tc_units']=='mK':
        tc=tc/1000.
    n = params[bolo]['n']
    power = k*(tc**n - T**n)

    return power


def GofT_fitplots(mezzmod, gparams, params,xrange=[0.2,0.6], title=''):

    nrows = np.round(np.sqrt(np.ceil(len(gparams[mezzmod]['PsatVtemp']))))
    ncols = np.ceil(len(gparams[mezzmod]['PsatVtemp'])/nrows)
    ds=10./ncols
    fig=plt.figure(figsize=(nrows*ds,ncols*ds))
    
    for jbolo, bolo in enumerate(gparams[mezzmod]['PsatVtemp']):        
        plt.subplot(nrows,ncols,jbolo+1)
        plt.plot(gparams[mezzmod]['PsatVtemp'][bolo]['T'], 1e12*(gparams[mezzmod]['PsatVtemp'][bolo]['Psat']),marker='o', color='k',linestyle='None')
        plot_T=np.linspace(xrange[0],xrange[1],100)
        
        if gparams[mezzmod]['PsatVtemp'][bolo]['name'] in params.keys():
            plot_Psat=psat_of_t(plot_T,gparams[mezzmod]['PsatVtemp'][bolo]['name'],params)
            plt.plot(plot_T, plot_Psat, color='b')
            k = gparams[mezzmod]['fit_params'][bolo][0]
            tc = gparams[mezzmod]['fit_params'][bolo][1]
            n = gparams[mezzmod]['fit_params'][bolo][2]
            psat300 = psat_of_t(0.300,gparams[mezzmod]['PsatVtemp'][bolo]['name'],params)
            ax=plt.gca()
            ax.annotate(params[gparams[mezzmod]['PsatVtemp'][bolo]['name']]['physical_name'],fontsize=8,xy=(0.5,0.89),xycoords='axes fraction',backgroundcolor='w')


        plt.grid(True)
        xtks=plt.xticks()
        if jbolo > nrows*(ncols-1)-1:
            plt.xlabel('T(K)')
            plt.xticks(xtks[0])
        else:
            tmplab=[]
            for kk in xtks[0]:
                tmplab.append('')
            plt.xticks(xtks[0],tmplab)
        ytks=plt.yticks()
        if np.mod(jbolo,ncols)==0:
            plt.ylabel('P (pW)')
            plt.yticks(ytks[0])
        else:
            tmplab=[]
            for kk in ytks[0]:
                tmplab.append('')
            plt.yticks(ytks[0],tmplab)
        plt.ylim([-2, 22])
        plt.xlim(xrange)
        plt.suptitle(title)
        #ax.annotate('k = %.0f$\pm$ %.0f' % (1e12*k, 1e12*gparams[mezzmod]['fit_errs'][bolo][0]),xy=(.05,.5),xycoords='axes fraction')
        #ax.annotate('Tc = %.3fK$\pm$ %.3fK' % (tc, gparams[mezzmod]['fit_errs'][bolo][1]),xy=(.05,.4),xycoords='axes fraction')
        #ax.annotate('Psat(300mK) = %.1f pW' % (1e12*psat300),xy=(.05,.2),xycoords='axes fraction')
        #ax.annotate('G(Tc) = %.0f pW/K' % (1e12*n*k*(tc**(n-1))),xy=(.05,.1),xycoords='axes fraction')
        #ax.annotate(gparams[mezzmod]['PsatVtemp'][bolo]['name'], fontsize=8,xy=(.02,.89),xycoords='axes fraction')
        


    return


def calculate_phonon_noise(n_vec,g_vec,tc_vec, tbath=0.232):
    k_b=1.38064852e-23 #m^2 kg s^-2 K^-1
    tc_vec=tc_vec/1000.
    gamma_phonon= (n_vec+1)/(2*n_vec+3)*(1-(tbath/tc_vec)**(2*n_vec+3))/(1-(tbath/tc_vec)**(n_vec+1))
    nep=np.sqrt(gamma_phonon*4*k_b*tc_vec**2*g_vec)
    
