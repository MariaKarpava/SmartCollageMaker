from PIL import Image
from colorthief_customized import ColorThief
from math import sqrt
import time
import os
import json
from helpers import *
import argparse
import sys


def main():
    start_time = time.time()
    parse_arguments_and_execute_command()
    elapsed_seconds = time.time() - start_time
    print("Command finished. Elapsed time (sec):", elapsed_seconds)


def process_palette(folder_with_palette_photos):
    (palette_dominant_colors, palette_img_names) = scan_palette(folder_with_palette_photos)
    save_palette_info_into_json_file(palette_dominant_colors, palette_img_names, 'palette.json')
    return 


def build_image(
        output_image_sector_side_size,
        sector_image_side_size,
        reference_image_name,
        folder_with_palette_photos,
        output_filename):

    input_image_size =  Image.open(reference_image_name).size
    input_image_width = input_image_size[0]
    input_image_height = input_image_size[1]   

    height_sectors_count = int(input_image_height / sector_image_side_size)
    width_sectors_count =  int(input_image_width / sector_image_side_size)

    output_image_width =  width_sectors_count * output_image_sector_side_size
    output_image_height = height_sectors_count * output_image_sector_side_size
      
    adjusted_input_image_width = width_sectors_count * sector_image_side_size  
    adjusted_input_image_height = height_sectors_count * sector_image_side_size
        

    output_image_size = (output_image_width, output_image_height)
    output_image_width = output_image_size[0]
    output_image_height = output_image_size[1]


    if adjusted_input_image_width > adjusted_input_image_height:
        smaller_side = adjusted_input_image_height
        larger_side = adjusted_input_image_width
    else:
        smaller_side = adjusted_input_image_width
        larger_side = adjusted_input_image_height
       

    crop_image(reference_image_name, larger_side, smaller_side, "Tmp/cropped_image.jpeg")

    grid_coordinates = find_grid_coordinates(width_sectors_count, height_sectors_count)

    canvas = Image.new('RGB', output_image_size, (250,250,250))
    
    
    print("Filling sectors started ...")

    (all_names_of_img, all_rgb_of_img) = load_palette_info('palette.json') 

    filled_sectors_count = 0
    for coordinate in grid_coordinates:
        (input_left, input_top, input_right, input_bottom) = count_coordinates(coordinate, sector_image_side_size)
        (output_left, output_top, output_right, output_bottom) = count_coordinates(coordinate, output_image_sector_side_size)

        # Take part of the reference which corresponds to the sector and save it to a tmp image
        # (It will not change original image)
        resized_reference_image = Image.open(r"Tmp/cropped_image.jpeg")
        reference_img_crop(resized_reference_image, input_left, input_top, input_right, input_bottom)

        dominant_color = sector_dominant_color("Tmp/sector_image.jpeg")

        # Find best match color for the sector image from the array of palette colors
        # Find the index and then name of the best match color for the sector image (in an array with dominant colors of all palette photos)
        dom_color_image_name_for_sector = find_name_of_sector_best_match_color(dominant_color, all_rgb_of_img, all_names_of_img)

        # Insert the best matching photo into the canvas by its name 
        best_matching_photo_into_canvas(folder_with_palette_photos, dom_color_image_name_for_sector, output_image_sector_side_size, canvas, output_left, output_top)

        filled_sectors_count += 1
        print("filled_sectors_count:", filled_sectors_count, "of", len(grid_coordinates))

    canvas.save(output_filename)

    print("Output image saved.")


# Parse CL arguments and execute command (scan palette or build image).
# Returns name of the executed command.
def parse_arguments_and_execute_command():
    parser = argparse.ArgumentParser(
        description = """
            This apps allows to build a collage of images in a smart way: the collage itself will look like a reference image. 
            You first need to prepare a large enough 'palette' of images, scan them using 'scan-palette' command, and then 
            call 'build-image' command, passing palette metadata and a reference image. 
            The app will split the reference image into sectors and replace each sector with a best matching image from palette. 
            In result you'll get a new image which looks as close as possible to the reference one but consists from other images. """)
    
    if len(sys.argv) < 2 or (len(sys.argv) == 2 and sys.argv[1] == "-h"):
        print("Please specify a command you wish to run by passing it as an argument: 'scan-palette' or 'build-image'.")
        return

    command_name = sys.argv[1]

    if command_name == 'scan-palette':
        parser.add_argument('-fwpf', '--folder-with-palette-photos', dest = 'folder_with_palette_photos', required = True)  

        parse_all_other_arguments = parser.parse_args(sys.argv[2:])

        folder_with_palette_photos = parse_all_other_arguments.folder_with_palette_photos
             
        process_palette(folder_with_palette_photos)

        return 'scan-palette'

    elif command_name == 'build-image':
        parser.add_argument('-fwpf', '--folder-with-palette-photos', dest = 'folder_with_palette_photos', required = True)  
        parser.add_argument('-i', '--filename', required = True) 
        parser.add_argument('-o', '--output-filename', dest = 'output_filename', required = True)         
        parser.add_argument('-iss', '--input-sector-size', dest = 'sector_image_side_size', type = int, required = True)
        parser.add_argument('-oss', '--output-sector-size', dest = 'output_sector_size', type = int, required = True)    
        
        parse_all_other_arguments = parser.parse_args(sys.argv[2:])
        
        folder_with_palette_photos = parse_all_other_arguments.folder_with_palette_photos
        reference_image_name = parse_all_other_arguments.filename
        output_filename =  parse_all_other_arguments.output_filename
        sector_image_side_size = parse_all_other_arguments.sector_image_side_size
        output_sector_size = parse_all_other_arguments.output_sector_size

        build_image(output_sector_size,
                    sector_image_side_size,
                    reference_image_name,
                    folder_with_palette_photos,
                    output_filename)

        return 'build-image'

    else:
        return 'Unrecognized command'


def scan_palette(folder_with_palette_photos):
    palette_dominant_colors = []
    palette_img_names = []

    print("Scanning palette started...")
    
    scanned_count = 0
    all_files = os.listdir(folder_with_palette_photos)
    for image in all_files:
        if (image.endswith(".jpeg")):
            name = os.path.basename(image)
            palette_img_names.append(name)

            path_to_image = folder_with_palette_photos + "/" + name

            original_size = Image.open(path_to_image).size
            # We don't want to scan too large images, because it takes significant amount of time.
            # At the same time downsizing an image will not affect it's dominant color significantly.
            # So we downsize the image if it's larger than 500 to speed up the scanning.
            square_size = min(original_size[0], original_size[1], 500)
            
            recize_and_crop_image(
                path_to_image,
                square_size,
                "Tmp/palette_img_for_color_thief.jpeg")

            color_thief = ColorThief("Tmp/palette_img_for_color_thief.jpeg")
            dominant_color = color_thief.get_color(quality=1)
            palette_dominant_colors.append(dominant_color)

        scanned_count += 1
        print("scanned:", scanned_count, "of", len(all_files))

    return (palette_dominant_colors, palette_img_names)


def save_palette_info_into_json_file(palette_dominant_colors, palette_img_names, output_file_name):
    palette_image_names_and_dom_colors = dict(zip(palette_img_names, palette_dominant_colors))

    with open(output_file_name, 'w') as convert_file:
        convert_file.write(json.dumps(palette_image_names_and_dom_colors))


def load_palette_info(input_file):
    with open(input_file) as f:
        data = f.read()

    fromJS_palette_image_names_and_dom_colors = json.loads(data) 

    # Reconstructing the data into arrays 
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
        # Calculate 3D Euclidean distance to compare colors.
        color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        color_diffs.append((color_diff, color))

    return min(color_diffs)[1]


def resize_reference_img(img_to_resize, output_image_size, new_img_name):
    im = img_to_resize.resize(output_image_size)
    im.save(new_img_name)
    Image.open(new_img_name)


def find_grid_coordinates(width_sectors_count, height_sectors_count):
    grid_coordinates = []
    
    for x in range(0, width_sectors_count):      
        for y in range(0, height_sectors_count):        
            coordinate = []
            coordinate.append(x)
            coordinate.append(y)
            grid_coordinates.append(coordinate)

    return grid_coordinates


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
    # PIL crops excluding right column and bottom row, hence "+ 1" to include them.
    sector_image = reference_img.crop((left, top, right + 1, bottom + 1))
    sector_image.save(r"Tmp/sector_image.jpeg")
    Image.open(r"Tmp/sector_image.jpeg")
    

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
    img.save(r"Tmp/palette_img.jpeg")

    recize_and_crop_image(image_path, sector_image_side_size, "Tmp/palette_img.jpeg")
    img = Image.open("Tmp/palette_img.jpeg", 'r')

    canvas.paste(img, (left, top))

    return 


if __name__ == "__main__":
    main()
