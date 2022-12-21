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

from resizing import * 
from crop_image_from_center import * 
import argparse


def main():
    parser = argparse.ArgumentParser(description ='app description.')
    parser.add_argument('filename')          
    parser.add_argument('--output-image-dimensions', dest = 'output_image_size', help = 'width then height', nargs = 2, type = int, required = True)  
    parser.add_argument('--sector-image-size', dest = 'sector_image_side_size', type = int, required = True)  
    args = parser.parse_args()
    print(args.filename, args.output_image_size, args.sector_image_side_size)
    

    # What user gives us:
    # 1. reference_image, 2. output_image_size, 3. sector_image_side_size
    reference_image_name = args.filename
    output_image_size = args.output_image_size   #(1023, 681) but here it is an array
    sector_image_side_size = args.sector_image_side_size   # 15 , image side length / sectors count = 1000/50 = 20
      

    # What we calculate based on these data:
    # 1. reference_image_name
    # 2. new output image width and heigt 
    output_image_width = output_image_size[0]+1
    output_image_height = output_image_size[1]+1
    
    table_sectors_count = int(output_image_height / sector_image_side_size)
    raw_sectors_count =  int(output_image_width / sector_image_side_size)
    
    if output_image_width % sector_image_side_size != 0:
        raw_sectors_count = int(output_image_width / sector_image_side_size) # 66
        raw_pixels_to_cut = output_image_width % sector_image_side_size   # 10
        output_image_width = output_image_width - raw_pixels_to_cut # 66
        
    if output_image_height % sector_image_side_size != 0:
        table_sectors_count = int(output_image_height / sector_image_side_size) 
        table_pixels_to_cut = output_image_height % sector_image_side_size   
        output_image_height = output_image_height - table_pixels_to_cut 
        
    
    # setting new output img size   
    output_image_size = (output_image_width, output_image_height)
    output_image_width = output_image_size[0]-1
    output_image_height = output_image_size[1]-1


    if output_image_width > output_image_height:
        smaller_side = output_image_height
        larger_side = output_image_width
    else:
        smaller_side = output_image_width
        larger_side = output_image_height
    
    
    # print("output_image_size", output_image_size)

    folder_with_palette_photos = "/Users/mkarpava/Documents/3_photos"
    (palette_dominant_colors, palette_img_names) = scan_palette(folder_with_palette_photos, sector_image_side_size)
    save_palette_info_into_txt_file(palette_dominant_colors, palette_img_names, 'convert.txt')
    (all_names_of_img, all_rgb_of_img) = load_palette_info('convert.txt') 


    # 5. Crop a reference image:
    crop_image(reference_image_name, larger_side, smaller_side, "cropped_image.jpeg")

    grid_coordinates = find_grid_coordinates(raw_sectors_count, table_sectors_count)

    canvas = Image.new('RGB', output_image_size, (250,250,250))
    
    

    print("Filling sectors started ...")

    filled_sectors_count = 0
    for coordinate in grid_coordinates:
    # 8. count the coordinates where to insert the specific palette photo
        (left, top, right, bottom) = count_coordinates(coordinate, sector_image_side_size)

        # 9. take part of the reference which corresponds to the sector and save it to a temp image
        # (It will not change original image)
        resized_reference_image = Image.open(r"cropped_image.jpeg")
        reference_img_crop(resized_reference_image, left, top, right, bottom)
            
        # 10. Find dominant color of sector from step 9
        dominant_color = sector_dominant_color("sector_image.jpeg")

        # 11. find best match color for the sector image from the array of palette colors
        # 12. find the index and then name of the best match color for the sector image (in an array with dominant colors of all palette photos)
        dom_color_image_name_for_sector = find_name_of_sector_best_match_color(dominant_color, all_rgb_of_img, all_names_of_img)

        # 13. incert the best matching photo into the canvas by its name 
        best_matching_photo_into_canvas(folder_with_palette_photos, dom_color_image_name_for_sector, sector_image_side_size, canvas, left, top)

        filled_sectors_count += 1
        print("filled_sectors_count:", filled_sectors_count, "of", len(grid_coordinates))

    canvas.save("canvas_image.jpeg")

    print("Output image saved.")





# 1. iterate over palette photos in a folder_with_palette_photos: 
    # - save dominant colors of every photo in an array 
    # - save file names for every photo in an array
        # - indexes in both arrays corresponds to each other

def scan_palette(folder_with_palette_photos, sector_image_side_size):
    palette_dominant_colors = []
    palette_img_names = []

    for image in os.listdir(folder_with_palette_photos):
        if (image.endswith(".jpeg")):
            name = os.path.basename(image)
            palette_img_names.append(name)

            path_to_image = folder_with_palette_photos + "/" + name

            recize_and_crop_image(path_to_image, sector_image_side_size, "palette_img_for_color_thief.jpeg")

            color_thief = ColorThief("palette_img_for_color_thief.jpeg")
            dominant_color = color_thief.get_color(quality=1)
            palette_dominant_colors.append(dominant_color)

    return (palette_dominant_colors, palette_img_names)



# 2. save all this info into a file  
def save_palette_info_into_txt_file(palette_dominant_colors, palette_img_names, output_txt_file_name):
    palette_image_names_and_dom_colors = dict(zip(palette_img_names, palette_dominant_colors))

    with open(output_txt_file_name, 'w') as convert_file:
        convert_file.write(json.dumps(palette_image_names_and_dom_colors))





def load_palette_info(input_file):
    # 3. reading the data from the file 
    with open(input_file) as f:
        data = f.read()
        
    # reconstructing the data as a dictionary
    fromJS_palette_image_names_and_dom_colors = json.loads(data) 

    # 4. reconstructing the data into arrays 
    # TODO: I already have this arrays: palette_dominant_colors, palette_img_names
    all_names_of_img = [] 
    all_rgb_of_img = [] 

    for name, rgb in fromJS_palette_image_names_and_dom_colors.items(): 
        all_names_of_img.append(name)
        all_rgb_of_img.append(rgb)
    
    return (all_names_of_img, all_rgb_of_img)





def closest_color(rgb, all_rgb_of_img):
    r, g, b = rgb
    color_diffs = []
    for color in all_rgb_of_img:
        cr, cg, cb = color
        color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        color_diffs.append((color_diff, color))

    return min(color_diffs)[1]




def resize_reference_img(img_to_resize, output_image_size, new_img_name):
    im = img_to_resize.resize(output_image_size)
    im.save(new_img_name)
    Image.open(new_img_name)


# 6. find grid coordinates of sectors:
def find_grid_coordinates(raw_sectors_count, table_sectors_count):
    grid_coordinates = []
    
    for x in range(0, raw_sectors_count):      
        for y in range(0, table_sectors_count):        
            coordinate = []
            coordinate.append(x)
            coordinate.append(y)
            grid_coordinates.append(coordinate)

    # print("greed coordinates", grid_coordinates)
    return grid_coordinates




# How to rename i, a, b?
def count_coordinates(i, sector_image_side_size):
    coordinate = []

    x = i[0]*sector_image_side_size
    y = i[1]*sector_image_side_size
    coordinate.append(x)
    coordinate.append(y)
    
    a = coordinate[0]+sector_image_side_size-1
    b = coordinate[1]+sector_image_side_size-1
    coordinate.append(a)
    coordinate.append(b)

    left = coordinate[0]
    top = coordinate[1]
    right = coordinate[2]
    bottom = coordinate[3]

    return (left, top, right, bottom)


def reference_img_crop(reference_img, left, top, right, bottom):
    sector_image = reference_img.crop((left, top, right, bottom)) # this is PIL Image object, represents image
    sector_image.save(r"sector_image.jpeg")
    Image.open(r"sector_image.jpeg")
    

def sector_dominant_color(img_name):
    color_thief = ColorThief(img_name)
    dominant_color = color_thief.get_color(quality=1)
    os.remove(img_name) 

    return dominant_color



def find_name_of_sector_best_match_color(dominant_color, all_rgb_of_img, all_names_of_img):
    best_match_color = closest_color(dominant_color, all_rgb_of_img)
    
    index_of_best_match_color = -1
    for i in range(0, len(all_rgb_of_img)):
        if all_rgb_of_img[i] == best_match_color:
            index_of_best_match_color = i

    dom_color_image_name_for_sector = all_names_of_img[index_of_best_match_color]

    return  dom_color_image_name_for_sector


def best_matching_photo_into_canvas(folder_with_palette_photos, dom_color_image_name_for_sector, sector_image_side_size, canvas, left, top):
    image_path = folder_with_palette_photos + "/" + dom_color_image_name_for_sector
    img = Image.open(image_path, 'r')
    img.save(r"palette_img.jpeg")

    recize_and_crop_image(image_path, sector_image_side_size, "palette_img.jpeg")
    img = Image.open("palette_img.jpeg", 'r')

    canvas.paste(img, (left, top))

    return 



if __name__ == "__main__":
    main()


