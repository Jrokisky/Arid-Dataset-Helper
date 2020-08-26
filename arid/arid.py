import argparse
import json
import os
from pathlib import Path
import random


import matplotlib.pyplot as plt
from PIL import Image, ImageDraw


def get_wps(dataset_root, incl_rgb=True, incl_depth=True, incl_pcl=False):
    dataset_root = Path(dataset_root)

    wps = []
    for exp in dataset_root.iterdir():
        for wp in exp.iterdir():
            wp_title = wp.stem
            rgb = Path(wp / 'rgb') if incl_rgb else None
            depth = Path(wp / 'depth') if incl_depth else None
            pcl = Path(wp / 'pcl') if incl_pcl else None
            
            annotations = None
            try:
                with open(Path(wp / f'{wp_title}_labels.json')) as json_file:
                    annotations = json.load(json_file)
            except FileNotFoundError as e:
                # Skip this wp if there are no valid annotations
                continue
            wps.append(WP(wp_title, rgb, depth, pcl, annotations))

    return wps


def annotation_path(path, method_name):
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
    


def annotate_img(img, file_path, annotations):
    draw = ImageDraw.Draw(img)
    if annotations:
        for annotation in annotations:
            title = annotation['id'] if annotation['id'] else 'unknown'
            coords = annotation['coords']
            score = annotation['score']
            colormap = annotation.get('colormap', 'binary')
            draw.polygon(coords, outline=map_score_to_color(score, colormap))

            # Stagger text to avoid overlaps
            x = coords[0][0]
            y = coords[0][1]
            txt_y = coords[0][1] + (random.random() * 15)

            draw.text((coords[0][0], txt_y), title, fill=(255,255,255,255))

        img.save(file_path)
    pass


def map_score_to_color(score, colormap):
    cmap = plt.get_cmap(colormap)
    r, g, b, a = cmap(score)
    return (int(r*255), int(g*255), int(b*255))


class WP():

    def __init__(self, title, rgb, depth, pcl, annotations):
        self.title = title
        self.rgb_root = rgb
        self.depth_root = depth
        self.pcl_root = pcl
        self.annotations = annotations


    def get_title(self):
        return self.title


    def get_rgb_root(self):
        return self.rgb_root


    def rgb_image_paths(self):
        images = []
        if self.rgb_root.exists():
            for img_path in self.rgb_root.iterdir():
                if img_path.is_file():
                    images.append(img_path)
        return images


    def get_depth_root(self):
        return self.depth_root


    def get_pcl_root(self):
        return self.pcl_root


    def get_annotations(self, img_title):
        for annotation in self.annotations:
            if annotation['filename'] == f'img/{img_title}.png':
                return annotation['annotations']


    def __str__(self):
        return self.title
        
