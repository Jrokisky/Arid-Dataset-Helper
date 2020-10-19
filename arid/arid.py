import argparse
import json
import os
from pathlib import Path
import random


import matplotlib.pyplot as plt
from PIL import Image, ImageDraw


def get_wps(dataset_root, incl_rgb=True, incl_depth=True, incl_pcl=False):
    """Build WP objects from the given dataset root.

    WP objects represent a single "scene" in the dataset. It's a collection
    of images that are the result of panning a camera over a scene. There is
    a single annotation file per WP.
    """
    dataset_root = Path(dataset_root)

    wps = []
    for exp in dataset_root.iterdir():
        for wp in exp.iterdir():
            wp_title = wp.stem
            rgb = Path(wp / 'rgb') if incl_rgb else None
            depth = Path(wp / 'depth') if incl_depth else None
            pcl = Path(wp / 'pcl') if incl_pcl else None

            if incl_rgb and not rgb.exists():
                continue

            methods = []
            for method in wp.iterdir():
                if method.is_dir() and str(method.stem) not in ['rgb', 'depth', 'pcl']:
                    methods.append(method)
            
            annotations = None
            annotations_path = Path(wp / f'{wp_title}_labels.json')
            try:
                with open(annotations_path) as json_file:
                    annotations = json.load(json_file)
                wps.append(WP(wp_title, rgb, depth, pcl, methods, annotations, annotations_path))
            except FileNotFoundError as e:
                # Skip this wp if there are no valid annotations
                print(f'{annotations_path} either could not be loaded or does not exist')
                continue

    return wps


def annotation_path(path, method_name):
    """Replaces the second to last item in the given path with the
    given method name. This is used to replace the 'rgb' dir name
    with the given bounding method name.
    """
    if isinstance(path, str):
        path = Path(path)
    parts = list(path.parts)
    file_name = parts.pop()
    curr_dir = parts.pop()
    parts.append(method_name)

    path = Path(*parts)
    if not path.exists():
        os.mkdir(path)

    return Path(path / file_name)
    


def annotate_img(img, file_path, annotations, save=True):
    """Draw bounding polygons on the given img.
    """
    draw = ImageDraw.Draw(img)
    if annotations:
        for annotation in annotations:
            title = annotation['id'] if annotation['id'] else 'unknown'
            coords = annotation['coords']
            score = annotation['score']
            colormap = annotation.get('colormap', 'binary')
            _coords = list(map(lambda c: (c[0], c[1]), coords))
            draw.polygon(_coords, outline=map_score_to_color(score, colormap))

            # Stagger text to avoid overlaps
            x = coords[0][0]
            y = coords[0][1]
            txt_y = coords[0][1] + (random.random() * 15)

            draw.text((x, txt_y), f'{title}-{str(int(score*100))}', fill=(255,255,255,255))

        if save:
            img.save(file_path)
    pass


def hide_crops(img, file_path, annotations, save=True):
    """Remove sections of an image.
    """
    draw = ImageDraw.Draw(img)
    if annotations:
        for annotation in annotations:
            coords = annotation['coords']
            _coords = list(map(lambda c: (c[0], c[1]), coords))
            draw.rectangle(_coords, fill="#ffffff")
        if save:
            img.save(file_path)
    pass


def map_score_to_color(score, colormap):
    cmap = plt.get_cmap(colormap)
    r, g, b, a = cmap(score)
    return (int(r*255), int(g*255), int(b*255))


def compute_bbox_iou(coords1, coords2):
    # Assumes all inputs are the coordinates for the corners of a bounding box.
    if len(coords1) != 4 or len(coords2) != 4:
        return False

    (ax1, ay1), (ax2, ay1), (ax2, ay2), (ax1, ay2) = coords1
    (bx1, by1), (bx2, by1), (bx2, by2), (bx1, by2) = coords2

    # No intersection at all.
    if ax1 > bx2 or bx1 > ax2 or ay1 > by2 or by1 > ay2:
        return 0

    # Compute the intersection
    min_right = min(ax2, bx2)
    max_left = max(ax1, bx1)
    intersection_width = min_right - max_left
    
    # (0,0) is in the top right corner of the image.
    max_top = max(ay1, by1)
    min_bottom = min(ay2, by2)
    intersection_height = min_bottom - max_top

    intersection_area = intersection_width * intersection_height
    if intersection_area == 0:
        return 0

    a_width = ax2 - ax1
    a_height = ay2 - ay1
    a_area = a_width * a_height

    b_width = bx2 - bx1
    b_height = by2 - by1
    b_area = b_width * b_height

    union_area = (a_area + b_area) - intersection_area

    return intersection_area / union_area



class WP():

    def __init__(self, title, rgb, depth, pcl, methods, annotation_data, annotations_path):
        self.title = title
        self.rgb_root = rgb
        self.depth_root = depth
        self.pcl_root = pcl
        self.method_roots = methods
        self.annotation_data = annotation_data
        self.keyed_annotations = {}
        for image_annotations in annotation_data:
            self.keyed_annotations[image_annotations['filename']] = image_annotations
        self.annotations_path = annotations_path


    def get_key(self):
        # generates a unique id for this wp that maintains sort order.
        prefix, session, waypoint, y = self.title.split("_")
        return int(session) * 1000 + int(waypoint) * 100 +  int(y) 


    def get_title(self):
        return self.title


    def get_rgb_root(self):
        return self.rgb_root

    
    def get_method_names(self):
        # Gets the methods used to generate annotated images.
        method_names = []
        for method_root in self.method_roots:
            method_names.append(method_root.stem)
        return method_names


    def method_image_paths(self):
        # Get image paths keyed by the method used to produce them.
        images = {}
        for method_root in self.methods_roots:
            method_name = method_root.stem
            images[method_name] = []
            for img_path in method_root.iterdir():
                if img_path.is_file():
                    images[method_name].append(img_path)
        return images


    def rgb_image_paths(self):
        # Get paths for all rgb images in this wp.
        images = []
        if self.rgb_root.exists():
            for img_path in self.rgb_root.iterdir():
                if img_path.is_file():
                    images.append(img_path)
        images = sorted(images, key=lambda i: int(i.stem))
        return images


    def get_depth_root(self):
        return self.depth_root


    def get_pcl_root(self):
        return self.pcl_root


    def get_annotations(self, img_title):
        # Get ground truth annotations for the given img.
        img_title = f'img/{img_title}.png'
        return self.keyed_annotations[img_title]


    def get_images_with_object(self, object_name):
        imgs = []
        for img, annotation_data in self.keyed_annotations.items():
            annotations = annotation_data['annotations']
            for annotation in annotations:
                if annotation.get('id') is None:
                    continue
                elif annotation['id'].startswith(object_name):
                    p = Path(self.rgb_root / Path(img).name)
                    imgs.append({
                        'path': p,
                        'annotation': annotation
                    })
        return imgs


    def __str__(self):
        return self.title
        
