import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm

res = json.load(open('../data/results_dict.json','r'))

rperi = []
rfrag = []
nfrag = []
for f,values in res.items():
    rperi.append(values['rperi'])
    rfrag.append(min(values['rfrag']))
    nfrag.append(values['Nfrag_final'])
plt.figure('minimum fragment separations')
plt.scatter(rperi,rfrag,c=nfrag,cmap=cm.inferno,edgecolors='black',s=100)
plt.xlabel(r'Periastron binary separation, $r_{\rm peri, actual}$ (AU)',fontsize=12)
plt.ylabel(r'Minimum initial $a_{\rm fragment}$ (AU)',fontsize=12)
cbar = plt.colorbar()
cbar.ax.tick_params(labelsize=12)
cbar.set_label(label='Number of fragments present in the final disc',size=12)
plt.savefig('all_fragment_separations.png')
plt.show()
