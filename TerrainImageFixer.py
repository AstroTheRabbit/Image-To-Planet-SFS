import math, time
import numpy as np
from PIL import Image

texturePath = "/Users/home/Library/Application Support/Steam/steamapps/common/Spaceflight Simulator/SpaceflightSimulatorGame.app/Contents/Custom Solar Systems/Project Vulcan/Texture Data/JuventasAlphaSurface.png"
exportPath = "/Users/home/Library/Application Support/Steam/steamapps/common/Spaceflight Simulator/SpaceflightSimulatorGame.app/Contents/Custom Solar Systems/Project Vulcan/Texture Data/JuventasAlphaSurfaceScaled.png"
cropAndSaveInput = False

start = time.time()
totalTime = 0

image = Image.open(texturePath).convert("RGBA") # Open input image
if cropAndSaveInput:
    image = image.crop(image.getbbox())
    image.save(texturePath)

data = np.array(image) # Convert image to array of shape (y, x, 4)
center = [data.shape[0]/2, data.shape[1]/2] # Get the center of the image [y, x]
maxRadius = math.sqrt((center[0]*center[0])+(center[1]*center[1])) # Distance from any corner pixel to the center of the image

deltaPositions = np.argwhere(data[...,3] != 0) - center
maxTerrainRadius = np.max(np.sqrt(np.square(deltaPositions[:,0]) + np.square(deltaPositions[:,1])))

positions = np.indices(data.shape[0:2]) # Create array containing the positions of each pixel with shape (2, y, x)
positions = np.vstack(([positions[0].T], [positions[1].T])).T # Convert positions.shape to (y, x, 2): https://stackoverflow.com/a/4874230/14847250
deltaPositions = positions - center

radii = np.sqrt(np.square(deltaPositions[...,0]) + np.square(deltaPositions[...,1]))
angles = (math.tau - np.mod(np.arctan2(deltaPositions[...,0], deltaPositions[...,1]), math.tau)) / math.tau # Get angle of each pixel using arctan2

scales = np.nan_to_num(maxTerrainRadius / radii)
scales /= np.max(scales)

yrange, xrange = range(data.shape[0]), range(data.shape[1])
maxTerrainRadii = np.ndarray(radii.shape)

sincos = np.array((np.sin(angles), np.cos(angles))).T

z = np.einsum('...i,j->...ij', sincos, np.arange(maxRadius))
print(z.shape)
print(z)

# for sin, cos in np.nditer([np.sin(angles), np.cos(angles)]):
#     pos = [(np.arange(maxRadius) * sin + center[0]).astype(int), (np.arange(maxRadius) * cos + center[1]).astype(int)]
#     prev = [0,0]
#     for p in np.nditer(pos):
#         if p[0] not in yrange or p[1] not in xrange or data[p[0],p[1],3] == 0:
#             maxTerrainRadii[prev[0],prev[1]] = math.sqrt((prev[0]*prev[0])+(prev[1]*prev[1]))
#             break
#         prev = p

# # scales = np.broadcast_to(scales.T, (2,*scales.T.shape)).T
# # scaled = ((scales * deltaPositions) + center).astype(int)
# output = np.zeros(data.shape, dtype=data.dtype)
# output[scaled[...,0], scaled[...,1]] = data[positions[...,0], positions[...,1]]
# Image.fromarray(output).show()