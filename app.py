from __future__ import annotations

import gc
from io import BytesIO
from pathlib import Path
from typing import Any

import streamlit as st

from csv_loader import (
    create_preview_text,
    find_numeric_columns,
    load_csv,
)
from export import export_figure
from plotting import create_basic_figure
from sidebar import render_sidebar

try:
    from styles import apply_app_styles
except Exception:
    apply_app_styles = None


# ============================================================
# PATHS
# ============================================================

PROJECT_DIRECTORY = Path(__file__).resolve().parent

LOGO_PATH = (
    PROJECT_DIRECTORY
    / "assets"
    / "figureforge_logo.png"
)

EXAMPLE_FIGURE_PATH = (
    PROJECT_DIRECTORY
    / "assets"
    / "example_figure.png"
)

SAMPLE_DATA_PATH = (
    PROJECT_DIRECTORY
    / "sample_test.csv"
)


# ============================================================
# PAGE CONFIGURATION
# Must be the first Streamlit command.
# ============================================================

st.set_page_config(
    page_title="FigureForge",
    page_icon=(
        str(LOGO_PATH)
        if LOGO_PATH.exists()
        else "📈"
    ),
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLING
# ============================================================

if apply_app_styles is not None:
    try:
        apply_app_styles()

    except Exception as error:
        st.warning(
            "FigureForge loaded without custom styling. "
            f"{type(error).__name__}: {error}"
        )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def render_header() -> None:
    """
    Render the FigureForge production header.
    """

    logo_column, text_column = st.columns(
        [1, 7],
        vertical_alignment="center",
    )

    with logo_column:
        if LOGO_PATH.exists():
            st.image(
                str(LOGO_PATH),
                width=100,
            )

    with text_column:
        st.title("FigureForge")

        st.markdown(
            "### Turn raw scientific data into professional figures in under a minute."
        )

        st.write(
            "Upload CSV data, select columns, customize professional "
            "figures, and download results."
        )


def render_workflow() -> None:
    """
    Render the four-step FigureForge workflow.
    """

    st.markdown("## Main Workflow")

    step_1, step_2, step_3, step_4 = st.columns(4)

    with step_1:
        st.info(
            "**1. Upload Data**\n\n"
            "Import and inspect your CSV file."
        )

    with step_2:
        st.info(
            "**2. Select Columns**\n\n"
            "Choose X and Y data series."
        )

    with step_3:
        st.info(
            "**3. Customize Figure**\n\n"
            "Set axes, colors, styles, and fits."
        )

    with step_4:
        st.info(
            "**4. Download Results**\n\n"
            "Export your completed figure."
        )


def render_bottom_section() -> None:
    """
    Render the example, feedback, privacy statement, and creator credit.
    """

    st.divider()

    st.markdown("## Learn More")

    example_column, information_column = st.columns(
        [1.4, 1]
    )

    with example_column:
        st.subheader("Example Figure")

        st.write(
            "FigureForge can create figures with custom "
            "colors, dual Y-axes, curve fitting, logarithmic scaling, "
            "and custom formatting."
        )

        if EXAMPLE_FIGURE_PATH.exists():
            left_space, image_column, right_space = st.columns(
                [.1, 3, .1]
            )

            with image_column:
                st.image(
                    str(EXAMPLE_FIGURE_PATH),
                    caption=(
                        "Example of a figure "
                        "created with FigureForge"
                    ),
                    use_container_width=True,
                )

        else:
            st.info(
                "Add an example image at "
                "`assets/example_figure.png` to display it here."
            )

    with information_column:
        st.subheader("Feedback")

        st.write(
            "Found an issue or have a feature suggestion?"
        )

        st.link_button(
            "Send Feedback",
            (
                "mailto:sarah.alizadeh100@gmail.com"
                "?subject=FigureForge%20Feedback"
            ),
            use_container_width=True,
        )

        st.subheader("Privacy")

        st.write(
            "Uploaded CSV files are processed only for the current "
            "FigureForge session. Do not upload confidential, restricted, "
            "or personally identifiable data unless you are authorized "
            "to process it."
        )

    st.divider()

    st.markdown(
        """
        <div class="figureforge-footer">
            <strong>Built by Sarah Alizadeh</strong><br>
            M.S. Mechanical Engineering student at Boston University
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_metric(
    value: Any,
    decimal_places: int = 6,
) -> str:
    """
    Safely format a numeric metric.
    """

    try:
        numeric_value = float(value)

        if numeric_value != numeric_value:
            return "N/A"

        return f"{numeric_value:.{decimal_places}g}"

    except (TypeError, ValueError):
        return "N/A"


def render_fit_results(
    fit_results: list[dict[str, Any]],
    settings: dict[str, Any],
) -> None:
    """
    Render curve-fit equations, statistics, and parameters.
    """

    if not fit_results:
        return

    st.subheader("Curve-Fit Results")

    for result in fit_results:
        if not isinstance(result, dict):
            st.warning(
                "One curve-fit result had an invalid format."
            )
            continue

        series_name = result.get(
            "series",
            "Unknown Series",
        )

        model_name = result.get(
            "model",
            "Unknown Model",
        )

        result_error = result.get("error")

        if result_error:
            st.warning(
                f"{series_name} — {model_name}: "
                f"{result_error}"
            )
            continue

        with st.expander(
            f"{series_name} — {model_name}",
            expanded=True,
        ):
            if settings.get(
                "show_fit_equation",
                True,
            ):
                st.markdown("**Fitted Equation**")

                st.code(
                    str(
                        result.get(
                            "equation",
                            "Equation unavailable",
                        )
                    ),
                    language=None,
                )

            if settings.get(
                "show_fit_statistics",
                True,
            ):
                metric_1, metric_2, metric_3, metric_4 = (
                    st.columns(4)
                )

                with metric_1:
                    st.metric(
                        "R²",
                        format_metric(
                            result.get(
                                "r_squared"
                            )
                        ),
                    )

                with metric_2:
                    st.metric(
                        "RMSE",
                        format_metric(
                            result.get(
                                "rmse"
                            )
                        ),
                    )

                with metric_3:
                    st.metric(
                        "MAE",
                        format_metric(
                            result.get(
                                "mae"
                            )
                        ),
                    )

                with metric_4:
                    st.metric(
                        "Points",
                        result.get(
                            "point_count",
                            0,
                        ),
                    )

            parameters = result.get(
                "parameters",
                {},
            )

            if parameters:
                st.markdown("**Fit Parameters**")

                parameter_lines: list[str] = []

                for parameter_name, parameter_value in (
                    parameters.items()
                ):
                    parameter_lines.append(
                        f"{parameter_name}: "
                        f"{format_metric(parameter_value, 8)}"
                    )

                st.code(
                    "\n".join(
                        parameter_lines
                    ),
                    language=None,
                )

class NamedBytesIO(BytesIO):
    """
    In-memory file object with a filename.

    This lets the built-in sample CSV behave like a file uploaded
    through Streamlit.
    """

    def __init__(
        self,
        data: bytes,
        filename: str,
    ) -> None:
        super().__init__(data)
        self.name = filename

# ============================================================
# STARTUP CLEANUP
# ============================================================

try:
    gc.collect()
except Exception:
    pass


# ============================================================
# HEADER AND WORKFLOW
# ============================================================

render_header()
render_workflow()


# ============================================================
# 1. UPLOAD DATA
# ============================================================

st.header("1. Upload Data")

data_source = st.radio(
    "Choose a data source",
    options=[
        "Use Sample Dataset",
        "Upload My Own CSV",
    ],
    horizontal=True,
    key="figureforge_data_source",
)


uploaded_file = None


if data_source == "Use Sample Dataset":
    st.info(
        "The sample dataset contains elapsed time, temperature, "
        "and pressure data so you can test multiple Y-values."
    )

    if not SAMPLE_DATA_PATH.exists():
        st.error(
            "The sample dataset could not be found. Make sure "
            "`sample_test.csv` is in the main FigureForge folder."
        )

        render_bottom_section()
        st.stop()

    sample_bytes = SAMPLE_DATA_PATH.read_bytes()

    uploaded_file = NamedBytesIO(
        sample_bytes,
        SAMPLE_DATA_PATH.name,
    )

    st.success(
        "Sample dataset selected: `sample_test.csv`"
    )

    st.download_button(
        label="Download Sample CSV",
        data=sample_bytes,
        file_name="figureforge_sample_data.csv",
        mime="text/csv",
        use_container_width=False,
        key="download_sample_dataset",
    )


else:
    uploaded_file = st.file_uploader(
        "Upload your CSV file",
        type=["csv"],
        help=(
            "Upload a CSV file containing column headers "
            "and at least one data row."
        ),
        key="production_csv_uploader",
    )

    if uploaded_file is None:
        st.info(
            "Upload a CSV file to begin creating your figure."
        )

        render_bottom_section()
        st.stop()


try:
    dataset, load_error = load_csv(
        uploaded_file
    )

except MemoryError:
    st.error(
        "The uploaded CSV is too large to load into memory."
    )

    render_bottom_section()
    st.stop()

except Exception as error:
    st.error(
        "FigureForge encountered an unexpected file-loading error. "
        f"{type(error).__name__}: {error}"
    )

    render_bottom_section()
    st.stop()


if load_error:
    st.error(load_error)

    render_bottom_section()
    st.stop()


if dataset is None:
    st.error(
        "The CSV loader did not return a dataset."
    )

    render_bottom_section()
    st.stop()


required_dataset_keys = {
    "columns",
    "rows",
    "row_count",
    "column_count",
}

missing_dataset_keys = [
    key
    for key in required_dataset_keys
    if key not in dataset
]

if missing_dataset_keys:
    st.error(
        "The CSV dataset is missing required information: "
        + ", ".join(
            sorted(missing_dataset_keys)
        )
    )

    render_bottom_section()
    st.stop()


columns = dataset.get(
    "columns",
    [],
)

rows = dataset.get(
    "rows",
    [],
)


if len(columns) < 2:
    st.error(
        "The CSV must contain at least two columns."
    )

    render_bottom_section()
    st.stop()


if not rows:
    st.error(
        "The CSV does not contain any usable data rows."
    )

    render_bottom_section()
    st.stop()


try:
    numeric_columns = find_numeric_columns(
        dataset
    )

except Exception:
    numeric_columns = []


st.success("CSV loaded successfully.")

metric_1, metric_2, metric_3 = st.columns(3)

with metric_1:
    st.metric(
        "Rows",
        f"{dataset['row_count']:,}",
    )

with metric_2:
    st.metric(
        "Columns",
        dataset["column_count"],
    )

with metric_3:
    st.metric(
        "Numeric Columns",
        len(numeric_columns),
    )


with st.expander(
    "CSV Preview — First 10 Rows",
    expanded=True,
):
    try:
        st.code(
            create_preview_text(
                dataset=dataset,
                maximum_rows=10,
            ),
            language=None,
        )

    except Exception as error:
        st.warning(
            "The CSV loaded, but the preview could not be created. "
            f"{type(error).__name__}: {error}"
        )


with st.expander(
    "Column Information",
    expanded=False,
):
    numeric_column_set = set(
        numeric_columns
    )

    for column in columns:
        non_empty_count = 0
        missing_count = 0
        unique_values: set[str] = set()

        for row in rows:
            value = str(
                row.get(
                    column,
                    "",
                )
            ).strip()

            if value:
                non_empty_count += 1
                unique_values.add(value)

            else:
                missing_count += 1

        detected_type = (
            "Numeric"
            if column in numeric_column_set
            else "Text / Categorical"
        )

        st.markdown(
            f"**{column}**  \n"
            f"Detected type: `{detected_type}`  \n"
            f"Non-empty values: `{non_empty_count}`  \n"
            f"Missing values: `{missing_count}`  \n"
            f"Unique values: `{len(unique_values)}`"
        )

        st.divider()


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

try:
    settings = render_sidebar(
        dataset
    )

except MemoryError:
    st.error(
        "The figure controls used too much memory."
    )

    render_bottom_section()
    st.stop()

except Exception as error:
    st.error(
        "FigureForge could not create the figure controls. "
        f"{type(error).__name__}: {error}"
    )

    render_bottom_section()
    st.stop()


if not isinstance(settings, dict):
    st.error(
        "The sidebar did not return valid figure settings."
    )

    render_bottom_section()
    st.stop()


# ============================================================
# 2. SELECT COLUMNS
# ============================================================

st.header("2. Select Columns")

selection_1, selection_2, selection_3 = st.columns(3)

with selection_1:
    st.markdown("**X-axis**")

    st.code(
        str(
            settings.get(
                "x_column",
                "Not selected",
            )
        ),
        language=None,
    )

with selection_2:
    st.markdown("**Y-axis series**")

    selected_y_columns = settings.get(
        "y_columns",
        [],
    )

    if selected_y_columns:
        st.code(
            "\n".join(
                str(column)
                for column in selected_y_columns
            ),
            language=None,
        )

    else:
        st.warning(
            "No Y-axis columns selected."
        )

with selection_3:
    st.markdown("**Graph type**")

    st.code(
        str(
            settings.get(
                "graph_type",
                "Not selected",
            )
        ),
        language=None,
    )


axis_assignments = settings.get(
    "axis_assignments",
    {},
)

if axis_assignments:
    with st.expander(
        "Axis Assignments",
        expanded=False,
    ):
        st.code(
            "\n".join(
                f"{series}: {axis_name}"
                for series, axis_name
                in axis_assignments.items()
            ),
            language=None,
        )


# ============================================================
# WAIT FOR GENERATION
# ============================================================

if not settings.get(
    "generate",
    False,
):
    st.info(
        "Choose your data, figure style, axis assignments, "
        "curve-fit options, and export settings in the sidebar. "
        "Then click **Generate Figure**."
    )

    render_bottom_section()
    st.stop()


# ============================================================
# VALIDATE SELECTIONS
# ============================================================

x_column = settings.get("x_column")
y_columns = settings.get(
    "y_columns",
    [],
)


if not x_column:
    st.error(
        "Select an X-axis column."
    )

    render_bottom_section()
    st.stop()


if x_column not in columns:
    st.error(
        f'The selected X-axis column "{x_column}" '
        "does not exist in the uploaded CSV."
    )

    render_bottom_section()
    st.stop()


if not y_columns:
    st.error(
        "Select at least one Y-axis column."
    )

    render_bottom_section()
    st.stop()


missing_y_columns = [
    column
    for column in y_columns
    if column not in columns
]

if missing_y_columns:
    st.error(
        "These selected Y-axis columns do not exist: "
        + ", ".join(
            missing_y_columns
        )
    )

    render_bottom_section()
    st.stop()


if settings.get(
    "fit_enabled",
    False,
) and not settings.get(
    "fit_columns",
    [],
):
    st.error(
        "Curve fitting is enabled, but no Y-series was selected."
    )

    render_bottom_section()
    st.stop()


# ============================================================
# 3. CUSTOMIZE FIGURE
# ============================================================

st.header("3. Customize Figure")

st.write(
    "The figure below uses the axis, style, fitting, and layout "
    "settings selected in the sidebar."
)


with st.spinner(
    "Building your publication-ready figure..."
):
    try:
        (
            figure,
            fit_results,
            figure_error,
        ) = create_basic_figure(
            dataset=dataset,
            settings=settings,
        )

    except MemoryError:
        st.error(
            "The figure used too much memory. "
            "Try fewer series or a smaller CSV."
        )

        render_bottom_section()
        st.stop()

    except Exception as error:
        st.error(
            "FigureForge encountered an unexpected plotting error. "
            f"{type(error).__name__}: {error}"
        )

        render_bottom_section()
        st.stop()


if figure_error:
    st.error(figure_error)

    render_bottom_section()
    st.stop()


if figure is None:
    st.error(
        "The plotting function did not return a figure."
    )

    render_bottom_section()
    st.stop()


st.success(
    "Figure generated successfully."
)


try:
    st.plotly_chart(
        figure,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "figureforge_figure",
                "height": int(
                    settings.get(
                        "figure_height",
                        600,
                    )
                ),
                "width": int(
                    settings.get(
                        "figure_width",
                        900,
                    )
                ),
                "scale": 2,
            },
        },
    )

except Exception as error:
    st.error(
        "The figure was created but could not be displayed. "
        f"{type(error).__name__}: {error}"
    )

    render_bottom_section()
    st.stop()


render_fit_results(
    fit_results,
    settings,
)

# ============================================================
# 4. DOWNLOAD RESULTS
# ============================================================

st.header("4. Download Results")

st.write(
    "Choose the file type and export settings in the sidebar, "
    "then download your completed figure."
)

export_format = settings.get(
    "export_format",
    "PNG",
)

with st.spinner(
    f"Preparing {export_format} export..."
):
    try:
        (
            export_data,
            completed_filename,
            export_mime,
            export_error,
        ) = export_figure(
            figure=figure,
            export_format=export_format,
            filename=settings.get(
                "export_filename",
                "figureforge_figure",
            ),
            width=int(
                settings.get(
                    "figure_width",
                    900,
                )
            ),
            height=int(
                settings.get(
                    "figure_height",
                    600,
                )
            ),
            scale=float(
                settings.get(
                    "export_scale",
                    2.0,
                )
            ),
        )

    except Exception as error:
        export_data = None
        completed_filename = None
        export_mime = None
        export_error = (
            "Unexpected export error: "
            f"{type(error).__name__}: {error}"
        )


if export_error:
    st.error(export_error)

    if export_format != "Interactive HTML":
        st.info(
            "Static export requires Kaleido. Run:\n\n"
            "`python -m pip install --upgrade kaleido`\n\n"
            "Then restart FigureForge."
        )

elif (
    export_data is not None
    and completed_filename is not None
    and export_mime is not None
):
    st.download_button(
        label=f"Download {export_format}",
        data=export_data,
        file_name=completed_filename,
        mime=export_mime,
        type="primary",
        use_container_width=True,
        key="download_generated_figure",
    )


# ============================================================
# BOTTOM SECTION
# ============================================================

render_bottom_section()


# ============================================================
# FINAL CLEANUP
# ============================================================

try:
    gc.collect()
except Exception:
    pass