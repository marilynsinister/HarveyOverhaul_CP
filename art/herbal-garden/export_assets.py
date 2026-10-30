"""Reduce the current large botanical paintings and add the game-pixel contour."""
from pathlib import Path
import argparse
import sys

PACK = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACK / "scripts"))
from painted_herbal_garden import export


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true")
    export(parser.parse_args().install)
