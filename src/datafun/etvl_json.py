"""etvl_json.py - JSON ETVL pipeline.

Author: Denise Case
Author: Joseph Michael Tomasso
Date: 2026-08-23

Practice key Python skills related to:
    - ETVL pipeline structure (Extract, Transform, Verify, Load)
    - reading JSON files using the json module
    - walking JSON: dictionaries, lists, and nested structures
    - keyword-only function arguments
    - defensive programming for untrusted input
    - runtime type checking with isinstance()
    - writing results to a text file

OBS:
  This file is part of the working example project.
  First, run and understand the example as provided.
  When you take ownership of the project, adapt this pipeline
  to process data for your new problem.

RUN:
  No need.
  We don't usually run supporting modules like this one directly.
"""

# === DECLARE IMPORTS (BRING IN FREE CODE) ===

import json
import logging
from pathlib import Path
from typing import Any

# === SKILL: JSON DATA STRUCTURE ===

# JSON is a common format for exchanging data over the web.
# Python's json module reads JSON into native Python types:
#
#   JSON object  / Python dict   { "key": value }
#   JSON array   / Python list   [ value, value ]
#   JSON string  / Python str    "hello"
#   JSON number  / Python int or float
#   JSON boolean / Python bool   true / True
#   JSON null    / Python None
#
# JSON is hierarchical: lists and dicts can be nested inside each other.
# Example:
#   {
#     "people": [
#       { "name": "Oleg Kononenko", "craft": "ISS" },
#       { "name": "Jasmin Moghbeli", "craft": "ISS" }
#     ]
#   }
#
# json.load(file) returns the top-level structure - usually a dict.
# Use dict.get(key, default) to safely access keys that may be missing.


# === SKILL: DEFENSIVE PROGRAMMING FOR UNTRUSTED INPUT ===

# JSON is untrusted input: keys may be missing, values may be wrong types.
# Never assume a key exists. Never assume a value is the expected type.
# Use isinstance() to check types at runtime before using a value.
# Use dict.get(key, default) to handle missing keys without crashing.


# === E: EXTRACT ===


def extract_record_list(
    *,
    file_path: Path,
    list_key: str = "record",
) -> list[dict[str, Any]]:
    """E/V: Read JSON file and extract a list of dictionaries under list_key.

    Arguments:
        file_path: Path to input JSON file.
        list_key: Top-level key expected to map to a list (default: "Record").

    Returns:
        A list of dictionaries from the JSON file.
    """
    # Handle known possible error: no file at the path provided.
    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        # json.load() reads the entire file and returns a Python object.
        data: Any = json.load(f)

    # JSON top level should be a dict - verify before accessing keys.
    if not isinstance(data, dict):
        raise TypeError("Expected JSON top-level object to be a dictionary.")

    # Use dict.get() to safely retrieve the list - default to empty list if missing.
    value: Any = data.get(list_key, [])

    # Verify the value is a list before iterating.
    if not isinstance(value, list):
        raise TypeError(f"Expected {list_key!r} to be a list.")

    # Walk the list and keep only items that are dictionaries.
    # Each  record should be a dict with keys like "name" and "craft".
    record_list: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            record_list.append(item)  # type: ignore[arg-type]

    return record_list


# === T: TRANSFORM ===

# dict.get(key, default) returns the default if the key is missing.
# counts.get(craft, 0) + 1 increments the count for each craft name seen.
# This is a common pattern for counting occurrences in a list.


def transform_count_by_group(
    *,
    record_list: list[dict[str, Any]],
    group_key: str = "craft",
) -> dict[str, int]:
    """T: Count records by group.

    Arguments:
        record_list: List of record dictionaries.
        group_key: Key to read group name from (default: "craft").

    Returns:
        Dictionary mapping group names to counts.
    """
    counts: dict[str, int] = {}

    for record in record_list:
        # Use dict.get() to safely access the group key.
        group: Any = record.get(group_key, "Unknown")

        # Guard against non-string or empty values.
        if not isinstance(group, str) or not group.strip():
            group = "Unknown"

        # Increment the count for this group, starting at 0 if not yet seen.
        counts[group] = counts.get(group, 0) + 1

    return counts


# === V: VERIFY ===


def verify_counts(*, counts: dict[str, int]) -> None:
    """V: Verify counts are non-negative and group names are not empty.

    Arguments:
        counts: Dictionary mapping group names to counts.

    Returns:
        None.
    """
    for group, count in counts.items():
        # Handle known possible error: invalid group name.
        if not group.strip():
            raise ValueError(f"Invalid group name: {group!r}")

        # Handle known possible error: count is negative.
        if count < 0:
            raise ValueError(f"Invalid count for group {group!r}: {count}")


# === L: LOAD ===

# sorted() returns a new list in alphabetical order.
# This makes output consistent and predictable regardless of input order.


def load_counts_report(
    *,
    counts: dict[str, int],
    out_path: Path,
) -> None:
    """L: Write craft counts to a text file in data/processed.

    Arguments:
        counts: Dictionary mapping group names to counts.
        out_path: Path to output text file.

    Returns:
        None.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        f.write("Double-reed instruments by location\n")

        # Sort group names alphabetically for consistent, readable output.
        for group in sorted(counts):
            f.write(f"{group}: {counts[group]}\n")


# === CALL THIS PIPELINE FROM app.py ===

# The main app.py file declares the data-specific choices:
#
#   JSON_INPUT     = data/raw/astros.json
#   JSON_OUTPUT    = data/processed/json_astronauts_by_craft.txt
#   JSON_LIST_KEY  = people
#   JSON_CRAFT_KEY = craft
#
# app.py calls this function and passes those values in:
#
#   run_etvl_json(
#       input_file=JSON_INPUT,
#       output_file=JSON_OUTPUT,
#       list_key=JSON_LIST_KEY,
#       craft_key=JSON_CRAFT_KEY,
#       log=LOG,
#   )
#
# Each named argument provides one value this function needs.
# The parameter name is on the LEFT of =.
# The value declared in app.py is on the RIGHT.
#
# The * below means each argument must be passed by name.


# === FULL PIPELINE ===

# This function composes the four steps into a single callable pipeline.
# Each step receives the output of the previous step.
# The logger is passed in as an argument so this function works in any context.


def run_etvl_json(
    *,
    input_file: Path,
    output_file: Path,
    list_key: str,
    group_key: str,
    log: logging.Logger,
) -> None:
    """Run the full JSON ETVL pipeline.

    Arguments:
        input_file: Path to the input JSON file.
        output_file: Path to the output text file.
        list_key: Top-level key containing the list of records.
        craft_key: Key containing the craft name in each record.
        log: Logger for logging messages.

    Returns:
        None.
    """
    log.info("JSON: START")

    # E: Read raw data.
    record_list = extract_record_list(
        file_path=input_file,
        list_key=list_key,
    )

    # T: Count records by group.
    group_counts = transform_count_by_group(
        record_list=record_list,
        group_key=group_key,
    )

    # V: Verify results before writing.
    verify_counts(
        counts=group_counts,
    )

    # L: Write results to disk.
    load_counts_report(
        counts=group_counts,
        out_path=output_file,
    )

    log.info("JSON: wrote %s", output_file)
    log.info("JSON: END")
