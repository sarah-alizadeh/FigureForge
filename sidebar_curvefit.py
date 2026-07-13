from __future__ import annotations

from typing import Any

import streamlit as st


FIT_MODELS = [
    "Linear",
    "Polynomial",
    "Exponential",
    "Logarithmic",
    "Power Law",
    "Moving Average",
]

FIT_LINE_STYLES = [
    "Solid",
    "Dashed",
    "Dotted",
    "Dash-Dot",
]


def render_curve_fit_controls(
    y_columns: list[str],
) -> dict[str, Any]:
    """
    Render curve-fitting controls.

    This module contains no pandas, NumPy, SciPy, or Matplotlib.
    """

    with st.expander(
        "Curve Fitting",
        expanded=False,
    ):
        fit_enabled = st.toggle(
            "Add fitted curve",
            value=False,
            key="curvefit_enabled",
        )

        if not fit_enabled:
            return {
                "fit_enabled": False,
                "fit_columns": [],
                "fit_model": "Linear",
                "polynomial_degree": 2,
                "moving_average_window": 3,
                "fit_points": 300,
                "fit_line_style": "Dashed",
                "fit_line_width": 3,
                "fit_opacity": 0.95,
                "show_fit_equation": True,
                "show_fit_statistics": True,
            }

        if not y_columns:
            st.warning(
                "Select at least one Y-axis series before enabling fitting."
            )

            return {
                "fit_enabled": False,
                "fit_columns": [],
                "fit_model": "Linear",
                "polynomial_degree": 2,
                "moving_average_window": 3,
                "fit_points": 300,
                "fit_line_style": "Dashed",
                "fit_line_width": 3,
                "fit_opacity": 0.95,
                "show_fit_equation": True,
                "show_fit_statistics": True,
            }

        fit_columns = st.multiselect(
            "Fit these Y-series",
            options=y_columns,
            default=y_columns[:1],
        )

        fit_model = st.selectbox(
            "Fit model",
            options=FIT_MODELS,
        )

        polynomial_degree = 2

        if fit_model == "Polynomial":
            polynomial_degree = st.slider(
                "Polynomial degree",
                min_value=2,
                max_value=5,
                value=2,
            )

        moving_average_window = 3

        if fit_model == "Moving Average":
            moving_average_window = st.slider(
                "Moving-average window",
                min_value=2,
                max_value=25,
                value=3,
            )

        fit_points = st.slider(
            "Fit smoothness",
            min_value=50,
            max_value=1000,
            value=300,
            step=50,
            disabled=(
                fit_model == "Moving Average"
            ),
        )

        fit_line_style = st.selectbox(
            "Fit line style",
            options=FIT_LINE_STYLES,
            index=1,
        )

        fit_line_width = st.slider(
            "Fit line width",
            min_value=1,
            max_value=8,
            value=3,
        )

        fit_opacity = st.slider(
            "Fit opacity",
            min_value=0.20,
            max_value=1.00,
            value=0.95,
            step=0.05,
        )

        show_fit_equation = st.toggle(
            "Show fitted equation",
            value=True,
            key="curvefit_show_equation",
        )

        show_fit_statistics = st.toggle(
            "Show fit statistics",
            value=True,
            key="curvefit_show_statistics",
        )

    return {
        "fit_enabled": fit_enabled,
        "fit_columns": fit_columns,
        "fit_model": fit_model,
        "polynomial_degree": int(
            polynomial_degree
        ),
        "moving_average_window": int(
            moving_average_window
        ),
        "fit_points": int(
            fit_points
        ),
        "fit_line_style": fit_line_style,
        "fit_line_width": int(
            fit_line_width
        ),
        "fit_opacity": float(
            fit_opacity
        ),
        "show_fit_equation": show_fit_equation,
        "show_fit_statistics": show_fit_statistics,
    }