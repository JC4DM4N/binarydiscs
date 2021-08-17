import numpy as np
import matplotlib.pyplot as plt

dat = np.genfromtxt('ptmass_xyz.dat')

# centre orbits on primary star
dat[:,3] -= dat[:,0]
dat[:,0] -= dat[:,0]
dat[:,4] -= dat[:,1]
dat[:,1] -= dat[:,1]
dat[:,5] -= dat[:,2]
dat[:,2] -= dat[:,2]

plt.plot(dat[:,3],dat[:,4],color='red')
plt.scatter(0,0)
plt.xlabel('Dist, AU')
plt.ylabel('Dist, AU')
plt.title('Binary orbits centred on primary star position')

plt.show()
