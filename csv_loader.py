from __future__ import annotations

import math
from io import StringIO
from pathlib import Path
from typing import Any, BinaryIO, Optional

import pandas as pd


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_FILE_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
}


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _reset_file_pointer(
    uploaded_file: BinaryIO,
) -> None:
    """
    Safely move an uploaded file back to its beginning.
    """

    try:
        uploaded_file.seek(0)
    except Exception:
        pass


def _clean_column_name(
    column_name: Any,
    column_number: int,
) -> str:
    """
    Convert a column heading into a clean, non-empty string.
    """

    cleaned_name = str(column_name).strip()

    if not cleaned_name or cleaned_name.lower().startswith(
        "unnamed:"
    ):
        return f"Column_{column_number}"

    return cleaned_name


def _make_column_names_unique(
    column_names: list[str],
) -> list[str]:
    """
    Ensure duplicate column headings receive unique names.

    Example:
        Temperature
        Temperature_2
        Temperature_3
    """

    counts: dict[str, int] = {}
    unique_names: list[str] = []

    for column_name in column_names:
        if column_name not in counts:
            counts[column_name] = 1
            unique_names.append(column_name)
            continue

        counts[column_name] += 1

        unique_names.append(
            f"{column_name}_{counts[column_name]}"
        )

    return unique_names


def _clean_cell_value(
    value: Any,
) -> Any:
    """
    Convert Pandas and NumPy values into plain Python values.

    Missing values become empty strings so downstream code can
    safely call str(), float(), and dictionary methods.
    """

    if value is None:
        return ""

    try:
        missing = pd.isna(value)

        if isinstance(missing, bool) and missing:
            return ""

    except Exception:
        pass

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""

    return value


def _dataframe_to_dataset(
    dataframe: pd.DataFrame,
    source_filename: str,
) -> dict[str, Any]:
    """
    Convert a Pandas DataFrame into the dictionary format used by
    FigureForge.
    """

    dataframe = dataframe.copy()

    cleaned_columns = [
        _clean_column_name(
            column_name=column_name,
            column_number=index + 1,
        )
        for index, column_name in enumerate(
            dataframe.columns
        )
    ]

    dataframe.columns = _make_column_names_unique(
        cleaned_columns
    )

    dataframe = dataframe.dropna(
        axis=0,
        how="all",
    )

    dataframe = dataframe.dropna(
        axis=1,
        how="all",
    )

    columns = [
        str(column)
        for column in dataframe.columns
    ]

    rows: list[dict[str, Any]] = []

    for record in dataframe.to_dict(
        orient="records"
    ):
        cleaned_record = {
            str(column): _clean_cell_value(
                record.get(
                    column,
                    "",
                )
            )
            for column in columns
        }

        rows.append(cleaned_record)

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "column_count": len(columns),
        "source_filename": source_filename,
    }


def _read_csv_file(
    uploaded_file: BinaryIO,
) -> pd.DataFrame:
    """
    Read a CSV file with several safe encoding and delimiter fallbacks.
    """

    attempts = [
        {
            "encoding": "utf-8-sig",
            "sep": None,
            "engine": "python",
        },
        {
            "encoding": "utf-8",
            "sep": None,
            "engine": "python",
        },
        {
            "encoding": "latin-1",
            "sep": None,
            "engine": "python",
        },
    ]

    last_error: Optional[Exception] = None

    for options in attempts:
        try:
            _reset_file_pointer(
                uploaded_file
            )

            return pd.read_csv(
                uploaded_file,
                **options,
            )

        except Exception as error:
            last_error = error

    if last_error is not None:
        raise last_error

    raise ValueError(
        "The CSV file could not be read."
    )


def _read_excel_file(
    uploaded_file: BinaryIO,
    extension: str,
) -> pd.DataFrame:
    """
    Read the first worksheet from an Excel workbook.
    """

    _reset_file_pointer(
        uploaded_file
    )

    engine = (
        "openpyxl"
        if extension == ".xlsx"
        else "xlrd"
    )

    return pd.read_excel(
        uploaded_file,
        sheet_name=0,
        engine=engine,
    )


# ============================================================
# PUBLIC FILE-LOADING FUNCTION
# ============================================================

def load_csv(
    uploaded_file: BinaryIO,
) -> tuple[
    Optional[dict[str, Any]],
    Optional[str],
]:
    """
    Load a CSV or Excel file into FigureForge's dataset format.

    The function name remains `load_csv` for compatibility with
    the existing app.

    Supported types:
        .csv
        .xlsx
        .xls

    Returns:
        dataset_dictionary, error_message
    """

    if uploaded_file is None:
        return (
            None,
            "No file was provided.",
        )

    filename = str(
        getattr(
            uploaded_file,
            "name",
            "",
        )
    ).strip()

    if not filename:
        return (
            None,
            "The uploaded file does not have a filename.",
        )

    extension = Path(
        filename
    ).suffix.lower()

    if extension not in SUPPORTED_FILE_EXTENSIONS:
        return (
            None,
            (
                "Unsupported file type. Please upload a CSV "
                "(.csv) or Excel file (.xlsx or .xls)."
            ),
        )

    try:
        if extension == ".csv":
            dataframe = _read_csv_file(
                uploaded_file
            )

        else:
            dataframe = _read_excel_file(
                uploaded_file=uploaded_file,
                extension=extension,
            )

    except ImportError as error:
        if extension == ".xlsx":
            return (
                None,
                (
                    "Excel .xlsx support requires openpyxl. "
                    "Install it with: "
                    "`python -m pip install openpyxl`"
                ),
            )

        if extension == ".xls":
            return (
                None,
                (
                    "Excel .xls support requires xlrd. "
                    "Install it with: "
                    "`python -m pip install xlrd`"
                ),
            )

        return (
            None,
            f"Required file-reading package is missing: {error}",
        )

    except pd.errors.EmptyDataError:
        return (
            None,
            "The uploaded file is empty.",
        )

    except pd.errors.ParserError as error:
        return (
            None,
            (
                "The CSV file could not be parsed. "
                f"Details: {error}"
            ),
        )

    except ValueError as error:
        return (
            None,
            (
                "The file could not be read. "
                f"Details: {error}"
            ),
        )

    except Exception as error:
        return (
            None,
            (
                "An unexpected file-loading error occurred. "
                f"Details: {type(error).__name__}: {error}"
            ),
        )

    if dataframe is None:
        return (
            None,
            "The file reader returned no data.",
        )

    if dataframe.empty:
        return (
            None,
            "The uploaded file does not contain any data rows.",
        )

    if len(dataframe.columns) < 2:
        return (
            None,
            "The uploaded file must contain at least two columns.",
        )

    try:
        dataset = _dataframe_to_dataset(
            dataframe=dataframe,
            source_filename=filename,
        )

    except Exception as error:
        return (
            None,
            (
                "The uploaded data could not be converted into "
                "FigureForge format. "
                f"Details: {type(error).__name__}: {error}"
            ),
        )

    if not dataset["rows"]:
        return (
            None,
            "The uploaded file does not contain any usable rows.",
        )

    if len(dataset["columns"]) < 2:
        return (
            None,
            "The uploaded file must contain at least two usable columns.",
        )

    return dataset, None


# ============================================================
# NUMERIC COLUMN DETECTION
# ============================================================

def find_numeric_columns(
    dataset: dict[str, Any],
) -> list[str]:
    """
    Identify columns that contain usable numeric data.

    A column is considered numeric when at least one non-empty value
    exists and at least 80 percent of its non-empty values can be
    converted to numbers.
    """

    if not isinstance(
        dataset,
        dict,
    ):
        return []

    columns = dataset.get(
        "columns",
        [],
    )

    rows = dataset.get(
        "rows",
        [],
    )

    numeric_columns: list[str] = []

    for column in columns:
        non_empty_count = 0
        numeric_count = 0

        for row in rows:
            raw_value = row.get(
                column,
                "",
            )

            if raw_value is None:
                continue

            value_text = str(
                raw_value
            ).strip()

            if not value_text:
                continue

            non_empty_count += 1

            try:
                numeric_value = float(
                    value_text.replace(
                        ",",
                        "",
                    )
                )

                if math.isfinite(
                    numeric_value
                ):
                    numeric_count += 1

            except (
                TypeError,
                ValueError,
            ):
                continue

        if non_empty_count == 0:
            continue

        numeric_fraction = (
            numeric_count
            / non_empty_count
        )

        if numeric_fraction >= 0.80:
            numeric_columns.append(
                column
            )

    return numeric_columns


# ============================================================
# PREVIEW CREATION
# ============================================================

def create_preview_text(
    dataset: dict[str, Any],
    maximum_rows: int = 10,
) -> str:
    """
    Create a readable text preview from FigureForge's dataset format.
    """

    if not isinstance(
        dataset,
        dict,
    ):
        return "No dataset is available."

    columns = dataset.get(
        "columns",
        [],
    )

    rows = dataset.get(
        "rows",
        [],
    )

    if not columns:
        return "The dataset does not contain any columns."

    preview_rows = rows[
        :max(
            0,
            int(maximum_rows),
        )
    ]

    preview_dataframe = pd.DataFrame(
        preview_rows,
        columns=columns,
    )

    output_buffer = StringIO()

    preview_dataframe.to_string(
        buf=output_buffer,
        index=False,
        na_rep="",
    )

    return output_buffer.getvalue()


# ============================================================
# OPTIONAL COMPATIBILITY ALIAS
# ============================================================

def load_dataset(
    uploaded_file: BinaryIO,
) -> tuple[
    Optional[dict[str, Any]],
    Optional[str],
]:
    """
    Alias for future code that uses the more general name
    `load_dataset`.
    """

    return load_csv(
        uploaded_file
    )