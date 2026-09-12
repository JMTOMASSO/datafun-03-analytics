r"""src/datafun/utils_etvl.py - Reusable ETVL pipeline utilities.

Author: Denise Case
Author: Joseph Michael Tomasso
Date: 2026-08-20

Purpose:

Provide reusable ETVL pipeline mechanics that can be used
throughout the Data Analytics Fundamentals course.

ETVL:

- Extract: read raw values from a source
- Transform: calculate results from the raw values
- Verify: check the results before writing
- Load: write the verified results to a destination

These functions:

- receive the values they need through arguments
- return useful values when possible
- avoid project-specific global variables
- report progress through a logger passed in

OBS: You should read, but should not need to modify this file.

RUN:
  No need.
  We don't usually run supporting modules like this one directly.
"""

# === DECLARE IMPORTS (BRING IN FREE CODE) ===

import csv
import logging
from pathlib import Path
import statistics

# === E: EXTRACT ===


def extract_csv_rows(
    *,
    file_path: Path,
    log: logging.Logger,
) -> list[dict[str, str]]:
    """E: Read a CSV file into a list of row dictionaries.

    Arguments:
        file_path: Path to the source CSV file.
        log: Logger used to report progress.

    Returns:
        List of rows, each a dictionary keyed by column name.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    with file_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file does not contain a header.")

        rows = list(reader)

    log.info(f"Extracted {len(rows)} rows from {file_path.name}")

    return rows


# === T: TRANSFORM ===


def transform_column_to_floats(
    *,
    rows: list[dict[str, str]],
    column_name: str,
    log: logging.Logger,
) -> list[float]:
    """T: Convert one column of raw string rows into floats.

    Empty and non-numeric values are skipped.

    Arguments:
        rows: CSV rows represented as dictionaries.
        column_name: Column to convert to floats.
        log: Logger used to report progress.

    Returns:
        List of valid numeric values.
    """
    values: list[float] = []
    skipped: int = 0

    for row in rows:
        raw_value = (row.get(column_name) or "").strip()
        if not raw_value:
            skipped += 1
            continue
        try:
            values.append(float(raw_value))
        except ValueError:
            skipped += 1

    log.info(f"Converted {len(values)} values, skipped {skipped}, from '{column_name}'")

    return values


def transform_years_to_ages(
    *,
    rows: list[dict[str, str]],
    column_name: str,
    current_year: int,
    log: logging.Logger,
) -> list[float]:
    """T: Convert manufacturing years into instrument ages.

    Arguments:
        rows: CSV rows represented as dictionaries.
        column_name: Column containing the manufacturing year.
        current_year: Year used to calculate instrument age.
        log: Logger used to report progress.

    Returns:
        List of calculated instrument ages.
    """
    ages: list[float] = []
    skipped: int = 0

    for row in rows:
        raw_value = (row.get(column_name) or "").strip()

        if not raw_value:
            skipped += 1
            continue

        try:
            year_manufactured = int(raw_value)
            instrument_age = current_year - year_manufactured
            ages.append(float(instrument_age))
        except ValueError:
            skipped += 1

    log.info(
        f"Calculated {len(ages)} instrument ages, "
        f"skipped {skipped}, from '{column_name}'"
    )

    return ages


def transform_column_to_stats(
    *,
    values: list[float],
    log: logging.Logger,
) -> dict[str, float]:
    """T: Calculate basic statistics for a list of floats.

    Arguments:
        values: List of numeric values.
        log: Logger used to report progress.

    Returns:
        Dictionary with keys: count, min, max, mean, stdev.
    """
    if not values:
        raise ValueError("No numeric values found for analysis.")

    stats = {
        "count": float(len(values)),
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        # stdev() requires at least two values; use 0.0 for a single value.
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }

    log.info(f"Calculated statistics: {stats}")

    return stats


# === V: VERIFY ===


def verify_stats(
    *,
    stats: dict[str, float],
    log: logging.Logger,
) -> None:
    """V: Sanity-check the statistics before writing them.

    Arguments:
        stats: Dictionary of statistics to verify.
        log: Logger used to report progress.

    Returns:
        None.

    Raises:
        KeyError: If required keys are missing.
        ValueError: If the values are not internally consistent.
    """
    required = {"count", "min", "max", "mean", "stdev"}
    missing = required - set(stats)
    if missing:
        raise KeyError(f"Missing stats keys: {sorted(missing)}")

    if stats["count"] <= 0:
        raise ValueError("Count must be positive.")

    if stats["min"] > stats["max"]:
        raise ValueError("Min cannot be greater than max.")

    log.info("Verified statistics: all checks passed.")


# === L: LOAD ===


def load_age_value_report(
    *,
    age_stats: dict[str, float],
    value_stats: dict[str, float],
    out_path: Path,
    log: logging.Logger,
) -> None:
    """L: Write instrument age and current value statistics to a text file.

    Arguments:
        age_stats: Descriptive statistics for instrument age.
        value_stats: Descriptive statistics for current value.
        out_path: Path to the output report.
        log: Logger used to report progress.

    Returns:
        None.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report = (
        "Double Reed Inventory Analysis\n"
        "\n"
        "Instrument Age\n"
        f"Count: {int(age_stats['count'])}\n"
        f"Minimum: {age_stats['min']:.2f} years\n"
        f"Maximum: {age_stats['max']:.2f} years\n"
        f"Mean: {age_stats['mean']:.2f} years\n"
        f"Standard Deviation: {age_stats['stdev']:.2f} years\n"
        "\n"
        "Current Value\n"
        f"Count: {int(value_stats['count'])}\n"
        f"Minimum: ${value_stats['min']:.2f}\n"
        f"Maximum: ${value_stats['max']:.2f}\n"
        f"Mean: ${value_stats['mean']:.2f}\n"
        f"Standard Deviation: ${value_stats['stdev']:.2f}\n"
    )

    out_path.write_text(report, encoding="utf-8")

    log.info(f"Wrote age and value report to {out_path.name}")


def load_stats_report(
    *,
    stats: dict[str, float],
    column_name: str,
    out_path: Path,
    log: logging.Logger,
) -> None:
    """L: Write the statistics to a text file.

    Arguments:
        stats: Dictionary of statistics to write.
        column_name: Name of the summarized column.
        out_path: Path to the output text file.
        log: Logger used to report progress.

    Returns:
        None.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as file:
        file.write(f"Statistics for column: {column_name}\n")
        file.write(f"Count: {int(stats['count'])}\n")
        file.write(f"Minimum: {stats['min']:.2f}\n")
        file.write(f"Maximum: {stats['max']:.2f}\n")
        file.write(f"Mean: {stats['mean']:.2f}\n")
        file.write(f"Standard Deviation: {stats['stdev']:.2f}\n")

    log.info(f"Wrote report to {out_path.name}")
