from __future__ import annotations

import sys
from pathlib import Path

SECURITY_SOURCE = Path(__file__).parents[2] / "apps" / "api" / "src"
sys.path.insert(0, str(SECURITY_SOURCE))
