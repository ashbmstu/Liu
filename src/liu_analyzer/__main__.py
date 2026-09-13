"""Entry point for `python -m liu_analyzer` or direct execution."""
from __future__ import annotations

import sys

if __package__:
    from .app import main
else:
    # Running as a script (e.g. `python __main__.py`); put src/ on sys.path
    # so `liu_analyzer.app` resolves.
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from liu_analyzer.app import main

if __name__ == "__main__":
    sys.exit(main())
