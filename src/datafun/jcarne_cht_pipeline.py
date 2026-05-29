"""jcarne_cht_pipeline.py - CHT ETVL pipeline.

Author: Jereme Carne
Date: 2026-05

  Practice key Python skills related to:
    - ETVL pipeline structure (Extract, Transform, Verify, Load)
    - reading CSV files using the csv module
    - keyword-only function arguments
    - error handling with raise
    - calculating statistics with the statistics module
    - writing results to a text file

  Paths (relative to repo root):

    INPUT FILE:  data/raw/dynon_data.csv
    OUTPUT FILE: data/processed/cht_stats.txt

  Terminal command to run this file from the root project folder:

    uv run python -m datafun.jcarne_cht_pipeline

"""

# === DECLARE IMPORTS (BRING IN FREE CODE) ===

import csv
import statistics
from pathlib import Path
from typing import Any

# === E: EXTRACT ===


def extract_cht_values(*, file_path: Path) -> list[float]:
    """E: Read CSV and extract all four CHT columns as floats.

    Arguments:
        file_path: Path to input CSV file.

    Returns:
        List of float values from all four CHT columns.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    cht_columns = ["CHT 1 (deg C)", "CHT 2 (deg C)", "CHT 3 (deg C)", "CHT 4 (deg C)"]
    values: list[float] = []

    with file_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Check all four CHT columns are present.
        for col in cht_columns:
            if reader.fieldnames is None or col not in reader.fieldnames:
                raise KeyError(
                    f"CSV missing expected column '{col}'. Found: {reader.fieldnames}"
                )

        for row in reader:
            for col in cht_columns:
                raw_value = (row.get(col) or "").strip()
                if not raw_value:
                    continue
                try:
                    values.append(float(raw_value))
                except ValueError:
                    continue

    return values


# === T: TRANSFORM ===


def transform_cht_stats(*, values: list[float]) -> dict[str, float]:
    """T: Calculate CHT statistics across all four cylinders in Fahrenheit.

    Arguments:
        values: List of float values from all CHT columns (in Celsius).

    Returns:
        Dictionary with keys: count, min, max, mean (converted to Fahrenheit).
    """
    if not values:
        raise ValueError("No numeric CHT values found for analysis.")

    def to_f(c: float) -> float:
        return (c * 9 / 5) + 32

    return {
        "count": float(len(values)),
        "min": to_f(min(values)),
        "max": to_f(max(values)),
        "mean": to_f(statistics.mean(values)),
    }


# === V: VERIFY ===


def verify_cht_stats(*, stats: dict[str, float]) -> None:
    """V: Sanity-check the CHT stats dictionary.

    Arguments:
        stats: Dictionary with statistics to verify.

    Returns:
        None
    """
    required = {"count", "min", "max", "mean"}
    missing = required - set(stats.keys())
    if missing:
        raise KeyError(f"Missing stats keys: {sorted(missing)}")

    if stats["count"] <= 0:
        raise ValueError("Count must be positive.")

    if stats["min"] > stats["max"]:
        raise ValueError("Min cannot be greater than max.")


# === L: LOAD ===


def load_cht_report(*, stats: dict[str, float], out_path: Path) -> None:
    """L: Write CHT stats to a text file in data/processed.

    Arguments:
        stats: Dictionary with statistics to write.
        out_path: Path to output text file.

    Returns:
        None
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        f.write("Dynon Flight Data - CHT Statistics\n")
        f.write(f"Total Readings: {int(stats['count'])}\n")
        f.write(f"Minimum CHT: {stats['min']:.1f} deg F\n")
        f.write(f"Maximum CHT: {stats['max']:.1f} deg F\n")
        f.write(f"Average CHT: {stats['mean']:.1f} deg F\n")


# === FULL PIPELINE ===


def run_cht_pipeline(*, raw_dir: Path, processed_dir: Path, logger: Any) -> None:
    """Run the full CHT ETVL pipeline.

    Arguments:
        raw_dir: Path to data/raw directory.
        processed_dir: Path to data/processed directory.
        logger: Logger for logging messages.

    Returns:
        None
    """
    logger.info("CHT: START")

    input_file = raw_dir / "dynon_data.csv"
    output_file = processed_dir / "cht_stats.txt"

    # E: Read raw data.
    values = extract_cht_values(file_path=input_file)

    # T: Calculate statistics.
    stats = transform_cht_stats(values=values)

    # V: Verify results before writing.
    verify_cht_stats(stats=stats)

    # L: Write results to disk.
    load_cht_report(stats=stats, out_path=output_file)

    logger.info("CHT: wrote %s", output_file)
    logger.info("CHT: END")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    from pathlib import Path

    run_cht_pipeline(
        raw_dir=Path("data/raw"),
        processed_dir=Path("data/processed"),
        logger=logger,
    )
