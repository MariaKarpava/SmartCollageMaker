from PIL import Image


def recize_and_crop_image(image_to_resize_and_crop, side_length, resized_and_croped_image):
    
    image = Image.open(image_to_resize_and_crop)
    # print(image.size)  # (1280, 853) - car // (800, 1200) - christmas

    width, height = image.size
    

    if width > height:
        smaller_side = height
        larger_side = width
    else:
        smaller_side = width
        larger_side = height
    
    # то во сколько раз меньшая сторона моей фотки больше желаемой стороны квадрата
    factor = smaller_side / side_length # 1.706

    smaller_side = side_length
    larger_side = round(larger_side / factor)
    

    if width > height:
        image_resized = image.resize((larger_side, smaller_side))
        image_resized.save(resized_and_croped_image)
    else:
        image_resized = image.resize((smaller_side, larger_side))
        image_resized.save(resized_and_croped_image)

    
    """
    - найди средний пиксель 
         - его координаты = длина / 2 и ширина / 2
    - от него отсчитай координату верхнего левого угла
         - a от него координату нового верхнего левого угла
    """

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


# recize_and_crop_image("christmas.jpeg", 600, "resized_and_croped_image.jpeg")