# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
import os

# Returns numpy image at size imageSize*imageSize
def getProcessedData(img, imageSize):
    img = img.resize((imageSize, imageSize), resample=Image.ANTIALIAS)
    imgData = np.asarray(img, dtype=np.uint8).reshape(imageSize, imageSize, 1)
    imgData = imgData / 255.
    return imgData


# Returns numpy image at size imageSize*imageSize
def getImageData(filename, imageSize):
    img = Image.open(filename)
    imgData = getProcessedData(img, imageSize)
    return imgData


def createDatasetFromSlicesPredict(sliceSize,path):
    data = []

    # Get slices in genre subfolder
    filenames = os.listdir(path)
    filenames = [filename for filename in filenames if filename.endswith('#part.png')]
    #print(filenames)

    # Add data (X,y)
    for filename in filenames:
        #print(filename)
        fileid = int(filename.split("#")[1])  # bluesboogiewoogie.00056.wav_18.png
        #print(fileid)
        imgData = getImageData(path+ "/" + filename, sliceSize)
        data.append((imgData, fileid))


    # Extract X and y
    data.sort(key=lambda tup: tup[1])
    # print(data[0])
    X, y = zip(*data)
    test_X = np.array(X).reshape([-1, sliceSize, sliceSize, 1])
    test_y = np.array(y)
    # print("......................................................")
    # print(y)
    # print("......................................................")
    return test_X, test_y
