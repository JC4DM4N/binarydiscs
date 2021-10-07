import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import matplotlib.markers as mmarkers
import matplotlib.lines as mlines


res = json.load(open('../data/results_dict.json','r'))

asep = []
rfrag = []
ecc=[]
inc=[]
for f,values in res.items():
    asep.append(values['a'])
    rfrag.append(min(values['rfrag']))
    ecc.append(values['e'])
    inc.append(int(values['i']/30))

all_markers = ['o','^','P','*']
markers = [all_markers[i] for i in inc]

def mscatter(x,y, ax=None, m=None, **kw):
    ax = ax or plt.gca()
    sc = ax.scatter(x,y,**kw)
    if (m is not None) and (len(m)==len(x)):
        paths = []
        for marker in m:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(
                        marker_obj.get_transform())
            paths.append(path)
        sc.set_paths(paths)
    ax.grid(alpha=0.5)
    ax.set_axisbelow(True)
    return sc

sc = mscatter(asep,rfrag,c=ecc,cmap=cm.get_cmap('inferno_r'),edgecolors='black',s=150,m=markers)
plt.xlabel(r'Companion semi-major axis (AU)',fontsize=12)
plt.ylabel(r'Minimum initial fragment separation (AU)',fontsize=12)
cbar = plt.colorbar(sc,ticks=[0,0.25,0.5])
cbar.ax.tick_params(labelsize=12)
cbar.set_label(label='Companion eccentricity',size=12)

handles = [mlines.Line2D([], [], color='white', marker=symb, linestyle='None',
                          markersize=10, markeredgecolor='black') for symb in all_markers]
labels=[r'$i=0^\circ$',r'$i=30^\circ$',r'$i=60^\circ$',r'$i=90^\circ$',]
plt.legend(handles,labels)
plt.ylim([24,85])
plt.savefig('all_fragment_separations.png')
plt.show()
