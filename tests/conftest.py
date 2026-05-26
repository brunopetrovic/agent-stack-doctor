"""pytest configuration."""

import sys
from pathlib import Path

# Ensure the src package is on the path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))