"""Export the current native botanical pixel maps without resizing."""
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
