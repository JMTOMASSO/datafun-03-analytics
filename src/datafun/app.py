"""src/datafun/app.py - Project script.

Author: Denise Case
Author: Joseph Michael Tomasso
Date: 2026-08-23

HOW TO RUN THIS FILE:

From the VS Code menu (with only this project open in VS Code),
click "Terminal" / New Terminal to
open an integrated Terminal in the root project folder.
Paste the following command and press ENTER or RETURN
to run this file as a script:

uv run python -m datafun.app

DOMAIN:

This project illustrates how the workflow is similar
even when the data is very different.
It uses four datasets, each in a different file format.

- CSV:  fictional double reed inventory
- JSON: astronauts currently in space, by spacecraft
- XLSX: student feedback text
- TXT:  a plain-text version of Romeo and Juliet

Paths (relative to repo root):

INPUT FILE:  data/raw/double_reed_inventory.csv
INPUT FILE:  data/raw/astros.json
INPUT FILE:  data/raw/Feedback.xlsx
INPUT FILE:  data/raw/romeo_and_juliet.txt

OUTPUT FILE: data/processed/csv_inventory_stats.txt
OUTPUT FILE: data/processed/json_astronauts_by_craft.txt
OUTPUT FILE: data/processed/xlsx_feedback_github_count.txt
OUTPUT FILE: data/processed/txt_summary.txt

EXPLORE:

Raw data usually needs work before it can be trusted.
An ETVL pipeline moves data through four stages:

- Extract: read raw values from a source file
- Transform: calculate results from the raw values
- Verify: check the results before writing them
- Load: write the verified results to an output file

The file format and the transform differ for each dataset,
but the four ETVL stages remain the same.

DESIGN:

Use this file to declare the data-specific choices
and the reasoning behind them,
then orchestrate the work.
The format-specific ETVL pipelines live in supporting modules.
"""


# === DECLARE IMPORTS (BRING IN FREE CODE) ===

import logging
from pathlib import Path
from typing import Final

from datafun_toolkit.logger import get_logger, log_header, log_path

from datafun.etvl_csv import run_etvl_csv
from datafun.etvl_json import run_etvl_json
from datafun.etvl_text import run_etvl_text
from datafun.etvl_xlsx import run_etvl_xlsx

# === CONFIGURE LOGGER ONCE FOR THE APPLICATION ===

LOG: logging.Logger = get_logger("P03", level="DEBUG")

# === LOCATE THE DATA FOLDERS ===

# Use the Path() constructor and the / operator to build
# relative paths to the input and output folders.
RAW_DIR: Final[Path] = Path("data") / "raw"
PROCESSED_DIR: Final[Path] = Path("data") / "processed"

# === CSV: SUMMARIZE A NUMERIC COLUMN ===

CSV_PIPELINE_DESCRIPTION: Final[str] = r"""
Read the fictional double reed inventory CSV file,
extract the current value column,
calculate descriptive statistics,
verify the results,
and write the statistics to a text file.
"""

CSV_INPUT: Final[Path] = RAW_DIR / "double_reed_inventory.csv"
CSV_OUTPUT: Final[Path] = PROCESSED_DIR / "csv_age_value_stats.txt"
CSV_COLUMN: Final[str] = "current_value"  # CUSTOM
WHY_CSV_COLUMN: Final[str] = r"""
Current value provides a useful first summary of the financial value
of the fictional double reed inventory before comparing value with age.
"""

# === JSON: COUNT RECORDS BY A CATEGORY ===

JSON_PIPELINE_DESCRIPTION: Final[str] = r"""
Read the astronauts JSON file,
extract the list of people,
count people by spacecraft,
verify the results,
and write the counts to a text file.
"""

JSON_INPUT: Final[Path] = RAW_DIR / "double_reed_locations.json"
JSON_OUTPUT: Final[Path] = PROCESSED_DIR / "json_instruments_by_location.txt"
JSON_LIST_KEY: Final[str] = "instruments"  # CUSTOM
JSON_GROUP_KEY: Final[str] = "location"  # CUSTOM
WHY_JSON_GROUPING: Final[str] = r"""
Each instrument is assigned to a location, so counting by location shows
how the instruments are distributed across different areas.
"""

# === XLSX: COUNT A WORD IN A COLUMN ===

XLSX_PIPELINE_DESCRIPTION: Final[str] = r"""
Read the feedback Excel file,
extract text from the selected column,
count occurrences of the selected word,
verify the result,
and write the count to a text file.
"""

XLSX_INPUT: Final[Path] = RAW_DIR / "double_reed_maintenance.xlsx"
XLSX_OUTPUT: Final[Path] = PROCESSED_DIR / "xlsx_repair_count.txt"
XLSX_COLUMN: Final[str] = "A"
XLSX_WORD: Final[str] = "repair"
WHY_XLSX_WORD: Final[str] = r"""
We are counting the instances of repair to see how often maintenance is needed for the double reed instruments.
"""

# === TEXT: SUMMARIZE A DOCUMENT ===

TXT_PIPELINE_DESCRIPTION: Final[str] = r"""
Read the double reed maintenance notes text file,
count its lines, words, and characters,
verify the results,
and write the summary to a text file.
"""

TXT_INPUT: Final[Path] = RAW_DIR / "double_reed_maintenance_notes.txt"
TXT_OUTPUT: Final[Path] = PROCESSED_DIR / "txt_maintenance_summary.txt"
WHY_TXT_SUMMARY: Final[str] = r"""
Line, word, and character counts give a quick size profile
of a plain-text document before any deeper reading.
"""

# === DEFINE THE MAIN FUNCTION ===

# === CALL THE PIPELINE FUNCTIONS ===

# Each imported pipeline function needs information to do its work.
# We pass that information using named arguments.
# In Python, every argument after a asterisk in a function definition
# MUST be passed by keyword, e.g. input_file=CSV_INPUT.
#
# For example:
#
# run_etvl_csv(
#     input_file=CSV_INPUT,
#     output_file=CSV_OUTPUT,
#     column_name=CSV_COLUMN,
#     log=LOG,
# )
#
# The parameter name is on the LEFT of =.
# The value we declared above is on the RIGHT.
#
# All pipeline calls follow this same pattern.
# When you do a custom project, you can keep these
# data sources - or for a more interesting project,
# find a new set of data sources to work with.


def main() -> None:
    """Entry point when running this file as a Python script.

    This is where the instructions begin.

    Arguments: None.
    Returns: None.
    """
    log_header(LOG, "P03")

    LOG.info("===================================")
    LOG.info("START main()")
    LOG.info("===================================")

    log_path(LOG, "raw folder", path=RAW_DIR)
    log_path(LOG, "processed folder", path=PROCESSED_DIR)

    # Ensure the output folder exists before any pipeline writes to it.
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    LOG.info("===================================")
    LOG.info("CSV pipeline")
    LOG.info("===================================")

    LOG.info(f"Pipeline: {CSV_PIPELINE_DESCRIPTION}")
    LOG.info(f"Column: {CSV_COLUMN}")
    LOG.info(f"Why: {WHY_CSV_COLUMN}")
    run_etvl_csv(
        input_file=CSV_INPUT,
        output_file=CSV_OUTPUT,
        column_name=CSV_COLUMN,
        log=LOG,
    )

    LOG.info("===================================")
    LOG.info("JSON pipeline")
    LOG.info("===================================")

    LOG.info(f"Pipeline: {JSON_PIPELINE_DESCRIPTION}")
    LOG.info(f"Grouping: {JSON_LIST_KEY} by {JSON_GROUP_KEY}")
    LOG.info(f"Why: {WHY_JSON_GROUPING}")
    run_etvl_json(
        input_file=JSON_INPUT,
        output_file=JSON_OUTPUT,
        list_key=JSON_LIST_KEY,
        group_key=JSON_GROUP_KEY,
        log=LOG,
    )

    LOG.info("===================================")
    LOG.info("XLSX pipeline")
    LOG.info("===================================")

    LOG.info(f"Pipeline: {XLSX_PIPELINE_DESCRIPTION}")
    LOG.info(f"Word: {XLSX_WORD} in column {XLSX_COLUMN}")
    LOG.info(f"Why: {WHY_XLSX_WORD}")
    run_etvl_xlsx(
        input_file=XLSX_INPUT,
        output_file=XLSX_OUTPUT,
        column_letter=XLSX_COLUMN,
        word=XLSX_WORD,
        log=LOG,
    )

    LOG.info("===================================")
    LOG.info("TEXT pipeline")
    LOG.info("===================================")

    LOG.info(f"Pipeline: {TXT_PIPELINE_DESCRIPTION}")
    LOG.info(f"Why: {WHY_TXT_SUMMARY}")
    run_etvl_text(
        input_file=TXT_INPUT,
        output_file=TXT_OUTPUT,
        log=LOG,
    )

    LOG.info("===================================")
    LOG.info("END main() - Executed successfully!")
    LOG.info("===================================")


# === CONDITIONAL EXECUTION GUARD ===

# WHY: This is standard Python "boilerplate" - we copy and paste it
# into every Python script. It is a "conditional execution" guard,
# meaning: if this file is being run as a script, then execute the code
# in the main() function.

if __name__ == "__main__":
    main()
