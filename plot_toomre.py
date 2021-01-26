import numpy as np
import matplotlib.pyplot as plt
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
# can be a list of files for multiplots
parser.add_argument('-files',nargs='+')
args = parser.parse_args()
files = args.files

for i,file in enumerate(files):
    # read in data and skip header
    data = np.genfromtxt(file,delimiter=',',skip_header=1)
    # read first row with time info on it
    infile = open(file, 'r')
    header = float(infile.readline())
    infile.close()

    # plot toomre vs rad
    plt.figure('Q')
    plt.plot(data[:,0],data[:,2],label='t=%.2f' %header)

    # plot temp vs rad
    plt.figure('T')
    plt.plot(data[:,0],data[:,1],label='t=%.2f' %header)

plt.figure('Q')
plt.ylim([0,10])
plt.xlim([0,100])
plt.title('Toomre, Q, vs rad')
plt.legend()
plt.grid(alpha=0.25)

plt.figure('T')
plt.ylim([0,100])
plt.xlim([0,100])
plt.title('Temp vs rad')
plt.legend()
plt.grid(alpha=0.25)
plt.show()
