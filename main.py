#  importing Image class from PIL package
from PIL import Image
# import pyheif

# for finding dominant color:
import matplotlib.image as img
import matplotlib.pyplot as plt
from scipy.cluster.vq import whiten
from scipy.cluster.vq import kmeans
import pandas as pd

from colorthief import ColorThief
import requests
import seaborn as sns
from PIL import Image
from math import sqrt


# for dividing image into parts:
import numpy as np
from patchify import patchify
from PIL import Image



# for iteration on files in a folder
# import the modules
import os
from os import listdir

# for writing info to a file on a disc
import json


# iterate over files in folder and find dominant colors:
folder_dir = "/Users/mkarpava/Documents/3_photos"

dominant_colors = []
file_names = []

for image in os.listdir(folder_dir):
    if (image.endswith(".jpeg")):
        name = os.path.basename(image)
        file_names.append(name)

        path_to_image = folder_dir + "/" + name

        color_thief = ColorThief(path_to_image)
        dominant_color = color_thief.get_color(quality=1)
        dominant_colors.append(dominant_color)
       
imageName_domColor = dict(zip(file_names, dominant_colors))

with open('convert.txt', 'w') as convert_file:
     convert_file.write(json.dumps(imageName_domColor))




# reading the data from the file
with open('convert.txt') as f:
    data = f.read()
      
# reconstructing the data as a dictionary
fromJS_imageName_domColor = json.loads(data) 

# should return value by key
# print(fromJS_imageName_domColor['IMG_2747.jpeg'])

# todo: what order do we expect here? (:
all_names_of_img = [] 
all_rgb_of_img = [] 

for name, rgb in fromJS_imageName_domColor.items(): 
    all_names_of_img.append(name)
    all_rgb_of_img.append(rgb)



def closest_color(rgb):
    r, g, b = rgb
    color_diffs = []
    for color in all_rgb_of_img:
        cr, cg, cb = color
        color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        color_diffs.append((color_diff, color))

    return min(color_diffs)[1]


# Resize and crop an image with PIL:
# Opens a image in RGB mode
im = Image.open(r"car.jpeg")

# Size of the image in pixels (size of original image) for ex: width, height = im.size
width, height = im.size

newsize = (999, 999)
im = im.resize(newsize)
im.save(r"NewImage.jpeg")
Image.open(r"NewImage.jpeg")

sectors_count = 50 # количество секторов

# find grid coordinates of small squares:
grid_coordinates = []
for x in range(0, sectors_count):      
    for y in range(0, sectors_count):        
        coordinate = []
        coordinate.append(x)
        coordinate.append(y)
        grid_coordinates.append(coordinate)


img_step = 20 # 1000/50
print("grid_coordinates")
print(len(grid_coordinates))

# Create a canvas 
canvas = Image.new('RGB', (999, 999), (250,250,250))
canvas.save(r"canvasImage.jpeg")

all_coordinaes_for_small_square = []
for i in grid_coordinates:
    coordinate = []
    x = i[0]*img_step
    y = i[1]*img_step
    coordinate.append(x)
    coordinate.append(y)
    
    a = coordinate[0]+img_step-1
    b = coordinate[1]+img_step-1
    coordinate.append(a)
    coordinate.append(b)

    left = coordinate[0]
    top = coordinate[1]
    right = coordinate[2]
    bottom = coordinate[3]

    all_coordinaes_for_small_square.append(coordinate)

    # Cropped image of above dimension (It will not change original image)
    im1 = im.crop((left, top, right, bottom)) # this is PIL Image object, represents image
    im1.save(r"tempImage.jpeg")
    Image.open(r"tempImage.jpeg")
    # im1.show()
    
    image = ColorThief("tempImage.jpeg") # this is ColorThief object, represents image
    
    # Find dominant color
    color_thief = ColorThief("tempImage.jpeg")
    dominant_color = color_thief.get_color(quality=1)
    print("dominant_color:")
    print(dominant_color)

    os.remove("tempImage.jpeg") 

    # find dominant color
    # find the name of image with this dominant color

    best_match_color = closest_color(dominant_color)
    print("best_match_color:")
    print(best_match_color)

 
    index_of_best_match_color = -1
    for i in range(0, len(all_rgb_of_img)):
        if all_rgb_of_img[i] == best_match_color:
            index_of_best_match_color = i

    dom_color_image_name = all_names_of_img[index_of_best_match_color]
    print("dom_color_image_name:")
    print(dom_color_image_name)

    for image_name in os.listdir(folder_dir):
        print("image_name:")
        print(image_name)
        if image_name == dom_color_image_name:
            image_path = folder_dir + "/" + image_name

            print("image_path:")
            print(image_path)

            img = Image.open(image_path, 'r')

            newsize = (img_step, img_step)
            img = img.resize(newsize)

            canvas.paste(img, (left, top))
            canvas.save(r"canvasImage.jpeg")

            # os.remove("resized_img.jpeg") 


canvas.show()










