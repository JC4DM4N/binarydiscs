"""
Generate datafiles which report the distance between the two binary stars throughout the
	duration of a simulation, for all directories found to have dumpfiles.
"""
import sys
import os
import numpy as np
sys.path.insert(0,'../modules')
import phantom

if __name__=='__main__':
    all_dumps = phantom.collect_all_dumps('..')
    # just want unique directories for these dumpfiles
    all_dirs = np.unique([os.path.dirname(dump) for dump in all_dumps])

    out_dir = '../outfiles_general'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for dir in all_dirs:
        phantom.create_binary_separation_file(dir,out_dir)
