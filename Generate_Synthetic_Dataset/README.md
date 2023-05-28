# Synthetic Dataset Generation

This repository provides a tool for generating synthetic datasets by combining background images and foreground images. The purpose of this tool is to create datasets for object detection projects. It allows you to randomly paste foreground images onto the specified areas of background images, generating a synthetic dataset with annotated objects.


## Usage

To generate a synthetic dataset, you need to provide background images and foreground images, along with their annotations. Follow the instructions below:

1. Prepare your background images:

   - Place your background images in the **Background_Images** directory.
   - Background images should be in common image formats such as PNG or JPG.

2. Prepare your foreground images:

   - Put your foreground images in the desired directory.
   - Foreground images must be in PNG format to preserve transparency.
   - Foreground image annotations must be in the form of a list of points representing a convex area in clockwise order.

3. Define the annotations for background images:

   - Background image annotations must be in JSON format, following the COCO annotation structure.
   - The annotations should specify the paste areas on the background images where the foreground images will be placed.
   - Each annotation should include the coordinates of the polygon vertices denoting the paste area.

4. Run the synthetic dataset generation script:



    python image_generation.py --n_images 10 --max_objects_per_image 5

-  the **--n_images** argument to specify the total number of images to be generated.
- Use the **--max_objects_per_image** argument to set the maximum number of objects to be added to each generated image.

5. The generated images will be saved in the **Generated_Images/images** directory, and the corresponding annotations will be saved in the **Generated_Images/labels** directory.

## Annotation Format

The annotations for background images must be provided in JSON format following the COCO annotation structure. Each annotation should contain the following information:

- **image**: The path to the background image file.
- **annotations**: A list of objects, where each object represents a paste area on the background image.
  - **category_id**: An identifier for the paste area category.
  - **segmentation**: A list of points representing a convex polygon denoting the paste area.

Example annotation for a background image JSON:

    {
      "image": "background_image1.png",
      "annotations": [
        {
          "category_id": 1,
          "segmentation": [[10, 20], [30, 40], [50, 60]]
        },
        {
          "category_id": 2,
          "segmentation": [[70, 80], [90, 100], [110, 120]]
        }
      ]
    }

Please ensure that the annotations are accurate and properly define the paste areas on the background images.
