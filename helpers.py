from PIL import Image


def crop_image(image_to_crop, new_larger_side, new_smaller_side, cropped_image):
    
    image = Image.open(image_to_crop)

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
        

def recize_and_crop_image(image_to_resize_and_crop, side_length, resized_and_croped_image):
    
    image = Image.open(image_to_resize_and_crop)

    width, height = image.size
    

    if width > height:
        smaller_side = height
        larger_side = width
    else:
        smaller_side = width
        larger_side = height

    factor = smaller_side / side_length

    smaller_side = side_length
    larger_side = round(larger_side / factor)
    
    if width > height:
        image_resized = image.resize((larger_side, smaller_side))
        image_resized.save(resized_and_croped_image)
    else:
        image_resized = image.resize((smaller_side, larger_side))
        image_resized.save(resized_and_croped_image)

    if width > height:
        left = (larger_side / 2) - (side_length / 2)
        upper = 0

        right = (larger_side / 2) + (side_length / 2)
        lower = side_length

        with Image.open(resized_and_croped_image) as im:
            im_crop = im.crop((left, upper, right, lower))
            im_crop.save(resized_and_croped_image)

    elif height > width:

        left = 0     
        upper = (larger_side / 2) - (side_length / 2)

        right = side_length    
        lower = (larger_side / 2) + (side_length / 2)

        with Image.open(resized_and_croped_image) as im:
            im_crop = im.crop((left, upper, right, lower))
            im_crop.save(resized_and_croped_image)

    elif height == width:

        left = 0     
        upper = 0

        right = side_length    
        lower = side_length

        with Image.open(resized_and_croped_image) as im:
            im_crop = im.crop((left, upper, right, lower))
            im_crop.save(resized_and_croped_image)
