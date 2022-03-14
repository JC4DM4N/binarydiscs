import os
import sys
import subprocess
import shutil
import PIL.Image as Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import argparse

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'../phantom_files'))
from libanalysis import PhantomAnalysis as pa
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'../modules'))
import phantom

plots_output_dir = '.'
all_dumps = [file for file in os.listdir('.') if 'abc' in file]
# potentially will be some files like 'sgdisc_00000.png', so remove these from list
all_dumps = [file for file in all_dumps if not file.endswith('.png')]

def crop_splash_image(input_file):
    im = Image.open(input_file)
    box = (80, 0, 730, 600)
    small_im = im.crop(box)
    small_im.save(input_file)

# plot all discs
for dump in all_dumps:
    # generate and save the plot of density
    plot_id = dump + '_dens.png'
    output_fname = os.path.join(plots_output_dir,plot_id)
    phantom.generate_png_plot(dump,output_fname,render=6)

    # generate and save an edge on plot rendered by density
    plot_id = dump + '_dens_edgeon.png'
    output_fname = os.path.join(plots_output_dir,plot_id)
    phantom.generate_png_plot(dump,output_fname,orientation='xz',render=6)

    # generate and save the plot of div v
    plot_id = dump + '_divv.png'
    output_fname = os.path.join(plots_output_dir,plot_id)
    phantom.generate_png_plot(dump,output_fname,render=11)

    # Generate plots of Toomre parameter
    plot_id = dump + '_toomre.png'
    output_fname = os.path.join(plots_output_dir,plot_id)
    disc = phantom.read_dump_file(dump)
    disc_properties = phantom.get_az_averaged_properties(disc,midplane_only=False)
    fig = plt.Figure(figsize=(5,5))
    plt.plot(disc_properties['r'], disc_properties['toomre'])
    plt.ylabel('Toomre Q',fontsize=20)
    plt.xlabel('Radius (AU)',fontsize=20)
    plt.xlim([0,100])
    plt.ylim([0,5])
    plt.savefig(output_fname)
    plt.clf()

def generate_plot_title():
    dirname = os.getcwd().split('/')[-1]
    translations = {
        'mdisc': 'Disc Mass: ',
        'opacity': 'Opacity prefactor: ',
        'tmin': 'Floor temperature: ',
        'mbin': 'Companion Mass: ',
        ' i': '\n Binary Inclination: ',
        ' e': ' Binary Eccentricity: '
    }
    plot_title = dirname.replace('_','  ')
    for k, v in translations.items():
        plot_title = plot_title.replace(k,v)
    return plot_title

title = generate_plot_title()

# stitch all the plots together
all_plots = [file for file in os.listdir('.') if file.endswith('.png')]
for i, dump in enumerate(all_dumps):

    fig, ax = plt.subplots(2,2,figsize=(13,10))

    plot_id = dump + '_dens.png'
    fname = os.path.join(plots_output_dir,plot_id)
    ax[0,0].imshow(mpimg.imread(fname))
    ax[0,0].axis('off')
    plot_id = dump + '_dens_edgeon.png'
    fname = os.path.join(plots_output_dir,plot_id)
    ax[1,0].imshow(mpimg.imread(fname))
    ax[1,0].axis('off')
    plot_id = dump + '_divv.png'
    fname = os.path.join(plots_output_dir,plot_id)
    ax[0,1].imshow(mpimg.imread(fname))
    ax[0,1].axis('off')
    plot_id = dump + '_toomre.png'
    fname = os.path.join(plots_output_dir,plot_id)
    ax[1,1].imshow(mpimg.imread(fname))
    ax[1,1].axis('off')

    fig.text(0.2, 0.5,title, fontsize=20)
    plot_id = dump + '_multiplot.png'
    output_fname = os.path.join(plots_output_dir,plot_id)
    plt.tight_layout()
    plt.savefig(output_fname)
    plt.clf()
