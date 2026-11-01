"""Compatibility entry point: current garden art is authored at native size.

Previous painting reducer is archived in
art/herbal-garden/native-v13/before/scripts/painted_herbal_garden.py.
"""
import argparse
from native_herbal_garden import (
    INK, NAMES, LABELS, ASSETS, FRAME_MAP, crop_stages, herb, seed_packet,
    build_items, build_crops, export,
)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    export(parser.parse_args().install)
