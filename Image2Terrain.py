import math, time
import numpy as np
from PIL import Image

texturePath = "/Users/home/Downloads/Poland.png"
exportPath = "/Users/home/Downloads/PolandScaled.png"
cropAndSaveInput = False

start = time.time()
totalTime = 0

image = Image.open(texturePath).convert("RGBA") # Open input image
if cropAndSaveInput:
    image = image.crop(image.getbbox())
    image.save(texturePath)

data = np.array(image) # Convert image to array of shape (y, x, 4)
numAngles = 2 * (data.shape[0] + data.shape[1] - 2) # Bigger = better but takes longer to render
print(numAngles)
# 7500 seems good for Juventas Alpha
# Possible calc to absolutely guarantee all pixels are moved: 2 * (imgWidth + imgHeight - 2)? https://www.symbolab.com/solver/step-by-step/simplify%202x%2B2y-4?or=input

center = [data.shape[1]/2, data.shape[0]/2] # Get the center of the image
maxRadius = math.sqrt((center[0]*center[0])+(center[1]*center[1])) # Distance from any corner pixel to the center of the image

radii = np.empty((numAngles,),dtype=int)
yrange, xrange = range(data.shape[0]), range(data.shape[1])
start = time.time()

for a in range(numAngles):
    print(round(100*a/numAngles, 2), '\t', round((100*a/numAngles) / (time.time() - start), 2), '\t', time.time() - start)
    angle = math.tau * a / numAngles
    for r in range(int(maxRadius)):
        dy = int((r * math.sin(angle)) + center[0])
        dx = int((r * math.cos(angle)) + center[1])
        if dy not in yrange or dx not in xrange or data[dy,dx,3] == 0:
            radii[a] = r - 1
            break
        # data[dy,dx] = [255 * a/numAngles, 0, 255 * r/maxRadius, 255]

# Image.fromarray(data).show()
scales = np.nan_to_num(np.max(radii) / radii)
scales /= np.max(scales)
output = np.zeros(data.shape, dtype=data.dtype)
start2 = time.time()

for a in range(numAngles):
    print(round(100*a/numAngles, 2), '\t', round((100*a/numAngles) / (time.time() - start2), 2), '\t', time.time() - start2)
    angle = math.tau * a / numAngles
    for r in range(int(maxRadius)):
        dy = int((r * math.sin(angle)) + center[0])
        dx = int((r * math.cos(angle)) + center[1])
        if dy not in yrange or dx not in xrange or data[dy,dx,3] == 0:
            break
        
        sdy = int((scales[a] * r * math.sin(angle)) + center[0])
        sdx = int((scales[a] * r * math.cos(angle)) + center[1])
        output[sdy,sdx] = data[dy,dx]

outputImg = Image.fromarray(output)
outputImg = outputImg.crop(outputImg.getbbox())
outputImg.show()
outputImg.save(exportPath)
print("Took", time.time() - start, "seconds, used", numAngles, "different angles")