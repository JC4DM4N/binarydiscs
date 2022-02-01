import sys, os
path_to_pyphantom = '../../../programs/phantom/scripts/pyphantom/'
sys.path.insert(0,os.path.join(os.path.dirname(__file__),path_to_pyphantom))

from phantomanalysis import PhantomAnalysis
