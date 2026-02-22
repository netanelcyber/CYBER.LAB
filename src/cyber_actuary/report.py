from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def write_xlsx(path: Path, df: pd.DataFrame) -> None:
    """Write a DataFrame to an XLSX file. Requires openpyxl.

    This creates parent directories if needed and writes the DataFrame
    using pandas' Excel writer.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Let pandas select the engine (openpyxl) and raise a clear error if missing.
    df.to_excel(path, index=False)
