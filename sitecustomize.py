"""
Auto-added to Python at startup if present on sys.path.
Ensures project root is importable when running scripts from tests/ or subfolders.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
