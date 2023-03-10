import math, time, os
import numpy as np
from PIL import Image

texturePath = "/Users/home/Downloads/Poland.png"
exportPath = "/Users/home/Downloads/PolandHeightmap.png"

exportColor = [0,0,0,255] # Color of the output heightmap image in 0 to 255 RGBA, purely cosmetic (unless you set A to 0 which will make the heightmap flat).
cropAndSaveInput = True # Crops any empty space borders around your input image.
planetRadius = 500 # Radius of your planet.

outputRes = (2000, 3000) # Resolution of the output heightmap:
# X would preferably the circumfrence of the planet or smaller,
# but if it's too high holes/bumps will start forming (especially if the resoulution of the input image is small)
# Higher Y values are better for planets with more variance in terrain, but may have similar downsides to high X values.
# but note that the Y resolution gets cropped down, so the output image is usually slightly shorter.

# !! DO NOT EDIT ANYTHING BELOW THIS UNLESS YOU KNOW WHAT YOU ARE DOING !!

start = time.time()
totalTime = 0

image = Image.open(texturePath).convert("RGBA") # Open input image
if cropAndSaveInput:
    image = image.crop(image.getbbox())
    image.save(texturePath)
data = np.array(image) # Convert image to array of shape (y, x, 4)

polarTransform = np.full((outputRes[1], outputRes[0]), False) # Create array to store the polar transformed pixels
center = [data.shape[1]/2, data.shape[0]/2] # Get the center of the image
maxRadius = math.sqrt((center[0]*center[0])+(center[1]*center[1])) # Distance from any corner pixel to the center of the image

positions = np.indices(data.shape[0:2]) # Create array containing the positions of each pixel with shape (2, y, x)
positions = np.vstack(([positions[0].T], [positions[1].T])).T # Convert positions.shape to (y, x, 2): https://stackoverflow.com/a/4874230/14847250

dy = np.take(positions, 0, axis=2) - center[1] # Y position relative to the center of the image
dx = np.take(positions, 1, axis=2) - center[0] # X position relative to the center of the image
radii = (maxRadius - np.sqrt(np.add(np.square(dx), np.square(dy)))) / maxRadius # Get radius of each pixel using Pythagorean theorem
angles = (math.tau - np.mod(np.arctan2(dy, dx), math.tau)) / math.tau # Get angle of each pixel using arctan2

mask = np.take(data, 3, axis=2) # Get alpha values of input image
mask = np.where(mask != 0, False, True) # Convert to booleans depending on alpha values

print(time.time() - start,"seconds to calculate radii, angles and mask")
totalTime += time.time() - start
start = time.time()

polarCoords = np.stack((np.floor(radii*polarTransform.shape[0])-1, np.floor(angles*polarTransform.shape[1])-1), axis=2) # Creates a (y, x, 2) array with the polar coordinates of the pixel as the values
indexCoords = polarCoords.reshape(-1, 2).astype(int) # Flatten polarCoords and convert to int
indexCoords = np.delete(indexCoords, mask.reshape(-1), axis=0) # Apply mask
polarTransform[tuple([*indexCoords.T])] = True # Place pixels in polar transform array

# Image.fromarray(polarTransform).show()

print(time.time() - start,"seconds for polar transform")
totalTime += time.time() - start
start = time.time()

border = np.empty((*polarTransform.shape, 4), dtype='uint8') # Create final image array
lowest, highest = 0, polarTransform.shape[0] # Create crop border variables

for a in range(polarTransform.shape[1]):
    # print("Final editing | ", round(100*a/polarTransform.shape[1], 1), '% Complete | Time Elapsed: ', round(time.time() - start2, 1), " seconds", sep='')
    flag = False
    for r in range(polarTransform.shape[0]):
        if polarTransform[r,a] and not flag:
            flag = True
            if r > lowest:
                lowest = r
            if r < highest:
                highest = r
        if flag:
            border[r,a] = exportColor

border = np.flip(border[highest:lowest], axis=1) # Apply crop and flip image

print(time.time() - start,"seconds for gap filling, min/max finding and cropping")
totalTime += time.time() - start

Image.fromarray(border).save(exportPath)
Image.fromarray(border).show()
print("\nRender took", totalTime, "seconds.")

lowest = polarTransform.shape[0] - lowest
highest = polarTransform.shape[0] - highest

terrainHeight = planetRadius * ((highest - lowest) / lowest)
print(f"For the planet radius of {planetRadius}, use this terrain formula: \"OUTPUT = AddHeightMap({exportPath.split(os.sep)[-1]}, {planetRadius * math.tau}, {terrainHeight})\"\n")