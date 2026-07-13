from __future__ import annotations
from sidebar_axes import render_axis_controls
from export import SUPPORTED_EXPORT_FORMATS
from typing import Any

import streamlit as st

from csv_loader import find_numeric_columns
from sidebar_curvefit import render_curve_fit_controls


GRAPH_TYPES = [
    "Line Plot",
    "Scatter Plot",
    "Bar Chart",
]

LINE_STYLES = [
    "Solid",
    "Dashed",
    "Dotted",
    "Dash-Dot",
]

MARKER_STYLES = [
    "Circle",
    "Square",
    "Diamond",
    "Star",
    "Triangle Up",
    "Triangle Down",
    "X",
    "Cross",
]

DISPLAY_MODES = [
    "Lines and Markers",
    "Lines Only",
    "Markers Only",
]

BACKGROUND_OPTIONS = [
    "White",
    "Black",
]

DEFAULT_COLORS = [
    "#2563EB",
    "#DC2626",
    "#059669",
    "#7C3AED",
    "#EA580C",
    "#0891B2",
    "#DB2777",
    "#65A30D",
]


def make_safe_key(
    index: int,
    column_name: str,
) -> str:
    cleaned_name = "".join(
        character
        if character.isalnum()
        else "_"
        for character in column_name
    )

    return f"{index}_{cleaned_name}"


def render_sidebar(
    dataset: dict[str, Any],
) -> dict[str, Any]:
    """
    Render FigureForge controls without pandas.
    """

    columns = dataset.get(
        "columns",
        [],
    )

    if not columns:
        return {
            "x_column": None,
            "y_columns": [],
            "graph_type": "Line Plot",
            "generate": False,
            "series_styles": {},
            "fit_enabled": False,
            "fit_columns": [],
        }

    numeric_columns = find_numeric_columns(
        dataset
    )

    default_x_column = columns[0]

    default_y_columns = [
        column
        for column in numeric_columns
        if column != default_x_column
    ][:1]

    if not default_y_columns:
        default_y_columns = [
            column
            for column in columns
            if column != default_x_column
        ][:1]

    with st.sidebar:
        st.header(
            "Figure Controls"
        )

        st.subheader(
            "Stage 2: Data Selection"
        )

        x_column = st.selectbox(
            "X-axis column",
            options=columns,
            index=0,
        )

        available_y_columns = [
            column
            for column in columns
            if column != x_column
        ]

        valid_default_y_columns = [
            column
            for column in default_y_columns
            if column in available_y_columns
        ]

        if (
            not valid_default_y_columns
            and available_y_columns
        ):
            numeric_y_options = [
                column
                for column in available_y_columns
                if column in numeric_columns
            ]

            valid_default_y_columns = (
                numeric_y_options[:1]
                if numeric_y_options
                else available_y_columns[:1]
            )

        y_columns = st.multiselect(
            "Y-axis column(s)",
            options=available_y_columns,
            default=valid_default_y_columns,
        )

        graph_type = st.selectbox(
            "Graph type",
            options=GRAPH_TYPES,
        )

        st.divider()

        st.subheader(
            "Stage 3: Figure Customization"
        )

        default_title = (
            f"{', '.join(y_columns)} vs. {x_column}"
            if y_columns
            else "Scientific Figure"
        )

        figure_title = st.text_input(
            "Figure title",
            value=default_title,
        )

        x_axis_title = st.text_input(
            "X-axis title",
            value=x_column,
        )

        y_axis_title = st.text_input(
            "Y-axis title",
            value=(
                ", ".join(y_columns)
                if y_columns
                else "Value"
            ),
        )

        dimension_1, dimension_2 = st.columns(
            2
        )

        with dimension_1:
            figure_width = st.number_input(
                "Width",
                min_value=500,
                max_value=1600,
                value=900,
                step=50,
            )

        with dimension_2:
            figure_height = st.number_input(
                "Height",
                min_value=350,
                max_value=1200,
                value=600,
                step=50,
            )

        background = st.radio(
            "Figure background",
            options=BACKGROUND_OPTIONS,
            horizontal=True,
        )

        scale_1, scale_2 = st.columns(2)

        with scale_1:
            x_scale = st.selectbox(
                "X-axis scale",
                options=[
                    "Linear",
                    "Logarithmic",
                ],
            )

        with scale_2:
            y_scale = st.selectbox(
                "Y-axis scale",
                options=[
                    "Linear",
                    "Logarithmic",
                ],
            )

        show_grid = st.toggle(
            "Show grid",
            value=True,
            key="figure_show_grid",
        )

        show_legend = st.toggle(
            "Show legend",
            value=True,
            key="figure_show_legend",
        )

        title_font_size = st.slider(
            "Title font size",
            12,
            36,
            20,
        )

        axis_font_size = st.slider(
            "Axis-title font size",
            10,
            28,
            14,
        )

        tick_font_size = st.slider(
            "Tick-label font size",
            8,
            22,
            11,
        )

        series_styles: dict[
            str,
            dict[str, Any],
        ] = {}

        with st.expander(
            "Data Presentation",
            expanded=True,
        ):
            for index, y_column in enumerate(
                y_columns
            ):
                safe_key = make_safe_key(
                    index,
                    y_column,
                )

                st.markdown(
                    f"### {y_column}"
                )

                color = st.color_picker(
                    f"Color — {y_column}",
                    DEFAULT_COLORS[
                        index % len(DEFAULT_COLORS)
                    ],
                    key=f"color_{safe_key}",
                )

                display_mode = st.selectbox(
                    f"Display mode — {y_column}",
                    options=DISPLAY_MODES,
                    key=f"display_{safe_key}",
                    disabled=(
                        graph_type != "Line Plot"
                    ),
                )

                line_style = st.selectbox(
                    f"Line style — {y_column}",
                    options=LINE_STYLES,
                    key=f"line_style_{safe_key}",
                    disabled=(
                        graph_type == "Scatter Plot"
                    ),
                )

                marker_style = st.selectbox(
                    f"Marker style — {y_column}",
                    options=MARKER_STYLES,
                    key=f"marker_style_{safe_key}",
                    disabled=(
                        graph_type == "Bar Chart"
                    ),
                )

                line_width = st.slider(
                    f"Line width — {y_column}",
                    1,
                    8,
                    2,
                    key=f"line_width_{safe_key}",
                    disabled=(
                        graph_type == "Scatter Plot"
                    ),
                )

                marker_size = st.slider(
                    f"Marker size — {y_column}",
                    4,
                    24,
                    8,
                    key=f"marker_size_{safe_key}",
                    disabled=(
                        graph_type == "Bar Chart"
                    ),
                )

                opacity = st.slider(
                    f"Opacity — {y_column}",
                    0.10,
                    1.00,
                    0.90,
                    0.05,
                    key=f"opacity_{safe_key}",
                )

                series_styles[y_column] = {
                    "color": color,
                    "display_mode": display_mode,
                    "line_style": line_style,
                    "marker_style": marker_style,
                    "line_width": int(
                        line_width
                    ),
                    "marker_size": int(
                        marker_size
                    ),
                    "opacity": float(
                        opacity
                    ),
                }

                if index < len(y_columns) - 1:
                    st.divider()
        axis_settings = render_axis_controls(
            y_columns
        )

        fit_settings = render_curve_fit_controls(
            y_columns
        )


        st.divider()
        # ====================================================
        # EXPORT SETTINGS
        # ====================================================

        with st.expander(
            "Export Settings",
            expanded=False,
        ):
            export_format = st.selectbox(
                "File type",
                options=list(
                    SUPPORTED_EXPORT_FORMATS.keys()
                ),
                index=0,
                key="export_file_type",
            )

            export_filename = st.text_input(
                "File name",
                value="figureforge_figure",
                key="export_filename",
            )

            export_scale = st.select_slider(
                "Export quality",
                options=[
                    1.0,
                    2.0,
                    3.0,
                    4.0,
                ],
                value=2.0,
                format_func=lambda value: {
                    1.0: "Standard",
                    2.0: "High",
                    3.0: "Very High",
                    4.0: "Maximum",
                }[value],
                key="export_scale",
                disabled=(
                    export_format
                    in {
                        "SVG",
                        "PDF",
                        "Interactive HTML",
                    }
                ),
            )

            if export_format in {
                "SVG",
                "PDF",
            }:
                st.caption(
                    "SVG and PDF are vector formats and remain sharp "
                    "when enlarged."
                )

            elif export_format == "Interactive HTML":
                st.caption(
                    "HTML keeps zooming, hovering, legends, and other "
                    "Plotly interactions."
                )

            else:
                st.caption(
                    "Higher quality creates a larger raster image."
                )

        generate_button = st.button(
            "Generate Figure",
            type="primary",
            use_container_width=True,
    )

    settings = {
        "x_column": x_column,
        "y_columns": y_columns,
        "graph_type": graph_type,
        "numeric_columns": numeric_columns,
        "figure_title": figure_title,
        "x_axis_title": x_axis_title,
        "y_axis_title": y_axis_title,
        "figure_width": int(figure_width),
        "figure_height": int(figure_height),
        "background": background,
        "x_scale": x_scale,
        "y_scale": y_scale,
        "show_grid": show_grid,
        "show_legend": show_legend,
        "title_font_size": int(title_font_size),
        "axis_font_size": int(axis_font_size),
        "tick_font_size": int(tick_font_size),
        "series_styles": series_styles,
        "generate": generate_button,
                "export_format": export_format,
        "export_filename": export_filename,
        "export_scale": float(export_scale),
    }

    settings.update(
        axis_settings
    )

    settings.update(
        fit_settings
    )
    return settings
