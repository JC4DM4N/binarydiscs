from astropy.io import fits
import matplotlib.pyplot as plt
import PIL.Image as Image
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-file')
parser.add_argument('-affine', default=False, action='store_true')
parser.add_argument('-tilt', help='tilt of the disc in radians', type=float)
args = parser.parse_args()

im = fits.open(args.file)
im_sub = im.copy()

for i in range(8):
    plt.imshow(im[0].data[i][0][0],vmin=1e-23,vmax=1e-20)
plt.savefig('continuum.png')

# read in metadata
npix_x = im[0].header['NAXIS1']
npix_y = im[0].header['NAXIS2']
centre_pix = (npix_x/2., npix_y/2.)
pix_index_x, pix_index_y = np.indices((npix_x, npix_y))
# pixel distance from the center pixel
pix_dist = ((pix_index_x-centre_pix[0])**2 + (pix_index_y-centre_pix[1])**2)**0.5

if args.affine:
    # perform affine transformation to deproject the image if required
    # needs to be performed in two halves to ensure transformation is about the centre of the image
    affine_upper = [
              [1,0,0],
              [0, np.cos(args.tilt), -np.sin(args.tilt)],
              [0,np.sin(args.tilt), np.cos(args.tilt)]
            ]
    for i in range(8):
        # need to invert the top half, affine transform, then revert to original row ordering
        pil_im = Image.fromarray(im[0].data[i][0][0][:450][::-1])
        transformed = pil_im.transform((npix_x, 450), Image.AFFINE, data=np.asarray(affine_upper).T.flatten())
        im_sub[0].data[i][0][0][:450] = transformed
        im_sub[0].data[i][0][0][:450] = im_sub[0].data[i][0][0][:450][::-1]

    # perform affine transformation on the bottom half of the image
    for i in range(8):
        pil_im = Image.fromarray(im[0].data[i][0][0][450:])
        transformed = pil_im.transform((npix_x, 451), Image.AFFINE, data=np.asarray(affine_lower).T.flatten())
        im_sub[0].data[i][0][0][450:] = transformed

for i in range(8):
    plt.imshow(im[0].data[i][0][0],vmin=0,vmax=1e-20)
plt.show()

# radial bins for median subtraction
rad_bins = np.linspace(1, max(npix_x, npix_y), 400)

for i, bin in enumerate(rad_bins[1:]):
    in_bin = (pix_dist > rad_bins[i]) & (pix_dist <= rad_bins[i+1])
    for i in range(8):
        im_sub[0].data[i][0][0][in_bin] -= np.median(im[0].data[i][0][0][in_bin])

for i in range(8):
# also ensure no flux are below 0
    im_sub[0].data[i][0][0][im_sub[0].data[i][0][0] < 0] = 0

for i in range(8):
    plt.imshow(im[0].data[i][0][0],vmin=0,vmax=1e-21)

plt.savefig('continuum_median_sub.png')
plt.show()

print()
