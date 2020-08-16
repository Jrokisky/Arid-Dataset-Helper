import argparse
import configparser
import json
from pathlib import Path



def main():
    parser = argparse.ArgumentParser(description='Access the ARID database')
    parser.add_argument('--config', type=str, default='config.ini')
    args = parser.parse_args()
    build_wps(args.config)
    

def build_wps(config_path):
    config = configparser.ConfigParser()
    try:
        with open(config_path) as config_file:
            config.read_file(config_file)
    except FileNotFoundError as e:
        print(f'Config file not found')

    dataset_root = config['Dataset'].get('root', './dataset')
    dataset_root = Path(dataset_root).resolve()

    incl_rgb = config['Dataset'].getboolean('include_rgb', True)
    incl_depth = config['Dataset'].getboolean('include_depth', True)
    incl_pcl = config['Dataset'].getboolean('include_pcl', False)

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
            wps.append(WP(rgb, depth, pcl, annotations)

    return wps


class WP():

    def __init__(self, rgb, depth, pcl, annotations):
        self.rgb_root = rgb
        self.depth_root = depth
        self.pcl_root = pcl
        self.annotations = annotations


    def get_rgb_root(self):
        return self.rgb_root


    def get_depth_root(self):
        return self.depth_root


    def get_pcl_root(self):
        return self.pcl_root


    def get_annotations(self):
        return self.annotations
        

if __name__ == '__main__':
    main()
