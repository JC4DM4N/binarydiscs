import os
import sys
import subprocess
import shutil
import PIL.Image as Image
import matplotlib.pyplot as plt
import numpy as np
import argparse

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'../phantom_files'))
from libanalysis import PhantomAnalysis as pa
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'../modules'))
import phantom

parser = argparse.ArgumentParser()
parser.add_argument('-orientation', default='xy',
                    help='orientation of image. xy or xz.')
args = parser.parse_args()
orientation = args.orientation

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
    plot_id = dump + '.png'
    output_fname = os.path.join(plots_output_dir,plot_id)
    # generate and save the plot
    phantom.generate_png_plot(dump,output_fname,orientation)
    # crop the plots to remove white space
    #crop_splash_image(output_fname)
