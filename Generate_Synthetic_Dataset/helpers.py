import os
import json
from pathlib import Path
import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps


def get_background_images_and_paste_areas():
    """
    This function reads the directory './Background_Images' and finds all PNG or JPG images stored alog with their JSON
    annotations file in COCO format (if available). It then returns a list of dictionaries where each dictionary
    represents an image and contains the image object, the path to the image file, and the list of vertices for the
    image's shape.

    Parameters:
    - None

    Returns:
    A list of dictionaries where each dictionary represents an image and contains the following information:
    'image'      : The image object in RGBA format.
    'image_path' : The path to the image file.
    'vertices'   : The list of vertices for the image's shape. If the image has no annotations,
                   the vertices will be the four corners of the image.
    """

    # Define the base directory and the path to the JSON annotation file
    base_dir = Path('./Background_Images/')
    json_dir = base_dir / 'annotations/instances_default.json'

    # Check if annotation file exists
    if os.path.exists(json_dir):
        # Load the JSON file with the shape vertices
        with open(json_dir, "r") as f:
            annotations = json.load(f)
    else:
        annotations = None

    # Create an empty list to store information about each image
    images = []

    # Loop through each file in the directory
    for file in os.listdir(base_dir):
        file_path = base_dir / Path(file)

        # Check if the file corresponds to an PNG or JPG image
        extension  = file_path.suffix

        # Check if the file is an image
        if (extension == '.png') or (extension == '.jpg'):
            image_path = file_path
            image_name = file_path.name  # with extension

            # Open the image file and convert it to RGBA format
            image = Image.open(image_path).convert("RGBA")

            # Initialize image annotation to the case were no annotations are available
            # If in the process annotations are found appropriate changes will be made
            image_id = None

            # Get the size of the image
            width, height = image.size

            # Define the default shape vertices to be the four corners of the image
            vertices = [[  0  ,    0  ],  # Top    right corner
                        [width,    0  ],  # Top    left  corner
                        [width, height],  # Bottom left  corner
                        [  0  , height]]  # Bottom right corner

            # Check if there is an available annotation for the chosen image
            if annotations:
                # Find the correct image in the annotations file
                for image_info in annotations['images']:
                    if image_info['file_name'] == image_name:
                        # Save the corresponding image id to retrieve the correct annotations
                        image_id = image_info['id']
                        break

                if image_id:
                    # Find the corresponding annotation for the image
                    for annot in annotations['annotations']:
                        if annot['id'] == image_id:
                            # Extract the list of vertices for the image's shape
                            annots_list = annot['segmentation'][0]
                            break

                    # Group the vertices into tuples of length 2: (x,y)
                    vertices = []
                    for i in range(0, len(annots_list), 2):
                        vertices.append((annots_list[i], annots_list[i + 1]))

            # Add the image, image path, and vertices to the list of images
            images.append({'image'     : image     ,
                           'image_path': image_path,
                           'vertices'  : vertices  ,
                           })

    # Return the list of images
    return images


def get_object(dim_multiplier=0.15):
    """
    The get_object function takes an optional argument dim_multiplier, which is used to resize the images and masks. It
    then loops through each folder in the directory and for each image file in the folder, it opens the image file and
    converts it to RGBA format. It then resizes the image based on the dim_multiplier argument and computes the
    bounding box of the object. It creates a mask by converting transparent pixels to black and non-transparent pixels
    to white, and saves the bounding box as a JSON file and the mask as an image. Finally, it appends the image, image
    path, id, label, bounding box, and mask to the list of objects and returns the list of objects.

    Parameters:
    - dim_multiplier: A float factor to multiply the dimensions of the object image.

    Returns:
    A list of objects where each dictionary represents an object and contains the following information:
    'image'      : The image object in RGBA format.
    'image_path' : The path to the image file.
    'idx'        : The object ID.
    'label'      : The name of object label.
    'bbox'       : The object bbox, format: {'left': int, 'top': int, 'width': int, 'height': int}).
    'bbox_path'  : The path to the JASON file containing the bbox information.
    'mask'       : The mask image, where white pixels represent the object and black pixels the background.
    'mask_path'  : The path to the PNG image of the mask.
    """

    # Set the base directory
    base_dir = Path('./Paste_Images/')

    # Create an empty list to store objects
    objects = []

    # Loop through each folder in the directory
    for idx, folder in enumerate(os.listdir(base_dir)):
        folder_path = base_dir / Path(folder)

        # Loop through each file in the folder
        for file in os.listdir(str(folder_path)):
            file_path = folder_path / file

            # Check if the file corresponds to an PNG image and not a mask file
            extension = file_path.suffix
            file_name = file_path.stem

            if (extension == '.png') and ('mask' not in file_name):
                image_path   = file_path
                image_name   = file_name
                image_parent = image_path.parent

                # Open the image file and convert it to RGBA format
                image = Image.open(image_path).convert("RGBA")

                # Compute the new size based on the dimension multiplier
                w, h  = image.size
                new_w = int(w * dim_multiplier)
                new_h = int(h * dim_multiplier)
                image = image.resize((new_w, new_h), Image.BOX)

                # # Split the image into color bands
                # red, green, blue, alpha = image.split()
                # Create an enhancer for the brightness and contrast ann Adjust
                image = ImageEnhance.Sharpness(image).enhance(-1.0)
                image = ImageEnhance.Color    (image).enhance( 0.5)
                # Merge the color bands back into an RGBA image
                # image = Image.merge('RGBA', (red, green, blue, alpha))
                # # Replace the RGB channels with the adjusted brightness and contrast channels
                # image = Image.merge('RGBA', (sharpness_enhancer.split()[:3] + (alpha,)))
                # image = Image.merge('RGBA', (color_enhancer.split()[:3]     + (alpha,)))

                # Compute the bounding box of the object
                bbox = {'left': 0, 'top': 0, 'width': new_w, 'height': new_h}

                # Create a mask by converting transparent pixels to black and non-transparent pixels to white
                img_arr = np.array(image)
                mask_arr = np.ones((new_h, new_w), dtype=np.uint8) * 255
                alpha = img_arr[:, :, 3]
                mask_arr[alpha == 0] = 0

                # Construct the output file names with the prefix of the original image name
                bbox_file_name = f'{image_name}_bbox.json'
                mask_file_name = f'{image_name}_mask.png'
                bbox_path = image_parent / bbox_file_name
                mask_path = image_parent / mask_file_name

                # Save the bounding box as a JSON file
                with open(bbox_path, 'w') as f:
                    json.dump(bbox, f)

                # Save the mask as an image
                mask_img = Image.fromarray(mask_arr, mode='L')
                mask_img.save(mask_path)

                # Add the image, image path, index, label, bounding box, and mask to the list of objects
                objects.append({'image'      : image     ,
                                'image_path' : image_path,
                                'idx'        : idx       ,
                                'label'      : folder    ,
                                'bbox'       : bbox      ,
                                'bbox_path'  : bbox_path ,
                                'mask'       : mask_img  ,
                                'mask_path'  : mask_path ,
                                })

    # Return the list of objects
    return objects


def apply_transformations(image):
    """
    This function applies random transformations to an input image, including rotation, scaling, brightness adjustment,
    and color shift.

    Parameters:
    - image: A PIL Image object representing the image to be transformed.

    Returns:
    A PIL Image object representing the transformed image.
    """

    # Define random transformation parameters
    rotation_angle    = random.uniform(-90.0, 90.0)
    scale_factor      = random.uniform(  0.8,  1.2)
    brightness_factor = random.uniform(  0.5,  1.5)  # 1.0: Original img,  0.0: Black      img, >1.0: Brighter  img
    color_factor      = random.uniform(  0.5,  1.2)  # 1.0: Original img,  0.0: B&W        img,  >1.0: Intenser  colors
    contrast_factor   = random.uniform(  0.5,  0.8)  # 1.0: Original img,  0.0: Total Grey img, >1.0: Contrast  img
    sharp_factor      = random.uniform( -0.8,  1.2)  # 1.0: Original img, <1.0: Blurred    img, >1.0: Sharpened img

    # Apply the transformations
    image = image.rotate(rotation_angle, resample=Image.BICUBIC, expand=True)
    image = image.resize((int(image.width * scale_factor), int(image.height * scale_factor)), resample=Image.BICUBIC)
    image = ImageEnhance.Brightness(image).enhance(brightness_factor)
    image = ImageEnhance.Color     (image).enhance(color_factor     )
    image = ImageEnhance.Contrast  (image).enhance(contrast_factor  )
    image = ImageEnhance.Sharpness (image).enhance(sharp_factor     )

    return image


def get_polygon_bounds(vertices):
    """
    This function takes a list of vertices defining a polygon and returns the bounding box
    coordinates of the polygon.

    Parameters:
    - vertices: A list of 2D coordinate tuples representing the vertices of the polygon.

    Returns:
    A tuple containing the (min_x, min_y, max_x, max_y) coordinates of the polygon's bounding box.
    """

    # Extract x and y coordinates of vertices
    x_coords = [int(v[0]) for v in vertices]
    y_coords = [int(v[1]) for v in vertices]

    # Calculate min and max x and y coordinates
    min_x = min(x_coords)
    max_x = max(x_coords)
    min_y = min(y_coords)
    max_y = max(y_coords)

    # Return bounding box coordinates as a tuple
    return min_x, min_y, max_x, max_y


def is_point_in_polygon(x, y, vertices):
    """
    This function determines if a point is inside a CONVEX polygon. It works by computing the cross product of the
    vector formed by the current vertex and the next vertex with the vector formed by the current vertex and the test
    point. If all cross products have the same sign, then the point is inside the polygon. Otherwise, it is outside.

    Parameters:
    - x: The x-coordinate of the point.
    - y: The y-coordinate of the point.
    - vertices: A list of tuples representing the vertices of the polygon, given in clockwise order.

    Returns:
    True if the point is inside the polygon, False otherwise.
    """

    # Get the point and the vertices as np.arrays
    point    = np.array([x, y])
    vertices = np.array(vertices)

    # The polygon is defined by its vertices in clockwise order
    sides         = np.roll(vertices, -1, axis=0) - vertices
    to_point      = point - vertices
    cross_product = np.cross(sides, to_point)

    # Returns if the point is inside the polygon
    return all(cross_product <= 0) or all(cross_product >= 0)


def get_random_point_in_polygon(vertices):
    """
    This function generates a random point inside a CONVEX polygon defined by the input vertices.

    Parameters:
    - vertices: List of (x, y) coordinates of the vertices of the polygon.

    Returns:
    list: [x, y] coordinates of a random point inside the polygon.
    """

    # Get the minimum and maximum x and y values of the polygon
    bounds = get_polygon_bounds(vertices)
    min_x, min_y, max_x, max_y = bounds

    # Loop until a random point inside the polygon is found
    while True:
        # Generate a random x coordinate within the polygon bounds
        x = random.randint(min_x, max_x)
        # Generate a random y coordinate within the polygon bounds
        y = random.randint(min_y, max_y)

        # Check if the random point is inside the polygon
        if is_point_in_polygon(x, y, vertices):
            # If the point is inside the polygon, return its coordinates
            return [x, y]


if __name__ == '__main__':
    pass
