# Smart Collage Maker

## What is it?

**Smart Collage Maker** is a command line tool that allows you to combine your favourite photos into a work of art. You can create gorgeous collages, ready to print to canvas, share on social media and use as personalized photo gifts to loved ones.

This is also a Final Project for the [Harvard CS50x course](https://cs50.harvard.edu/x/2022).

The idea is:
  - You prepare a "palette" of images, which is large and diverse enough.
  - You pick a "reference" image.
  - The app will split the reference image into many small square sectors, for each of them it will find a best matching image from the palette and then assemble these images back into a single one.
  - The output image will look close to the reference image when looking from distance, but when zooming in you'll see that it comprises not of plain pixels but of other images.

## Demo

Video overview: https://youtu.be/6Ic8RDP9hZs

## How to use?

1). Install the dependencies

The project includes `requirements.txt` file, which lists all the dependencies (python packages) used by the app.
You can install them using `pip`: 

```
pip install -r requirements.txt
```

Note: you might benefit from creating a dedicated `venv` for this project and isntalling the dependencies there. 


2). Prepare and scan the palette

```
python smart_collage_maker.py scan-palette --folder-with-palette-photos /dir/with/palette/images
```

Note:
- Only `jpeg` is supported so far.
- Palette dir should not contain nested dirs (they'll be ignored).
- The output will be stored into `palette.json` in the same dir from where you launch the app.
- This file contains metadata about the scanned palette (dominant color for each image).
- This file will be (re)used at the next step. You can scan palette once and then experiment with building different collages later.


3). Build a collage representing reference image based on a palette

```
python smart_collage_maker.py build-image --folder-with-palette-photos /dir/with/palette/images -i /path/to/reference/image.jpeg -o /path/to/save/the/result/collage.jpeg -iss 10 -oss 100
```

Note:
- `palette.json` should be present in a current dir from where you launch the app
- `-iss`: sector size in the reference image
- `-oss`: sector size in the output image
- e.g. `-iss 10 -oss 100` means that the reference image will be split into `10x10` sectors, but the size of corresponding sector (and the image which fills it) in the collage will be `100x100`.


## Overview of the project files

- `smart_collage_maker.py`:
    - main logic and `main()` entry point live here
    - responsible for parsing command line arguments and executing one of the two commands based on the parsing result: either scan palette or build image.
    - uses Euclidean distance to compare colors.
- `helpers.py`:
    - contains helper-functions that can resize and/or crop images from the center.
- `colorthief_customised.py`:
    - Among other dependencies, the app uses `ColorThief` for calculating dominant colors, but unfortunately it wasn't working well with images which consist only from "too white" pixels, it was crashing in such cases.
    - This file contains slightly modified sources of original `ColorThief` (version '0.2.1') with the fix (the line responsible for filtering "too white" pixels was removed).
- `requirements.txt`
    - Produced by `pip freeze > requirements.txt`.
    - Contains the list of dependencies which are required for the app to work.
- `.gitignore`:
    - Tells git which files/dirs to ignore.
    - Lists generic items like `.DS_Store`, `.venv/*` and `.vscode/*`, as well as some other dirs and files which were handy to use during development.
- `Tmp/README.md`
    - This empty readmy was added purely to allow "Tmp" dir to be checked in to Git. The app needs this dir to be present during the execution. Users don't need to use any files from this dir.
- `README.md`
    - Current file, contains overview of the project.


## Design decisions

- Comparing sectors / paletter images by average color vs by dominant color:
  - Dominant is better as it is much closer to the color that out eyes recognise as the prevalent color on the photo. E.g. if an image consists of 2 equal rectangles, one red and the other one blue, then average will be purple, while there is no purple visible by human eye. Using dominant was a better choice based on experiments. 
- When scanning a palette, calculating dominant color based on the original-sized image or downsized?
  - Ideally, we don't want any downsizing in this context at all, but the problem which became noticeable during testing was that scanning full-size images was taking a considerable amount of time.
  - Experiments proved that downsizing an image will not affect its dominant color significantly.
  - Chose to downsize images if they are more than 500px.
- Scanning palette and building image in one go or as a 2 separate steps?
  - Decided to split into 2 separate steps.
  - Key motivator is that scanning palette might be very time consuming, and user might want to experiment how the same palette behaves with different reference images and sector sizes.
  - Having scanning as a separate step allows to do scanning once and then reuse the results.


## Potential future improvements

- Use multithreading to speed-up processing.
- For each sector in the output apply colored filter / overlay to make it look visually closer to the target color of the sector. 
- Support other popular image types.
- Support palette dirs containing nested dirs (scan them recursively).
- Saving intermediate progress and handle errors better. (e.g. now if saving output image fails then the whole progress is lost).
- Option to prevent / limit reusing the same palette image multiple times.
- Option to replace sector with a target color itself, rather than by palette image which is closest to this color.
