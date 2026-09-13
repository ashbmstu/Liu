"""Launch the app from source. Usage: `python run.py` from this folder."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from liu_analyzer.app import main

sys.exit(main())
