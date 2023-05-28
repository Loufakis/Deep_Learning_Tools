import numpy as np
import random
from PIL import Image
from helpers import *
from tqdm import tqdm
import argparse


def main(itterastions, max_objects_per_image=5):
    generated_images_dir      = Path('./Generated_Images/images')
    generated_annotations_dir = Path('./Generated_Images/labels')


    # Initialize Random Seed
    random.seed(0)

    # Read the background images
    background_imgs = get_background_images_and_paste_areas()

    # Read the object images
    object_imgs = get_object()

    for itter in tqdm(range(itterastions)):
        # Choose a random background image (randomly)
        background_data =  random.choice(background_imgs)

        # print(f'Chosen image: {background_data["image_path"].name}')

        # Load the background image and the vertices of the paste area
        background_img        = background_data['image'].copy()
        background_paste_area = background_data['vertices']

        # initialize object list
        object_list = []

        # Choose number of object images to paste
        n_object_images = random.randint(1, max_objects_per_image)
        # print(f'Number of object: {n_object_images}')
        for _ in range(n_object_images):
            # Choose an object image (randomly)
            object_data   = random.choice(object_imgs)
            object_idx    = object_data['idx'  ]
            object_label  = object_data['label']
            object_img    = object_data['image'].copy()  # PIL Image
            width, height = object_img.size

            # Modify the object image
            object_img = apply_transformations(object_img)

            # Choose a random point inside the paste area of the background image
            point = get_random_point_in_polygon(background_paste_area)

            # Update object list
            object_list.append(f'{object_idx} {point[0]} {point[1]} {width} {height}')  # index x y width height


            # Create a new transparent image of the same size as the foreground image
            mask = Image.new("L", object_img.size, 255)

            # Set the opacity level (0-255) for the non-transparent part of the foreground image
            opacity = 0.9
            opacity = int(opacity * 255)

            # Iterate over each pixel in the mask and set the opacity level for non-transparent pixels
            for y in range(object_img.height):
                for x in range(object_img.width):
                    if object_img.getpixel((x, y))[3] == 0:  # Check if pixel is transparent
                        mask.putpixel((x, y), 0)  # Set pixel to fully transparent
                    else:
                        mask.putpixel((x, y), opacity)  # Set pixel to desired opacity

            # Paste the chosen image onto the random point
            background_img.paste(object_img, point, mask)

        output_txt_dir = generated_annotations_dir / f'{itter}.txt'
        output_img_dir = generated_images_dir      / f'{itter}.png'

        # Save the annotation TXT
        with open(output_txt_dir, "w") as file:
            for objt in object_list:
                file.write(f"{objt}\n")

        # Save the resulting image
        background_img.save(output_img_dir)


if __name__ == '__main__':
    # Get needed arguments with parser
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--n_images', type=int, required=False, default=10,
                        help=" The total number of images that will be generated")
    parser.add_argument('--max_objects_per_image', type=int, required=False, default=5,
                        help="the maximum number of objects that will be added to each generated image")

    args = parser.parse_args()
    n_images = args.n_images
    max_objects_per_image = args.max_objects_per_image

    # Generate Images
    main(itterastions=n_images, max_objects_per_image=max_objects_per_image)