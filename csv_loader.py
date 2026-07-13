from __future__ import annotations

import csv
import io
from typing import Any, Optional


def clean_column_names(
    original_columns: list[str],
) -> list[str]:
    """
    Remove surrounding spaces and make duplicate column names unique.
    """

    column_counts: dict[str, int] = {}
    cleaned_columns: list[str] = []

    for original_column in original_columns:
        base_name = str(original_column).strip()

        if not base_name:
            base_name = "Unnamed Column"

        column_counts[base_name] = (
            column_counts.get(base_name, 0) + 1
        )

        if column_counts[base_name] == 1:
            cleaned_columns.append(base_name)

        else:
            cleaned_columns.append(
                f"{base_name}_{column_counts[base_name]}"
            )

    return cleaned_columns


def decode_uploaded_file(
    file_bytes: bytes,
) -> tuple[Optional[str], Optional[str]]:
    """
    Decode CSV bytes using common text encodings.
    """

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ]

    errors_seen: list[str] = []

    for encoding in encodings:
        try:
            decoded_text = file_bytes.decode(
                encoding
            )

            return decoded_text, None

        except UnicodeDecodeError as error:
            errors_seen.append(
                f"{encoding}: {error}"
            )

    return None, (
        "FigureForge could not decode this CSV. "
        "Save the file using UTF-8 encoding and try again. "
        + "; ".join(errors_seen[-2:])
    )


def detect_delimiter(
    decoded_text: str,
) -> str:
    """
    Detect commas, tabs, semicolons, or pipe delimiters.
    Defaults to a comma when detection fails.
    """

    sample = decoded_text[:4096]

    try:
        dialect = csv.Sniffer().sniff(
            sample,
            delimiters=",;\t|",
        )

        return dialect.delimiter

    except csv.Error:
        return ","


def load_csv(
    uploaded_file,
) -> tuple[
    Optional[dict[str, Any]],
    Optional[str],
]:
    """
    Safely load a CSV without pandas or PyArrow.

    Returns:
        {
            "columns": list[str],
            "rows": list[dict[str, str]],
            "row_count": int,
            "column_count": int,
        },
        error_message
    """

    if uploaded_file is None:
        return None, "No CSV file was uploaded."

    try:
        file_bytes = uploaded_file.getvalue()

    except Exception as error:
        return None, (
            "FigureForge could not access the uploaded file. "
            f"Details: {type(error).__name__}: {error}"
        )

    if not file_bytes:
        return None, "The uploaded CSV is empty."

    decoded_text, decoding_error = decode_uploaded_file(
        file_bytes
    )

    if decoding_error:
        return None, decoding_error

    if decoded_text is None:
        return None, "The CSV could not be decoded."

    delimiter = detect_delimiter(
        decoded_text
    )

    try:
        text_stream = io.StringIO(
            decoded_text
        )

        reader = csv.reader(
            text_stream,
            delimiter=delimiter,
        )

        raw_rows = list(reader)

    except csv.Error as error:
        return None, (
            "FigureForge could not parse this CSV. "
            f"Details: {error}"
        )

    except MemoryError:
        return None, (
            "The uploaded CSV is too large to load into memory."
        )

    except Exception as error:
        return None, (
            "FigureForge encountered an unexpected CSV error. "
            f"Details: {type(error).__name__}: {error}"
        )

    if not raw_rows:
        return None, "The CSV does not contain any rows."

    raw_columns = raw_rows[0]

    if len(raw_columns) < 2:
        return None, (
            "The CSV must contain at least two columns."
        )

    columns = clean_column_names(
        raw_columns
    )

    data_rows = raw_rows[1:]

    cleaned_rows: list[dict[str, str]] = []

    for row_number, row in enumerate(
        data_rows,
        start=2,
    ):
        if not any(
            str(value).strip()
            for value in row
        ):
            continue

        if len(row) < len(columns):
            row = row + [
                ""
            ] * (
                len(columns) - len(row)
            )

        elif len(row) > len(columns):
            row = row[
                :len(columns)
            ]

        cleaned_row = {
            columns[index]: str(
                row[index]
            ).strip()
            for index in range(
                len(columns)
            )
        }

        cleaned_rows.append(
            cleaned_row
        )

    if not cleaned_rows:
        return None, (
            "The CSV contains column headings but no data rows."
        )

    return {
        "columns": columns,
        "rows": cleaned_rows,
        "row_count": len(cleaned_rows),
        "column_count": len(columns),
        "delimiter": delimiter,
    }, None


def is_numeric_value(
    value: Any,
) -> bool:
    """
    Return True when a value can be converted to a finite float.
    """

    if value is None:
        return False

    text = str(value).strip()

    if not text:
        return False

    try:
        number = float(text)

        return number == number and number not in {
            float("inf"),
            float("-inf"),
        }

    except (TypeError, ValueError):
        return False


def find_numeric_columns(
    dataset: dict[str, Any],
    minimum_numeric_ratio: float = 0.80,
) -> list[str]:
    """
    Find columns where at least 80% of non-empty values are numeric.
    """

    numeric_columns: list[str] = []

    columns = dataset.get(
        "columns",
        [],
    )

    rows = dataset.get(
        "rows",
        [],
    )

    for column in columns:
        non_empty_count = 0
        numeric_count = 0

        for row in rows:
            value = row.get(
                column,
                "",
            )

            if str(value).strip() == "":
                continue

            non_empty_count += 1

            if is_numeric_value(value):
                numeric_count += 1

        if (
            non_empty_count > 0
            and numeric_count / non_empty_count
            >= minimum_numeric_ratio
        ):
            numeric_columns.append(
                column
            )

    return numeric_columns


def create_preview_text(
    dataset: dict[str, Any],
    maximum_rows: int = 10,
) -> str:
    """
    Create a readable fixed-width preview without pandas or Arrow.
    """

    columns = dataset.get(
        "columns",
        [],
    )

    rows = dataset.get(
        "rows",
        [],
    )[:maximum_rows]

    if not columns:
        return "No columns available."

    widths: dict[str, int] = {}

    for column in columns:
        longest_value = max(
            [
                len(str(column)),
                *[
                    len(
                        str(
                            row.get(
                                column,
                                "",
                            )
                        )
                    )
                    for row in rows
                ],
            ]
        )

        widths[column] = min(
            longest_value,
            24,
        )

    header = " | ".join(
        str(column)[
            :widths[column]
        ].ljust(
            widths[column]
        )
        for column in columns
    )

    separator = "-+-".join(
        "-" * widths[column]
        for column in columns
    )

    body_lines: list[str] = []

    for row in rows:
        body_lines.append(
            " | ".join(
                str(
                    row.get(
                        column,
                        "",
                    )
                )[
                    :widths[column]
                ].ljust(
                    widths[column]
                )
                for column in columns
            )
        )

    return "\n".join(
        [
            header,
            separator,
            *body_lines,
        ]
    )