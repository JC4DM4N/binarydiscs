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

if __name__=='__main__':
	# ensure outfile directory exists
	outdir = '../u_and_udot_files'
	if not os.path.exists(outdir):
		os.mkdir(outdir)

	all_dumps = phantom.collect_all_dumps()

	for dump in all_dumps:
		fid = phantom.folder_id(dump)
		outfile = os.path.join(outdir, fid+'.dat')
		phantom.generate_u_udot_file(dump, outfile)
