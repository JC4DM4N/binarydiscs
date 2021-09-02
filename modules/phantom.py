import os, sys
import PIL.Image as Image
import matplotlib.pyplot as plt
import numpy as np
import shutil
import subprocess
sys.path.insert(0,'../phantom_files')
from libanalysis import PhantomAnalysis as pa

def get_units():
    """
    Dictionary of code -> physical units conversion.
    """
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

UNITS = get_units()

def read_dump_file(input_file):
    """
    Read phantom dump file using pyphantom/PhantomAnalysis
    """
    disc = pa(input_file)
    return disc

def folder_id(dir):
    """
    Convert directory path to a readable id which is generally used here to
        generate output file names for figures, data files etc.
    """
    return dir.split('../')[1].replace('/','_').replace('.','')

def collect_all_dumps(parent_dir='..'):
    """
    Walk through all directories in parent_dir, collecting any folders containing a phantom
        dump file with the prefix 'sgdisc_'
    """
    all_dumps = [os.path.join(r,f) for r,d,files in os.walk(parent_dir) for f in files if 'sgdisc_' in f]
    unwanted_extensions = ['.png','.dat','.tmp','.ascii']
    all_dumps = [dump for dump in all_dumps if not any([dump.endswith(ext) for ext in unwanted_extensions])]
    return all_dumps

def collect_all_final_dumps(parent_dir='..'):
    """
    Walk through all directories in parent_dir, collecting any folders containing a phantom
        dump file with the prefix 'sgdisc_'. For each folder containing dump files, this function
        will return the dump which represents the latest time in the simulation (identified by its
        numerical suffix).
    """
    all_final_dumps = []
    unwanted_extensions = ['.png','.dat','.tmp','.ascii']
    for r,d,files in os.walk('..'):
        all_dumps = [os.path.join(r,f) for f in files if 'sgdisc_' in f]
        all_dumps = [dump for dump in all_dumps if not any([dump.endswith(ext) for ext in unwanted_extensions])]
        # also don't want any dumps from the 'extra_dumps' subfolders
        all_dumps = [dump for dump in all_dumps if 'extra' not in dump]
        # also don't want any dumps from the 'debugging_dumps' subfolders
        all_dumps = [dump for dump in all_dumps if 'debugging' not in dump]
        if all_dumps:
            all_final_dumps.append(sorted(all_dumps)[-1])
    return all_final_dumps

def edit_splash_limits(disc):
    """
    Edit splash.limits file for a few custom plotting preferences.
    Required splash.defaults file is present in the working directory.
    """
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
    """
    Edit splash.defaults file for a few custom plotting preferences.
    Required splash.defaults file is present in the working directory.
    """
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
    """
    Generate rendered plot of gas density by running splash and saving the output
        as a png file.
    Function will copy splash.limits and splash.defaults file into the working
        directory, edit them to contain the desired limits, and then generate the
        png plot.
    """
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

def get_midplane_mask(disc):
    """
    Get particles within 1 scale height of disc midplane (if z < H), from
        phantom disc instance.
    """
    mask = abs(disc.xyzh[2] - disc.ptmass_xyzmh[2,0]) <= abs(disc.xyzh[3])
    return mask

def create_binary_separation_file(input_dir,output_dir):
    """
    Generate binary separation file of [ifile, time, binary separation] from a
        directory of phantom dumps generated during a run containing bianry stars.
    Also generates a file of [star1_x, star1_y, star1_z, star2_x, star2_y, star2_z]
        for any other desired calculations.
    Useful for plotting the phase of the binary orbit and monitoring the progress of
        each simulation.
    """
    dir_id = folder_id(input_dir)

    sepfile = open(os.path.join(output_dir,dir_id+'_binsep.dat'), 'w')
    posfile = open(os.path.join(output_dir,dir_id+'_ptmass_xyz.dat'), 'w')

    dumpfiles = [file for file in os.listdir(dir) if 'sgdisc_00' in file]
    # exclude ascii or temp files
    unwanted_extensions = ['.png','.dat','.tmp','.ascii']
    dumpfiles = [dump for dump in dumpfiles if not any([dump.endswith(ext) for ext in unwanted_extensions])]
    dumpfiles = sorted(dumpfiles)

    for dump in dumpfiles:
        try:
            disc = read_dump_file(os.path.join(input_dir,dump))
        except Exception as e:
            print('failed to load dumpfile: %s' %os.path.join(input_dir,dump))
            continue
        ptmass_xyzmh = disc.ptmass_xyzmh
        # only want to calculate anything if there's 2 stars
        if ptmass_xyzmh.shape[1] == 2:
            binsep = (ptmass_xyzmh[0,0]-ptmass_xyzmh[0,1])**2 + (ptmass_xyzmh[1,0]-ptmass_xyzmh[1,1])**2 + (ptmass_xyzmh[2,0]-ptmass_xyzmh[2,1])**2
            binsep = binsep**0.5
            # file id
            ifile = dump.split('sgdisc_')[1].lstrip('0')
            sepfile.write('%s %s %s \n' %(ifile, disc.time, binsep))
            posfile.write('%s %s %s %s %s %s \n' %(ptmass_xyzmh[0,0],ptmass_xyzmh[1,0],ptmass_xyzmh[2,0],
                                                   ptmass_xyzmh[0,1],ptmass_xyzmh[1,1],ptmass_xyzmh[2,1],))

    sepfile.close()
    posfile.close()

def get_az_averaged_properties(disc,nbins=100,rmax=100):
    """
    Calcualte azimuthally averaged disc properties from pyphantom disc instance.
    """
    radii = np.sqrt(
             (disc.xyzh[0]-disc.ptmass_xyzmh[0,0])**2 +
             (disc.xyzh[1]-disc.ptmass_xyzmh[1,0])**2
            )

    rad_bins = np.linspace(0,rmax,nbins)
    ibins = np.digitize(radii,rad_bins)

    #Calculate temperatures from thermal energies
    kB = 1.38064852e-16    #erg / K
    mH = 1.6735575e-24    #grams
    gmw = 2.381           #mean mass taken from Phantom
    gamma = 5./3.         #barotropic index
    mstar = 1
    G = 6.67430e-8        # cgs grav constant

    out = {'r' : [],
           'npart': [],
           'omega': [],
           'temp': [],
           'sigma': [],
           'cs': [],
           'toomre': [],
           'utherm': []
          }

    for i,rad in enumerate(rad_bins):
        # surface area of this radial bin
        bin_area = np.pi*(rad_bins[i]**2 - rad_bins[i-1]**2)
        bin_area_cgs = bin_area*UNITS['udist']*UNITS['udist']
        # mask for particles in this bin
        inbin = ibins==i
        # epicyclic frequency at this radial bin
        omega_cgs = np.sqrt(G*mstar*UNITS['umass']/(rad*UNITS['udist'])**3)
        # only want particles in disc midplane, defined as within 1AU of center
        midplane_mask = abs(disc.xyzh[2]-disc.ptmass_xyzmh[2,0])*UNITS['udist'] < UNITS['udist']
        # don't want any particles with h < 0
        h_mask = disc.xyzh[3] > 0
        wanted = inbin & midplane_mask & h_mask
        # calc mean temperature, from phantom eos.f90
        temp_cgs = np.mean(mH*gmw*(gamma-1)*disc.utherm[wanted]*UNITS['uerg']/kB)
        # density within this bin, from splash read_data_sphNG.f90
        rho_cgs = disc.massofgas*UNITS['umass']/np.abs((disc.hfact/disc.xyzh[3,wanted])*UNITS['udist'])**3
        sigma_cgs = np.sum(wanted)*disc.massofgas*UNITS['umass']/bin_area_cgs
        # cs = RMS cs within annulus
        spsound2_cgs = gamma*(gamma-1)*disc.utherm*UNITS['uerg'] # from phantom discplot.f90
        cs_cgs = np.sqrt(np.mean(spsound2_cgs[wanted]))
        # calc Q
        toomre = cs_cgs*omega_cgs/np.pi/sigma_cgs/G

        out['r'].append(rad)
        out['npart'].append(np.sum(wanted))
        out['omega'].append(omega_cgs)
        out['temp'].append(temp_cgs)
        out['sigma'].append(sigma_cgs)
        out['cs'].append(cs_cgs)
        out['toomre'].append(toomre)
        out['utherm'].append(np.mean(disc.utherm[wanted])*UNITS['uerg'])

    return out

def generate_u_udot_file(dump,outfile):
    """
    Generate data file containing thermodynamic properties of gas disc by running phantom
        directly. Data file will contain properties not readily available in pyphantom,
        such as du/dt, ttherm, du/dt (diffusion) and u_equilibrium.
    Ensure code and the end of the force subroutine in force.F90 is enabled in order
        to generate the required datafile.
    """
    # make temporary directory for running all this from
    td = 'tempdir'
    if os.path.exists(td):
        subprocess.call(['rm','-r',td])
    os.mkdir(td)

    # this will be "sgdisc_00..."
    dump_id = dump.split('/')[-1]
    # copy required files to tempdir
    shutil.copyfile('../phantom_files/sgdisc.in',os.path.join(td,'sgdisc.in'))
    shutil.copyfile('../phantom_files/phantom',os.path.join(td,'phantom'))
    shutil.copyfile('../phantom_files/myeos.dat',os.path.join(td,'myeos.dat'))
    shutil.copyfile(dump,os.path.join(td,dump_id))

    # edit sgdisc.in file to contain reference to correct dump
    infile = np.genfromtxt(os.path.join(td,'sgdisc.in'),dtype=str, delimiter='1,234jdks')
    new_string = 'dumpfile = ' + str(dump_id)
    infile = [new_string if 'dumpfile' in row else row for row in infile]
    np.savetxt(os.path.join(td,'sgdisc.in'),infile,fmt="%s")

    # change directory to tempdir for running phantom
    os.chdir(td)
    # allow permission to execute phantom
    subprocess.call(['chmod', 'a+x', 'phantom'])
    # all files now in place, run phantom
    subprocess.call(['./phantom','sgdisc.in'])
    # move generated file to output directory
    shutil.move('u_and_udot.dat',os.path.join('..',outfile))

    os.chdir('..')
    subprocess.call(['rm','-r',td])

    return

def read_u_udot_file(infile):
    """
    Take data file generated in generate_u_udot_file() and parse into usable dictionary.
    """
    data = np.genfromtxt(infile,dtype=float)

    out = {
        'x': data[:,0],
        'y': data[:,1],
        'z': data[:,2],
        'h': data[:,3],
        'u': data[:,4],
        'uequil': data[:,5],
        'ttherm': data[:,6],
        'ptmass_x': data[:,7][0],
        'ptmass_y': data[:,8][0],
        'ptmass_z': data[:,9][0],
        'dudt': data[:,10],
        'dudiff': data[:,11]
    }

    return out

def get_az_averaged_u_udot(results_dict,nbins=100,rmax=100):
    """
    Calculate azimuthally averaged u, du/dt, beta and tcool from values outputted
        directly from phantom.
    results_dict should be consistent with that generated in read_u_udot_file().
    """
    radii = np.sqrt(
        (results_dict['x'] - results_dict['ptmass_x'])**2 +
        (results_dict['y'] - results_dict['ptmass_y'])**2
    )

    rad_bins = np.linspace(0,rmax,nbins)
    ibins = np.digitize(radii,rad_bins)

    #Calculate temperatures from thermal energies
    mstar = 1
    G = 6.67430e-8        # cgs grav constant

    out = {'r' : [],
       'u': [],
       'udot': [],
       'tcool': [],
       'beta': []
      }

    for i,rad in enumerate(rad_bins):
        # mask for particles in this radial bin
        inbin = ibins==i
        # only want particles in disc midplane, defined as within 1AU of center
        midplane_mask = np.abs(results_dict['z']-results_dict['ptmass_z']) < 1
        # only want particles with h>0
        h_mask = results_dict['h'] > 0
        # the mask
        wanted = h_mask & inbin & midplane_mask
        # epicyclic frequency at this radial bin
        omega_cgs = np.sqrt(G*mstar*UNITS['umass']/(rad*UNITS['udist'])**3)
        u = np.mean(results_dict['u'][wanted])
        #udot = (results_dict['uequil'][wanted] - results_dict['u'][wanted])/results_dict['ttherm'][wanted]
        udot = np.mean(results_dict['dudt'][wanted])
        tcool = u/udot
        tcool = np.mean(results_dict['u'][wanted]/results_dict['dudt'][wanted])

        out['r'].append(rad)
        out['u'].append(u)
        out['udot'].append(udot)
        out['tcool'].append(tcool)
        out['beta'].append(omega_cgs*tcool)

    return out
