from PIL import Image


def crop_image(image_to_crop, new_larger_side, new_smaller_side, cropped_image):
    
    image = Image.open(image_to_crop)
    # print(image.size)  # (800, 1200) - christmas

    width, height = image.size
    
    if width > height:
        smaller_side = height
        larger_side = width
    else:
        smaller_side = width
        larger_side = height
    

    if width > height:

        left = (larger_side / 2) - (new_larger_side / 2)
        upper = (smaller_side / 2) - (new_smaller_side / 2)

        right = (larger_side / 2) + (new_larger_side / 2)
        lower = (smaller_side / 2) + (new_smaller_side / 2)

        with Image.open(image_to_crop) as im:
            im_cropped = im.crop((left, upper, right, lower))
            im_cropped.save(cropped_image)


    elif height >= width:

        left = (smaller_side / 2) - (new_smaller_side / 2)    
        upper = (larger_side / 2) - (new_larger_side / 2)

        right = (smaller_side / 2) + (new_smaller_side / 2)    
        lower = (larger_side / 2) + (new_larger_side / 2)

        with Image.open(image_to_crop) as im:
            im_cropped = im.crop((left, upper, right, lower))
            im_cropped.save(cropped_image)
        
            
# crop_image("christmas.jpeg", 1100, 750, "cropped_image.jpeg")