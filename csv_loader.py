from io import StringIO

import pandas as pd
import streamlit as st


def load_dataset(uploaded_file):
    """
    Load a CSV or Excel file into a pandas DataFrame.
    """

    if uploaded_file is None:
        return None, "No file uploaded."

    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".csv"):
            dataframe = pd.read_csv(uploaded_file)

        elif filename.endswith((".xlsx", ".xls")):
            dataframe = pd.read_excel(uploaded_file)

        else:
            return None, (
                "Unsupported file type. "
                "Please upload a CSV (.csv) or Excel (.xlsx/.xls) file."
            )

    except Exception as error:
        return None, f"Could not read file.\n\n{error}"

    if dataframe.empty:
        return None, "The uploaded file contains no data."

    dataframe.columns = dataframe.columns.astype(str)

    return dataframe, None


def find_numeric_columns(dataframe):
    """
    Return a list of numeric columns.
    """

    if dataframe is None:
        return []

    return (
        dataframe.select_dtypes(include="number")
        .columns.tolist()
    )


def create_preview_text(
    dataframe,
    rows=10,
):
    """
    Create a text preview of the dataset.
    """

    if dataframe is None:
        return ""

    buffer = StringIO()

    dataframe.head(rows).to_string(
        buffer,
        index=False,
    )

    return buffer.getvalue()


def show_upload_summary(dataframe):
    """
    Display a short upload summary.
    """

    if dataframe is None:
        return

    st.success(
        f"Loaded **{len(dataframe)} rows** and "
        f"**{len(dataframe.columns)} columns**."
    )


def show_csv_preview(dataframe):
    """
    Display a preview of the uploaded dataset.
    """

    if dataframe is None:
        return

    with st.expander("Dataset Preview", expanded=False):
        st.dataframe(
            dataframe.head(10),
            use_container_width=True,
            hide_index=True,
        )