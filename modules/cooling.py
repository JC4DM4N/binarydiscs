import numpy as np

def interp_myeos(rho,T,u,myeos):
    """
    Interpolate myeos.dat file, using utherm, temperature and rho to obtain
        kappaPart, kappaBar, gmw - for use in the calculation of tcool.
    """
    # find density value(s) in myeos closest to rho
    diff_rho = np.abs(myeos[:,0] - rho)
    rho_ = myeos[diff_rho.argmin(),0]

    subset = myeos[myeos[:,0]==rho_]

    # from this subset, find the temperature value(s) closest to T
    diff_temp = np.abs(subset[:,1]-T)
    temp_ = subset[diff_temp.argmin(),1]

    subset = subset[subset[:,1]==temp_]

    # from this subset, find the energy value(s) closest to u
    diff_u = np.abs(subset[:,2]-u)
    u_ = subset[diff_u.argmin(),2]

    subset = subset[subset[:,2]==u_]

    # return gmw, kappaBar, kappaPart
    return rho_, temp_, u_, subset[0][3], subset[0][4], subset[0][5]

def polytropic_cooling(input_dict, verbose=True):
    """
    Determine tcool and beta from azimuthally averaged disc properties.
    input_dict is expected to be consistent with that returned from phantom/get_az_averaged_properties(),
        hence should contain radius, surface density and internal energy.
    """
    myeos = np.genfromtxt('../phantom_files/myeos.dat', skip_header=1)
    #eos = myeos.reshape([261,1001,6])

    stefboltz = 5.67e-5

    Tmin = 10.0
    rho = np.asarray(input_dict['rho'])
    coldens = np.asarray(input_dict['sigma'])
    utherm = np.asarray(input_dict['utherm'])
    temp = np.asarray(input_dict['temp'])

    kappaBar = []
    kappaPart = []
    for i, (rhoi, tempi, ui) in enumerate(zip(rho, temp, utherm)):
        rho_, temp_, u_, gmw, kBar, kPart = interp_myeos(rhoi, tempi, ui, myeos)
        kappaBar.append(kBar)
        kappaPart.append(kPart)

        if verbose:
            # ensure the interpolated density, temp and internal energy returned are close to the input values
            if not np.allclose([rho_, temp_, u_], [rhoi, tempi, ui], rtol=0.05):
                print('Warning: myeos.dat interpolation values diverging from true values for index %i' %i)
                print('original values: {}'.format([rho_, temp_, u_]))
                print('interpolated values: {}'.format([rhoi, tempi, ui]))
    kappaBar = np.asarray(kappaBar)
    kappaPart = np.asarray(kappaPart)

    tcool = utherm*(kappaBar*coldens**2 + 1/kappaPart)
    tcool = tcool/(4*stefboltz*(temp**4 - Tmin**4))

    return tcool

def interp_myeos_original(ui, rhoi, eos):
    """
    Interpolate myeos.dat file, using utherm and rho to obtain the part temperature,
        kappaPart, kappaBar, gmw and gamma - for use in the calculation of tcool.
    This function is taken directly from the subroutine in phantom. Not being used currently
        but probably best to keep it around for now.
    """
    if rhoi < 1e-24:
        rhoi_ = 1e-24
    else:
        rhoi_ = rhoi

    i = 0
    while eos[i,0,0] <= rhoi_ and i < 260:
        i+=1

    if ui < 0.5302e8:
        ui_ = 0.5302e8
    else:
        ui_ = ui

    j = 0
    while eos[i-1,j,2] <= ui_ and j < 1000:
        j+=1

    m = (eos[i-1,j-1,4] - eos[i-1,j,4])/(eos[i-1,j-1,2] - eos[i-1,j,2])
    c = eos[i-1,j,4] - m*eos[i-1,j,2]
    kbar1 = m*ui_ + c

    m = (eos[i-1,j-1,5] - eos[i-1,j,5])/(eos[i-1,j-1,2] - eos[i-1,j,2])
    c = eos[i-1,j,5] - m*eos[i-1,j,2]
    kappa1 = m*ui_ + c

    m = (eos[i-1,j-1,1] - eos[i-1,j,1])/(eos[i-1,j-1,2] - eos[i-1,j,2])
    c = eos[i-1,j,1] - m*eos[i-1,j,2]
    Tpart1 = m*ui_ + c

    m = (eos[i-1,j-1,3] - eos[i-1,j,3])/(eos[i-1,j-1,2] - eos[i-1,j,2])
    c = eos[i-1,j,3] - m*eos[i-1,j,2]
    gmw1 = m*ui_ + c

    j = 0
    while eos[i,j-1,2] <= ui_ and j < 1000:
        j+=1

    m = (eos[i,j-1,4] - eos[i,j,4])/(eos[i,j-1,2] - eos[i,j,2])
    c = eos[i,j,4] - m*eos[i,j,2]
    kbar2 = m*ui_ + c

    m = (eos[i,j-1,5] - eos[i,j,5])/(eos[i,j-1,2] - eos[i,j,2])
    c = eos[i,j,5] - m*eos[i,j,2]
    kappa2 = m*ui_ + c

    m = (eos[i,j-1,1] - eos[i,j,1])/(eos[i,j-1,2] - eos[i,j,2])
    c = eos[i,j,1] - m*eos[i,j,2]
    Tpart2 = m*ui_ + c

    m = (eos[i,j-1,3] - eos[i,j,3])/(eos[i,j-1,2] - eos[i,j,2])
    c = eos[i,j,3] - m*eos[i,j,2]
    gmw2 = m*ui_ + c

    m = (kappa2 - kappa1)/(eos[i,0,0]-eos[i-1,0,0])
    c = kappa2 - m*eos[i,0,0]
    kappaPart = m*rhoi_ + c

    m = (kbar2 - kbar1)/(eos[i,0,0]-eos[i-1,0,0])
    c = kbar2 - m*eos[i,0,0]
    kappaBar = m*rhoi_ + c

    m = (Tpart2 - Tpart1)/(eos[i,0,0]-eos[i-1,0,0])
    c = Tpart2 - m*eos[i,0,0]
    Ti = m*rhoi_ + c

    m = (gmw2 - gmw1)/(eos[i,0,0]-eos[i-1,0,0])
    c = gmw2 - m*eos[i,0,0]
    gmwi = m*rhoi_ + c

    cv = ui_/Ti
    gammai = 1 + 1.38e-16/1.67e-24/gmwi/cv

    out = {
        'temp': Ti,
        'kappaBar': kappaBar,
        'kappaPart': kappaPart,
        'gmw': gmwi,
        'gamma': gammai
    }

    return out
