import argparse
import json
from pathlib import Path


from PIL import Image


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


def annotate_img(img, file_path, annotations):
    pass


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


    def rgb_images(self):
        images = {}
        for img_path in self.rgb_root.iterdir():
            if img_path.is_file():
                images[img_path.stem] = Image.open(img_path)
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
        
