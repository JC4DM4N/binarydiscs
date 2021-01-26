# Read in phantom dump file using pyanalysis and calculate azimuthally averaged
# disc temp and toomre Q parameter
# Write results to data file 'temp_Q_vs_rad_N.dat'

from libanalysis import PhantomAnalysis as pa
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-file')
args = parser.parse_args()
file = args.file

#open disc dump file
disc = pa('%s' %file)

#define units - needed for calculating disc temp
udens = disc.units['udens'] #gcm-3
umass = disc.units['umass'] #g
udist = disc.units['udist'] #cm
utime = disc.units['utime'] #s
#uerg = umass*udist**2/utime**2 #erg
uerg = udist**2/utime**2 # erg
uvel = udist/utime
yr = utime/60./60./24./365.25

#Calculate temperatures from thermal energies
kB = 1.38064852e-16    #erg / K
mH = 1.6735575e-24    #grams
gmw = 2.381           #mean mass taken from Phantom
gamma = 5./3.           #barotropic index (NEED TO DOUBLE CHECK THIS)
mstar = 1

temps = mH*gmw*(gamma-1)*disc.utherm*uerg*uerg/kB # from phantom eos.f90
spsound = np.sqrt(gamma*(gamma-1)*disc.utherm*uerg) # from phantom discplot.f90

# want to azimuthally average disc temp and Q, so I can plot T and Q vs Rad
nbins = 4*disc.npart**(1./3.) + 1
#nbins = 151
rmax = 150
rmin = 0
# bin particles into radius bins
radbins = np.linspace(rmin, rmax, nbins)
# radial distances from phantom dumps - these need to be centred on ptmass[0]
rads = np.sqrt((disc.xyzh[0]-disc.ptmass_xyzmh[0,0])**2 + (disc.xyzh[1]-disc.ptmass_xyzmh[1,0])**2)

outfile = open('temp_Q_vs_rad_%s.dat' %file[-3:], 'w')
# want header of current time in simulation
outfile.write('%s \n' %(disc.time*yr))
for ibin,rad, in enumerate(radbins):
    if ibin==0:
        continue
    # particles in this radial bin
    wanted = (rads>radbins[ibin-1]) & (rads<=radbins[ibin])
    # also only want midplane particles (with z < H)
    omega = np.sqrt(mstar/rad**3)
    H = spsound/omega
    wanted = wanted & (np.abs(disc.xyzh[2]-disc.ptmass_xyzmh[2,0])<=H)
    try:
        #calc mean temperature
        temp = np.mean(temps[wanted])
        # calc Q
        rho = disc.massofgas/np.abs(disc.xyzh[3,wanted])**3 # need to double check this is definitely density
        sigma = np.mean(rho*2*H[wanted]) # sigma = rho*2H
        cs = np.mean(spsound[wanted])
        toomre = cs*omega/np.pi/sigma

        outfile.write('%s, %s, %s \n' %(rad, temp, toomre))
    except:
        outfile.write('%s, 0, 0 \n' %rad)

outfile.close()
