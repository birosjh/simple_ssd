import os
import cv2
import json
import torch

import numpy as np
import imgaug.augmenters as iaa

from torch.utils.data import Dataset
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

class ImageDataset(Dataset):

    def __init__(self, data_config, transform):

        self.image_directory = data_config["image_directory"]

        self.transform = transform

        self.height = data_config["height"]
        self.width = data_config["width"]

        self.resize_transformation = iaa.Resize({
            "height": self.height,
            "width": self.width
        })

        with open(data_config["annotations"]) as file:
            annotations_file = file.read()

        annotation_json = json.loads(annotations_file)

        self.image_annotations = self.prep_images_and_annotations(
            annotation_json
        )

        self.images_list = list(self.image_annotations.keys())

        self.categories_by_id = self.prep_categories(
            annotation_json["categories"]
        )

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, idx):

        image_file = self.images_list[idx]

        path_to_file = os.path.join(self.image_directory, image_file)
        image = cv2.imread(path_to_file)

        labels = self.image_annotations[image_file]

        if self.transform:
            labels = BoundingBoxesOnImage(labels, shape=(self.height, self.width))

            image, labels = self.resize_transformation(
                image=image, 
                bounding_boxes=labels
            )
        
        labels = np.array([np.append(box.coords.flatten(), box.label) for box in labels.bounding_boxes])

        print(labels.shape)

        return (image, labels)

    def prep_images_and_annotations(self, annotation_json):

        # Split annotation_json
        images = annotation_json["images"]
        annotations = annotation_json["annotations"]

        # List images by image ID
        images_by_ids = {} 

        for image in images:
            images_by_ids[image["id"]] = image["file_name"]

        # Create a list of image_annotations
        image_annotations = {}

        for annotation in annotations:

            image_name = images_by_ids[
                annotation['image_id']
            ]

            # Create bounding box
            bounding_box = BoundingBox(
                x1=annotation['bbox'][0],
                y1=annotation['bbox'][1],
                x2=annotation['bbox'][0] + annotation['bbox'][2],
                y2=annotation['bbox'][1] + annotation['bbox'][3],
                label=annotation['category_id']
            )

            if image_name in image_annotations.keys():

                image_annotations[image_name].append(
                    bounding_box
                )

            else:
                image_annotations[image_name] = [bounding_box]

        return image_annotations

    def pair_images_with_annotations(self, images, annotations):

        image_ids_with_annotations = {}

        

        return image_ids_with_annotations

    def prep_categories(self, categories_json):

        categories_by_id = {}

        for category in categories_json:
            categories_by_id[category['id']] = category['name']

        return categories_by_id