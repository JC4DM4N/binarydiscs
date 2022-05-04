import sys, os
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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
    #angle between vector and xy plane
    unit_vec_xy = np.asarray([np.sqrt(0.5),np.sqrt(0.5),0])
    theta2 = np.arccos(np.dot(AM, unit_vec_xy.T)/(np.linalg.norm(AM)*np.linalg.norm(unit_vec_xy)))
    theta2 -= np.pi/2.
    #angle between star AM vector and xy plane
    unit_vec_xy = np.asarray([np.sqrt(0.5),np.sqrt(0.5),0])
    theta3 = np.arccos(np.dot(companion_AM, unit_vec_xy.T)/(np.linalg.norm(companion_AM)*np.linalg.norm(unit_vec_xy)))
    theta3 -= np.pi/2.

    print("Total AM Vector of disc: %.3f %3f %.3f" %(AM[0], AM[1], AM[2]))
    print("Total AM Vector of companion: %.3f %3f %.3f" %(companion_AM[0], companion_AM[1], companion_AM[2]))
    print("Angle between vectors: %.2f" %(theta*180/np.pi))
    print("Angle between vector and xy plane: %.2f" %(theta2*180./np.pi))
    print("Angle between companion AM vector and xy plane: %.2f" %(theta3*180./np.pi))
    if args.write_to_file:
        if not os.path.exists('AM_angles.dat'):
            f = open('AM_angles.dat','w')
            f.write("time   angle   angle_xy  angle_xy_companion \n")
        else:
            f = open('AM_angles.dat','a')
        f.write("%.2f   %.2f   %.2f   %.2f \n" %(disc.time, theta*180/np.pi, theta2*180/np.pi, theta3*180/np.pi))
        f.close()
    # also plot the two vectors
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.quiver(
        0, 0, 0, # <-- starting point of vector
        AM[0]*10, AM[1]*10, AM[2]*10, # <-- directions of vector
        color = 'red', alpha = .8, lw = 3, label='disc',
    )
    ax.quiver(
        0, 0, 0, # <-- starting point of vector
        companion_AM[0], companion_AM[1], companion_AM[2], # <-- directions of vector
        color = 'blue', alpha = .8, lw = 3, label='companion',
    )
    ax.set_xlim([-20,20])
    ax.set_ylim([-20,20])
    ax.set_zlim([-20,20])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.view_init(elev=10., azim=10.)
    plt.legend()
    plt.savefig(os.path.join(os.getcwd(),'%s_AM.png' %args.file))
else:
    # just print results for the disc
    print("Total AM Vector of disc: %.3f %3f %.3f" %(AM[0], AM[1], AM[2]))
    print("arctan(x/y) = %.3f" %(np.arctan(AM[0]/AM[1])))
    print("arctan(y/x) = %.3f" %(np.arctan(AM[1]/AM[0])))
    print("arctan(x/z) = %.3f" %(np.arctan(AM[0]/AM[2])))
    print("arctan(z/x) = %.3f" %(np.arctan(AM[2]/AM[0])))
    print("arctan(y/z) = %.3f" %(np.arctan(AM[1]/AM[2])))
    print("arctan(z/y) = %.3f" %(np.arctan(AM[2]/AM[1])))
