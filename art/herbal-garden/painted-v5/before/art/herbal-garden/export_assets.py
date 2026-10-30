"""Export native 16x16 / 16x32 paintings without bitmap downscaling.
Compatibility entry point; the old sampler is archived in native-v2/before.
"""
from pathlib import Path
import argparse
import sys

PACK = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACK / "scripts"))
from native_herbal_garden import export


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true")
    export(parser.parse_args().install)
