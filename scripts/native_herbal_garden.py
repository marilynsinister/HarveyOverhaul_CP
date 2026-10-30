"""Compatibility entry point for the current painted botanical assets.

The native-v4 integer drawings are archived in
art/herbal-garden/painted-v5/before/scripts/native_herbal_garden.py.
"""
import argparse

from painted_herbal_garden import (
    INK, NAMES, LABELS, crop_stages, herb, seed_packet, build_items, build_crops, export,
)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    export(parser.parse_args().install)
