"""
Generate datafiles which report the distance between the two binary stars throughout the
	duration of a simulation, for all directories found to have dumpfiles.
"""
import sys
import os
import numpy as np
import json
sys.path.insert(0,'../modules')
import phantom

if __name__=='__main__':
    # just want the initial dumps from each dir
    folder = '../init_dumps'
    initial_dumps = [os.path.join(folder, file) for file in os.listdir(folder)]

    results_dict = {}

    for dump in initial_dumps:
        try:
            disc = phantom.read_dump_file(dump)
        except:
            print("could not open file %s" %dump)
            continue
        out_dict = phantom.get_az_averaged_properties(disc)
        r0 = out_dict['r'][1]
        sig0 = out_dict['sigma'][4]
        temp0 = out_dict['temp'][1]
        results_dict[dump] = {
                            'R0' : r0,
                            'Sig0' : sig0,
                            'T0' : temp0
                            }

    json.dump(results_dict, open('sig0_T0_all.json','w'), indent=4)
