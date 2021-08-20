import os, sys
import PIL.Image as Image
import matplotlib.pyplot as plt
import numpy as np
import shutil
import subprocess
sys.path.insert(0,'../phantom_files')
from libanalysis import PhantomAnalysis as pa

def read_dump_file(input_file):
    disc = pa(input_file)
    return disc

def collect_all_dumps(parent_dir='..'):
    all_dumps = [os.path.join(r,f) for r,d,files in os.walk(parent_dir) for f in files if 'sgdisc_' in f]
    return all_dumps

def edit_splash_limits(disc):
    # plots +/- 150au around the star
    star_xy = disc.ptmass_xyzmh[:2,0]
    xmin, xmax = (star_xy[0] - 200, star_xy[0] + 200)
    ymin, ymax = (star_xy[1] - 200, star_xy[1] + 200)

    # try a constant density limit across all discs
    rho_min, rho_max = (1e-2,1e4)

    # write new limits to splash.limits file
    splash_limits = np.genfromtxt('splash.limits')
    output = splash_limits.copy()
    # x,y limits
    output[0,0] = xmin
    output[0,1] = xmax
    output[1,0] = ymin
    output[1,1] = ymax
    # density limits
    output[5,0] = rho_min
    output[5,1] = rho_max
    #write to file
    np.savetxt('splash.limits',output,fmt='%s')
    return

def edit_splash_defaults():
    splash_defaults = np.genfromtxt('splash.defaults',dtype=str,delimiter='1234./,;')
    output = splash_defaults.copy()
    # ensure plotting physical units
    output = ['IRESCALE=T ,' if 'IRESCALE' in row else row for row in output]
    # increase font size
    output = ['CHARHEIGHT=  1.5 ,' if 'CHARHEIGHT' in row else row for row in output]
    # turn time legend off
    output = ['IPLOTLEGEND=  F ,' if 'IPLOTLEGEND' in row else row for row in output]
    # turn colour bar off
    output = ['ICOLOURBARSTYLE=  0 ,' if 'ICOLOURBARSTYLE' in row else row for row in output]
    # make paper size a "large square"
    output = ['IPAPERSTYLE=  3 ,' if 'IPAPERSTYLE' in row else row for row in output]
    #write to file
    np.savetxt('splash.defaults',output,fmt='%s')
    return

DEFAULT_SPLASH_OUTPUT_FILE = 'splash.png'

def generate_png_plot(input_file,output_file=DEFAULT_SPLASH_OUTPUT_FILE):

    print(input_file)
    input_dir = os.path.dirname(input_file)

    if os.path.exists(os.path.join(input_dir,'splash.limits')):
        shutil.copy(os.path.join(input_dir,'splash.limits'),'.')
    else:
        shutil.copy('../splash_templates/splash.limits','.')
    if os.path.exists(os.path.join(input_dir,'splash.defaults')):
        shutil.copy(os.path.join(input_dir,'splash.defaults'),'.')
    else:
        shutil.copy('../splash_templates/splash.defaults','.')

    disc = read_dump_file(input_file)
    edit_splash_limits(disc)
    edit_splash_defaults()

    subprocess.call(['../phantom_files/splash',input_file,
                    '-y','2',
                    '-x','1',
                    '-r','6',
                    '-dev','/png'])
    shutil.move('splash.png',output_file)

    os.remove('splash.limits')
    os.remove('splash.defaults')

def display_splash_plot(image_file):
    im = Image.open(image_file)
    fig = plt.figure(figsize=(12,12))
    plt.imshow(im)
    plt.xticks([])
    plt.yticks([])
    plt.show()

def get_units():
    units = {
        'udens' : 5.94103125029151e-07,
        'umass' : 1.9891e+33,
        'udist' : 14960000000000.0,
        'utime' : 5022728.790082334,
        'uerg' : 8871227776136.363,
        'uvel' : 2978460.6386750126,
        'yr' : 0.1591606709661804
        }
    return units

def get_midplane_mask(disc):
    # get particles within 1 scale height of disc midplane (if z < H)
    mask = abs(disc.xyzh[2] - disc.ptmass_xyzmh[2,0]) <= abs(disc.xyzh[3])
    return mask

def bin_azimuthally(rads,vals,nbins=100,rmax=100):

    assert len(rads)==len(vals)

    rad_bins = np.linspace(0,rmax,nbins)

    ibins = np.digitize(rads,rad_bins)
    binned_vals = np.asarray([np.mean(vals[ibins==bin]) for bin in range(nbins)])

    return rad_bins,binned_vals

def create_binary_separation_file(dir):
    sepfile = open(os.path.join(dir,'binsep.dat'), 'w')
    posfile = open(os.path.join(dir,'ptmass_xyz.dat'), 'w')

    dumpfiles = sorted([file for file in os.listdir(dir) if 'sgdisc_00' in file])
    # exclude ascii or temp files
    dumpfiles = [file for file in dumpfiles if '.tmp' not in file]
    dumpfiles = [file for file in dumpfiles if '.ascii' not in file]

    for dump in dumpfiles:
        disc = read_dump_file(dump)
        ptmass_xyzmh = disc.ptmass_xyzmh
        binsep = (ptmass_xyzmh[0,0]-ptmass_xyzmh[0,1])**2 + (ptmass_xyzmh[1,0]-ptmass_xyzmh[1,1])**2 + (ptmass_xyzmh[2,0]-ptmass_xyzmh[2,1])**2
        binsep = binsep**0.5
        sepfile.write('%s %s %s \n' %(ifile, disc.time, binsep))
        posfile.write('%s %s %s %s %s %s \n' %(ptmass_xyzmh[0,0],ptmass_xyzmh[1,0],ptmass_xyzmh[2,0],
                                               ptmass_xyzmh[0,1],ptmass_xyzmh[1,1],ptmass_xyzmh[2,1],))

    sepfile.close()
    posfile.close()
