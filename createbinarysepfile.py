from libanalysis import PhantomAnalysis as pa
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-nfiles')
args = parser.parse_args()
nfiles = int(args.nfiles)

sepfile = open('binsep.dat', 'w')
posfile = open('ptmass_xyz.dat', 'w')

for ifile in range(0,nfiles):
    disc = pa('sgdisc_%s' %str(ifile).zfill(5))
    ptmass_xyzmh = disc.ptmass_xyzmh
    binsep = (ptmass_xyzmh[0,0]-ptmass_xyzmh[0,1])**2 + (ptmass_xyzmh[1,0]-ptmass_xyzmh[1,1])**2 + (ptmass_xyzmh[2,0]-ptmass_xyzmh[2,1])**2
    binsep = binsep**0.5
    sepfile.write('%s %s %s \n' %(ifile, disc.time, binsep))
    posfile.write('%s %s %s %s %s %s \n' %(ptmass_xyzmh[0,0],ptmass_xyzmh[1,0],ptmass_xyzmh[2,0],
                                           ptmass_xyzmh[0,1],ptmass_xyzmh[1,1],ptmass_xyzmh[2,1],))

sepfile.close()
posfile.close()
