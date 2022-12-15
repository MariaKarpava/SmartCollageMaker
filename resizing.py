from PIL import Image


def my_center_crop(img, side_length):

    image = Image.open(img)
    print(image.size)  # (1280, 853) - car // (800, 1200) - christmas

    width, height = image.size
    print("w:", width)
    print("h:", height)

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
    print("larger_side:", larger_side)
    print("smallew_side:", smaller_side)

    if width > height:
        image_resized = image.resize((larger_side, smaller_side))
        image_resized.save(r"image_resized.jpeg")
    else:
        image_resized = image.resize((smaller_side, larger_side))
        image_resized.save(r"image_resized.jpeg")

    print(image_resized.size)
    image_resized.show()
    
    """
    - найди средний пиксель 
         - его координаты = длина / 2 и ширина / 2
    - от него отсчитай координату верхнего левого угла
         - a от него координату нового верхнего левого угла
    """

    if width > height:
        new_x_left = (larger_side / 2) - (side_length / 2)
        new_y_upper = 0

        new_x_right = (larger_side / 2) + (side_length / 2)
        new_y_left_lower = side_length

        print("new_x_left ", new_x_left)
        print("new_y_upper", new_y_upper)
        print("new_x_right", new_x_right)
        print("new_y_left_lower", new_y_left_lower)

        with Image.open("image_resized.jpeg") as im:
            (left, upper, right, lower) = (new_x_left, new_y_upper, new_x_right, new_y_left_lower)
            im_crop = im.crop((left, upper, right, lower))

    elif height > width:

        new_x_left = 0     
        new_y_upper = (larger_side / 2) - (side_length / 2)

        new_x_right = side_length    
        new_y_left_lower = (larger_side / 2) + (side_length / 2)

        print("new_x_left ", new_x_left)
        print("new_y_upper", new_y_upper)
        print("new_x_right", new_x_right)
        print("new_y_left_lower", new_y_left_lower)

        with Image.open("image_resized.jpeg") as im:
            (left, upper, right, lower) = (new_x_left, new_y_upper, new_x_right, new_y_left_lower)
            im_crop = im.crop((left, upper, right, lower))

    elif height == width:

        new_x_left = 0     
        new_y_upper = 0

        new_x_right = side_length    
        new_y_left_lower = side_length

        print("new_x_left ", new_x_left)
        print("new_y_upper", new_y_upper)
        print("new_x_right", new_x_right)
        print("new_y_left_lower", new_y_left_lower)

        with Image.open("image_resized.jpeg") as im:
            (left, upper, right, lower) = (new_x_left, new_y_upper, new_x_right, new_y_left_lower)
            im_crop = im.crop((left, upper, right, lower))


    print("im_crop.size", im_crop.size)
    im_crop.show()


my_center_crop("christmas.jpeg", 600)