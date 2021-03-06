# -*- coding: utf-8 -*-
"""
=================================
Finding and masking bright pixels
=================================

How to find and overplot the location of the brightest
pixel and then mask pixels around that region.
"""
# sphinx_gallery_thumbnail_number = 2

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

import astropy.units as u

import sunpy.map
from sunpy.data.sample import AIA_171_IMAGE

###############################################################################
# We start with the sample data.
aia = sunpy.map.Map(AIA_171_IMAGE)

###############################################################################
# To find the brightest pixel, we find the maximum in the AIA image data
# then transform that pixel coordinate to a map coordinate.
pixel_pos = np.argwhere(aia.data == aia.data.max()) * u.pixel
hpc_max = aia.pixel_to_world(pixel_pos[:, 1], pixel_pos[:, 0])

###############################################################################
# Let's plot the results.
fig = plt.figure()
ax = plt.subplot(projection=aia)
aia.plot()
ax.plot_coord(hpc_max, 'bx', color='white', marker='x', markersize=15)
plt.show()

###############################################################################
# Next, we create arrays for all of the pixels in the map.
x, y = np.meshgrid(*[np.arange(v.value) for v in aia.dimensions]) * u.pixel

###############################################################################
# Now we can convert this to helioprojective coordinates and create a new
# array which contains the normalized radial position for each pixel adjusted
# for the position of the brightest pixel (using `hpc_max`) and then define a
# new map.
hpc_mask = aia.pixel_to_world(x, y)
r_mask = np.sqrt((hpc_mask.Tx-hpc_max.Tx) ** 2 + (hpc_mask.Ty-hpc_max.Ty) ** 2) / aia.rsun_obs
mask = ma.masked_less_equal(r_mask, 0.1)
scaled_map = sunpy.map.Map(aia.data, aia.meta, mask=mask.mask)

###############################################################################
# Let's plot the results.
fig = plt.figure()
ax = plt.subplot(projection=scaled_map)
scaled_map.plot()
plt.show()
