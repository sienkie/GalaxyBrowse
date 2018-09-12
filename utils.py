from constants import *
import json
import subprocess


class GalaxyBrowseParseError(Exception):
    def __init__(self):
        self.message = 'Uncorrect syntax of configuration options file. Please refer to file description.'

    def __str__(self):
        return self.message


def get_default_data(ftype):
    if ftype == 'flat':
        return default_flatfile
    elif ftype == 'wiggle':
        return default_wiggle
    elif ftype == 'variant':
        return default_variant
    else:
        raise ValueError


def get_supported_data(ftype):
    if ftype == 'flat':
        return supported_flatfile
    elif ftype == 'wiggle':
        return supported_wiggle
    elif ftype == 'variant':
        return supported_variant
    else:
        raise ValueError


def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')


def check_track_labels(label_key, tracks_file):
    with open(tracks_file, 'r') as f:
        data = json.load(f)
        labels = []
        for file in data['tracks']:
            if 'label' in file.keys():
                labels.append(file['label'])
        return sum([1 if label_key in label else 0 for label in labels])
