# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import json
from datetime import datetime
from pathlib import Path
from typing import Any

VECTORS_DIR = Path(__file__).parent.parent / "test-vectors"


def load_vectors(name: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = json.loads((VECTORS_DIR / name).read_text())["cases"]
    return cases


def parse_instant(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value)
