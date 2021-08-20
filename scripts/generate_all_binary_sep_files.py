import sys
import numpy as np
sys.path.insert(0,'..')
import phantom

if __name__=='__main__':
    all_dumps = phantom.collect_all_dumps('../..')
    # just want unique directories for these dumpfiles
    all_dirs = np.unique([os.path.dirname(dump) for dump in all_dumps])
    for dir in all_dirs:
        phantom.create_binary_separation_file(dir)
