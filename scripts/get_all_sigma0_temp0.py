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
    all_dumps = phantom.collect_all_dumps('..')
    # just want the initial dumps from each dir
    initial_dumps = [dump for dump in all_dumps if dump.endswith('sgdisc_00000')]

    results_dict = {}

    for dump in initial_dumps:
        disc = phantom.read_dump_file(dump)
        out_dict = phantom.get_az_averaged_properties(disc)
        r0 = out_dict['r'][1]
        sig0 = out_dict['sigma'][1]
        temp0 = out_dict['temp'][1]
        results_dict[dump] = {
                            'R0' : r0,
                            'Sig0' : sig0,
                            'T0' : temp0
                            }

    json.dump(results_dict, open('sig0_T0_all.json','w'), indent=4)
