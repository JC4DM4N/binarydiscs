import sys, os
import argparse
import numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'../phantom_files'))
from libanalysis import PhantomAnalysis as pa
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'../modules'))
import phantom

parser = argparse.ArgumentParser()
parser.add_argument("-file")
parser.add_argument("-include_companion", action='store_true', default=False)
parser.add_argument("-write_to_file", action='store_true', default=False)
args = parser.parse_args()

disc = pa(args.file)

momentum = disc.massofgas*disc.vxyz
if len(disc.ptmass_xyzmh.shape) == 1:
    sep = disc.xyzh[:3] - disc.ptmass_xyzmh[:3]
else:
    sep = disc.xyzh[:3] - disc.ptmass_xyzmh[:3,0].reshape([3,1])
AM = np.sum(np.cross(sep.T,momentum.T),axis=0)

# want to print different things if we do or don't include the companion in our calculations
if args.include_companion:
    ptmass_momentum = disc.ptmass_xyzmh[4,1]*disc.ptmass_vxyz[:,1]
    ptmass_sep = disc.ptmass_xyzmh[:3,0] - disc.ptmass_xyzmh[:3,1]
    companion_AM = np.cross(ptmass_sep.T, ptmass_momentum.T)
    #angle between the two vectors
    theta = np.arccos(np.dot(AM, companion_AM.T)/(np.linalg.norm(AM)*np.linalg.norm(companion_AM)))
    print("Total AM Vector of disc: %.3f %3f %.3f" %(AM[0], AM[1], AM[2]))
    print("Total AM Vector of companion: %.3f %3f %.3f" %(companion_AM[0], companion_AM[1], companion_AM[2]))
    print("Angle between vectors: %.2f" %(theta*180/np.pi))
    if args.write_to_file:
        if not os.path.exists('AM_angles.dat'):
            f = open('AM_angles.dat','w')
            f.write("time   angle")
        else:
            f = open('AM_angles.dat','a')
        f.write("%.2f   %.2f" %(disc.time, theta*180/np.pi))
        f.close()
else:
    # just print results for the disc
    print("Total AM Vector of disc: %.3f %3f %.3f" %(AM[0], AM[1], AM[2]))
    print("arctan(x/y) = %.3f" %(np.arctan(AM[0]/AM[1])))
    print("arctan(y/x) = %.3f" %(np.arctan(AM[1]/AM[0])))
    print("arctan(x/z) = %.3f" %(np.arctan(AM[0]/AM[2])))
    print("arctan(z/x) = %.3f" %(np.arctan(AM[2]/AM[0])))
    print("arctan(y/z) = %.3f" %(np.arctan(AM[1]/AM[2])))
    print("arctan(z/y) = %.3f" %(np.arctan(AM[2]/AM[1])))
