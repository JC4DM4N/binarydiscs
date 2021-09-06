"""
Run phantom for all dump files on disk to generate u and du/dt datafiles.
Ensure debugging code in force.F90 is enabled, otherwise the datafile will not 
	be written.
"""
import sys
import os
import datetime as dt

sys.path.insert(0,'../modules')
import phantom

all_dumps = phantom.collect_all_dumps()

for dump in all_dumps:
	fid = phantom.folder_id(dump)
	outfile = os.path.join('../u_and_udot_files', fid+'.dat')
	phantom.generate_u_udot_file(dump, outfile)
