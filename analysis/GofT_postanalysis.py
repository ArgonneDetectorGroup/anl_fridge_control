import matplotlib.pyplot as plt
import numpy as np

'''
Before running any of these codes, run the analyze_GofT
codes to get the G parameters.  You need to start with
a gparams dictionary indexed by mezzmod.

gparams = {'m1m4':{'name','PsatVtemp','fit_params','fit_errs'}}
'''

def make_param_dict(gparams):
    params={}
    for mezzmod in gparams:
        for bolo in gparams[mezzmod]['PsatVtemp']:
            k = gparams[mezzmod]['fit_params'][bolo][0]
            tc = gparams[mezzmod]['fit_params'][bolo][1]
            n = gparams[mezzmod]['fit_params'][bolo][2]
            G = n*k*(tc**(n-1))

            params[bolo]={'k':k*1e12, 'k_units':'pW/K^n', 'tc':tc*1e3, 'tc_units':'mK', 'n':n, 'band':bolo.split('.')[-2], 'G':G*1e12, 'G_units':'pW/K'}

            psat300 = k*(tc**n - 0.300**n)
            params[bolo]['psat300'] = psat300*1e12
            params[bolo]['psat_units']='pW'
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

    for bolo in params:
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
    plt.hist(ps90, color='r', alpha=0.5, label='90 GHz')
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
    n = params[bolo]['n']
    power = k*(tc**n - T**n)
    return power


def GofT_fitplots(mezzmod, gparams, params):
    nrows = np.ceil(len(gparams[mezzmod]['PsatVtemp']))
    ncols = np.ceil(len(gparams[mezzmod]['PsatVtemp'])/nrows)
    fig=plt.figure(figsize=(nrows*5,ncols*5))
    for jbolo, bolo in enumerate(gparams[mezzmod]['PsatVtemp']):
        plt.subplot(nrows,ncols,jbolo+1)
        plt.plot(gparams[mezzmod]['PsatVtemp'][bolo]['T'], 1e12*(gparams[mezzmod]['PsatVtemp'][bolo]['Psat']),marker='o', color='k',linestyle='None')
        plot_T=np.linspace(0.2,0.6,100)
        plot_Psat=psat_of_t(plot_T,bolo,params)
        plt.plot(plot_T, 1e12*plot_Psat, color='b')
        plt.xlim(0.2,0.6)
        plt.ylim([-5, 1.2*np.min([100, np.max(1.0e12*plot_Psat)])])
        plt.grid(True)
        k = gparams[mezzmod]['fit_params'][bolo][0]
        tc = gparams[mezzmod]['fit_params'][bolo][1]
        n = gparams[mezzmod]['fit_params'][bolo][2]
        psat300 = psat_of_t(0.300,bolo,mezzmod)
        plt.xlabel('Bath Temperature (K)')
        plt.ylabel('Power on TES (pW)')
        ax=plt.gca()
        ax.annotate('k = %.0f$\pm$ %.0f' % (1e12*k, 1e12*gparams[mezzmod]['fit_errs'][bolo][0]),xy=(.05,.5),xycoords='axes fraction')
        ax.annotate('Tc = %.3fK$\pm$ %.3fK' % (tc, gparams[mezzmod]['fit_errs'][bolo][1]),xy=(.05,.4),xycoords='axes fraction')
        ax.annotate('Psat(300mK) = %.1f pW' % (1e12*psat300),xy=(.05,.2),xycoords='axes fraction')
        ax.annotate('G(Tc) = %.0f pW/K' % (1e12*n*k*(tc**(n-1))),xy=(.05,.1),xycoords='axes fraction')
        ax.annotate(bolo, fontsize=14,xy=(.02,.89),xycoords='axes fraction')
