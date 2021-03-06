'''
SHORT DESCRIPTION
Fit various functions, including 1D signals, planes, etc.

FUTURE IMPROVEMENTS
fit_linear, fit_periodic

TESTING STATUS
Tested.
'''

### IMPORT MODULES ---
import numpy as np
import matplotlib.pyplot as plt


### TIMESERIES FITTING ---
def fit_linear(x, y, verbose=False):
    '''
    Fit an offset and secular trend to a 1D signal.
    '''
    # Parameters
    assert len(x) == len(y), 'Arrays x and y must be the same length'
    N = len(x)

    # Design matrix
    G = np.ones((N, 2))
    G[:,1] = x.flatten()

    # Plane fit parameters
    B = np.linalg.inv(np.dot(G.T, G)).dot(G.T).dot(y)

    # Reconstruct curve
    yhat = G.dot(B)

    # Compute residuals
    res = y - yhat
    RSS = np.sqrt(np.sum(res**2))  # root sum of squares
    meanRes = RSS/len(res)  # mean residual

    # Report if requested
    if verbose == True:
        B = B.flatten()
        print('Linear fit')
        print('x^0 {:f}\nx^1 {:f}'.format(*B))
        print('Expected residual: {:f}'.format(expRes))

    # Plot if requested
    if plot == True:
        fig, ax = plt.subplots()
        ax.plot(x, y, 'k.', label='data')
        ax.plot(x, yhat, 'b', label='fit')

    print('Not functional yet ;)')
    exit()


def fit_periodic(x, y, freq=1, verbose=False):
    '''
    Fit a periodic, linear, and offset to a 1D signal.
    Assumes a period/freq of 1 year.
    '''
    # Parameters
    assert len(x) == len(y), 'Arrays x and y must be the same length'
    N = len(x)

    # Design matrix
    G = np.ones((N, 4))
    G[:,1] = x.flatten()
    G[:,2] = np.sin(2*np.pi*freq*x)
    G[:,3] = np.cos(2*np.pi*freq*x)

    print('Not functional yet ;)')
    exit()



### SURFACE FITTING ---
def fit_surface(img, mask, degree=1, dx=1, dy=1, decimation=0, verbose=False, plot=False):
    '''
    Fit a n-degree polynomial to the image data set.
    Exclude mask values. Decimate by 10^[decimation].
    Horizontal units are arbitrary as long as pixels dimensions are equal.
    '''
    # Decimation factor
    dFactor = int(10**decimation)

    # Image parameters
    M, N = img.shape
    MN = M*N

    # Reformat image as MN x 1 array
    Z = img.copy()
    Z = Z.reshape(MN, 1)

    # Establish grid
    y = np.linspace(-1, 1, M)
    x = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)

    # Design matrix - depends on polynomial degree
    G = np.ones((MN, 1+2*degree))  # empty design matrix
    for i in range(1, degree+1):
        # Populate design matrix
        G[:,2*i-1] = X.flatten()**i
        G[:,2*i] = Y.flatten()**i

    # Reduce data to valid data points
    nds = mask.flatten()==1  # non-masked indices
    Gvld = G[nds,:]  # valid data points
    Zvld = Z[nds]  # valid data points

    # Decimate for speed
    Gvld = Gvld[::dFactor]
    Zvld = Zvld[::dFactor]

    # Plane fit parameters
    B = np.linalg.inv(np.dot(Gvld.T, Gvld)).dot(Gvld.T).dot(Zvld)

    # Reconstruct surface
    surface = G.dot(B).reshape(M, N)

    # Compute residuals
    res = img - surface  # residuals
    res = np.ma.array(res, mask=(mask==0))  # mask residuals
    res = res.compressed().flatten()  # use only valid residuals
    RSS = np.sqrt(np.sum(res**2))  # root sum of squares
    expRes = RSS/len(res)  # mean residual

    # Report if requested
    if verbose == True:
        B = B.flatten()
        print('Polynomial fit')
        print('Order: {:d}'.format(degree))
        print('\toffset: {:f}'.format(B[0]))
        [print('\tX^{i:d} {X:f} Y^{i:d} {Y:f}'.format(**{'i':i, 'X':B[2*i-1], 'Y':B[2*i]})) \
            for i in range(1, degree+1)]
        print('Expected residual: {:f}'.format(expRes))

    # Plot if requested
    if plot == True:
        fig, ax = plt.subplots()
        ax.imshow(surface)
        ax.set_title('Surface')

    return surface, B