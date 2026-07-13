from __future__ import annotations

from typing import Any, Optional

import plotly.graph_objects as go

from curve_fitting import fit_curve, to_float


# ============================================================
# PLOTLY STYLE MAPS
# ============================================================

LINE_DASH_MAP = {
    "Solid": "solid",
    "Dashed": "dash",
    "Dotted": "dot",
    "Dash-Dot": "dashdot",
}


MARKER_SYMBOL_MAP = {
    "Circle": "circle",
    "Square": "square",
    "Diamond": "diamond",
    "Star": "star",
    "Triangle Up": "triangle-up",
    "Triangle Down": "triangle-down",
    "X": "x",
    "Cross": "cross",
}


DISPLAY_MODE_MAP = {
    "Lines and Markers": "lines+markers",
    "Lines Only": "lines",
    "Markers Only": "markers",
}


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_log_values(
    values: list[float],
    axis_name: str,
) -> Optional[str]:
    """
    Validate numeric values before logarithmic scaling.
    """

    if not values:
        return (
            f"{axis_name} requires numeric values "
            "for logarithmic scaling."
        )

    if any(
        value <= 0
        for value in values
    ):
        return (
            f"{axis_name} contains zero or negative values. "
            "Logarithmic axes require values greater than zero."
        )

    return None


def get_series_axis_name(
    settings: dict[str, Any],
    series_name: str,
) -> str:
    """
    Return the Plotly axis name for a data series.

    Left Axis  -> y
    Right Axis -> y2
    """

    assignment = settings.get(
        "axis_assignments",
        {},
    ).get(
        series_name,
        "Left Axis",
    )

    if assignment == "Right Axis":
        return "y2"

    return "y"


def get_axis_series(
    settings: dict[str, Any],
    y_columns: list[str],
    assignment_name: str,
) -> list[str]:
    """
    Return the series assigned to one requested axis.
    """

    assignments = settings.get(
        "axis_assignments",
        {},
    )

    return [
        column
        for column in y_columns
        if assignments.get(
            column,
            "Left Axis",
        )
        == assignment_name
    ]


def determine_axis_color(
    settings: dict[str, Any],
    series_names: list[str],
    default_color: str,
) -> str:
    """
    Use the series color for an axis only when requested and
    when exactly one series is assigned to that axis.
    """

    if not settings.get(
        "match_axis_colors",
        False,
    ):
        return default_color

    if len(series_names) != 1:
        return default_color

    series_name = series_names[0]

    return settings.get(
        "series_styles",
        {},
    ).get(
        series_name,
        {},
    ).get(
        "color",
        default_color,
    )


# ============================================================
# MAIN FIGURE FUNCTION
# ============================================================

def create_basic_figure(
    dataset: dict[str, Any],
    settings: dict[str, Any],
) -> tuple[
    Optional[go.Figure],
    list[dict[str, Any]],
    Optional[str],
]:
    """
    Create a customized Plotly figure with:

    - Line, scatter, and bar charts
    - Multiple Y-series
    - Left and right Y-axes
    - Series-specific colors and styles
    - Optional curve fitting
    - Linear and logarithmic axes
    - White and black backgrounds

    Returns:
        figure, fit_results, error_message
    """

    try:
        rows = dataset.get(
            "rows",
            [],
        )

        columns = dataset.get(
            "columns",
            [],
        )

        x_column = settings.get(
            "x_column"
        )

        y_columns = settings.get(
            "y_columns",
            [],
        )

        graph_type = settings.get(
            "graph_type",
            "Line Plot",
        )

        # ====================================================
        # BASIC VALIDATION
        # ====================================================

        if not rows:
            return None, [], (
                "The dataset does not contain any rows."
            )

        if not columns:
            return None, [], (
                "The dataset does not contain column headings."
            )

        if not x_column:
            return None, [], (
                "Select an X-axis column."
            )

        if x_column not in columns:
            return None, [], (
                f'The selected X-axis column "{x_column}" '
                "does not exist."
            )

        if not y_columns:
            return None, [], (
                "Select at least one Y-axis column."
            )

        missing_y_columns = [
            column
            for column in y_columns
            if column not in columns
        ]

        if missing_y_columns:
            return None, [], (
                "These selected Y-axis columns do not exist: "
                + ", ".join(
                    missing_y_columns
                )
            )

        figure = go.Figure()

        fit_results: list[
            dict[str, Any]
        ] = []

        all_numeric_x_values: list[float] = []

        left_axis_y_values: list[float] = []

        right_axis_y_values: list[float] = []

        series_numeric_data: dict[
            str,
            tuple[
                list[float],
                list[float],
            ],
        ] = {}

        # ====================================================
        # BUILD EACH DATA SERIES
        # ====================================================

        for y_column in y_columns:
            x_values: list[Any] = []

            y_values: list[float] = []

            numeric_x_for_fit: list[float] = []

            numeric_y_for_fit: list[float] = []

            plotly_axis_name = get_series_axis_name(
                settings,
                y_column,
            )

            for row in rows:
                raw_x = row.get(
                    x_column,
                    "",
                )

                raw_y = row.get(
                    y_column,
                    "",
                )

                numeric_y = to_float(
                    raw_y
                )

                if numeric_y is None:
                    continue

                numeric_x = to_float(
                    raw_x
                )

                if numeric_x is None:
                    clean_x: Any = str(
                        raw_x
                    ).strip()

                    if not clean_x:
                        continue

                else:
                    clean_x = numeric_x

                    all_numeric_x_values.append(
                        numeric_x
                    )

                    numeric_x_for_fit.append(
                        numeric_x
                    )

                    numeric_y_for_fit.append(
                        numeric_y
                    )

                x_values.append(
                    clean_x
                )

                y_values.append(
                    numeric_y
                )

                if plotly_axis_name == "y2":
                    right_axis_y_values.append(
                        numeric_y
                    )

                else:
                    left_axis_y_values.append(
                        numeric_y
                    )

            if not x_values:
                return None, [], (
                    f'No usable X/Y values were found for "{y_column}".'
                )

            series_numeric_data[
                y_column
            ] = (
                numeric_x_for_fit,
                numeric_y_for_fit,
            )

            style = settings.get(
                "series_styles",
                {},
            ).get(
                y_column,
                {},
            )

            color = style.get(
                "color",
                "#2563EB",
            )

            opacity = float(
                style.get(
                    "opacity",
                    0.90,
                )
            )

            marker_symbol = MARKER_SYMBOL_MAP.get(
                style.get(
                    "marker_style",
                    "Circle",
                ),
                "circle",
            )

            marker_size = int(
                style.get(
                    "marker_size",
                    8,
                )
            )

            line_dash = LINE_DASH_MAP.get(
                style.get(
                    "line_style",
                    "Solid",
                ),
                "solid",
            )

            line_width = int(
                style.get(
                    "line_width",
                    2,
                )
            )

            # ================================================
            # LINE PLOT
            # ================================================

            if graph_type == "Line Plot":
                display_mode = DISPLAY_MODE_MAP.get(
                    style.get(
                        "display_mode",
                        "Lines and Markers",
                    ),
                    "lines+markers",
                )

                figure.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode=display_mode,
                        name=y_column,
                        yaxis=plotly_axis_name,
                        opacity=opacity,
                        line={
                            "color": color,
                            "width": line_width,
                            "dash": line_dash,
                        },
                        marker={
                            "color": color,
                            "size": marker_size,
                            "symbol": marker_symbol,
                        },
                        hovertemplate=(
                            f"<b>{y_column}</b><br>"
                            f"{x_column}: %{{x}}<br>"
                            f"{y_column}: %{{y}}"
                            "<extra></extra>"
                        ),
                    )
                )

            # ================================================
            # SCATTER PLOT
            # ================================================

            elif graph_type == "Scatter Plot":
                figure.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode="markers",
                        name=y_column,
                        yaxis=plotly_axis_name,
                        opacity=opacity,
                        marker={
                            "color": color,
                            "size": marker_size,
                            "symbol": marker_symbol,
                        },
                        hovertemplate=(
                            f"<b>{y_column}</b><br>"
                            f"{x_column}: %{{x}}<br>"
                            f"{y_column}: %{{y}}"
                            "<extra></extra>"
                        ),
                    )
                )

            # ================================================
            # BAR CHART
            # ================================================

            elif graph_type == "Bar Chart":
                figure.add_trace(
                    go.Bar(
                        x=x_values,
                        y=y_values,
                        name=y_column,
                        yaxis=plotly_axis_name,
                        opacity=opacity,
                        marker={
                            "color": color,
                        },
                        hovertemplate=(
                            f"<b>{y_column}</b><br>"
                            f"{x_column}: %{{x}}<br>"
                            f"{y_column}: %{{y}}"
                            "<extra></extra>"
                        ),
                    )
                )

            else:
                return None, [], (
                    f'Unknown graph type: "{graph_type}".'
                )

        # ====================================================
        # CURVE FITTING
        # ====================================================

        if settings.get(
            "fit_enabled",
            False,
        ):
            fit_columns = settings.get(
                "fit_columns",
                [],
            )

            for fit_column in fit_columns:
                fit_x, fit_y = series_numeric_data.get(
                    fit_column,
                    (
                        [],
                        [],
                    ),
                )

                model_name = settings.get(
                    "fit_model",
                    "Linear",
                )

                if len(fit_x) < 2:
                    fit_results.append(
                        {
                            "series": fit_column,
                            "model": model_name,
                            "error": (
                                "Curve fitting requires at least "
                                "two numeric X/Y pairs."
                            ),
                        }
                    )

                    continue

                fit_result, fit_error = fit_curve(
                    x_values=fit_x,
                    y_values=fit_y,
                    model_name=model_name,
                    polynomial_degree=settings.get(
                        "polynomial_degree",
                        2,
                    ),
                    moving_average_window=settings.get(
                        "moving_average_window",
                        3,
                    ),
                    fit_points=settings.get(
                        "fit_points",
                        300,
                    ),
                )

                if fit_error:
                    fit_results.append(
                        {
                            "series": fit_column,
                            "model": model_name,
                            "error": fit_error,
                        }
                    )

                    continue

                if fit_result is None:
                    fit_results.append(
                        {
                            "series": fit_column,
                            "model": model_name,
                            "error": (
                                "The fitting function returned no result."
                            ),
                        }
                    )

                    continue

                fit_color = settings.get(
                    "series_styles",
                    {},
                ).get(
                    fit_column,
                    {},
                ).get(
                    "color",
                    "#2563EB",
                )

                fit_name = (
                    f"{fit_column} — "
                    f"{fit_result['model']} fit"
                )

                if settings.get(
                    "show_fit_equation",
                    True,
                ):
                    fit_name += (
                        f"<br>{fit_result['equation']}"
                    )

                figure.add_trace(
                    go.Scatter(
                        x=fit_result[
                            "x_fit"
                        ],
                        y=fit_result[
                            "y_fit"
                        ],
                        mode="lines",
                        name=fit_name,
                        yaxis=get_series_axis_name(
                            settings,
                            fit_column,
                        ),
                        opacity=float(
                            settings.get(
                                "fit_opacity",
                                0.95,
                            )
                        ),
                        line={
                            "color": fit_color,
                            "width": int(
                                settings.get(
                                    "fit_line_width",
                                    3,
                                )
                            ),
                            "dash": LINE_DASH_MAP.get(
                                settings.get(
                                    "fit_line_style",
                                    "Dashed",
                                ),
                                "dash",
                            ),
                        },
                        hovertemplate=(
                            f"<b>{fit_column} fit</b><br>"
                            f"{x_column}: %{{x}}<br>"
                            "Fit value: %{y}"
                            "<extra></extra>"
                        ),
                    )
                )

                fit_result[
                    "series"
                ] = fit_column

                fit_results.append(
                    fit_result
                )

        # ====================================================
        # LOGARITHMIC AXIS VALIDATION
        # ====================================================

        if settings.get(
            "x_scale"
        ) == "Logarithmic":
            x_error = validate_log_values(
                all_numeric_x_values,
                "The X-axis",
            )

            if x_error:
                return None, fit_results, x_error

        if settings.get(
            "y_scale"
        ) == "Logarithmic":
            left_error = validate_log_values(
                left_axis_y_values,
                "The left Y-axis",
            )

            if left_error:
                return None, fit_results, left_error

        if (
            settings.get(
                "show_right_axis",
                False,
            )
            and settings.get(
                "right_y_scale",
                settings.get(
                    "y_scale",
                    "Linear",
                ),
            )
            == "Logarithmic"
        ):
            right_error = validate_log_values(
                right_axis_y_values,
                "The right Y-axis",
            )

            if right_error:
                return None, fit_results, right_error

        # ====================================================
        # BACKGROUND AND COLOR SETTINGS
        # ====================================================

        background = settings.get(
            "background",
            "White",
        )

        if background == "Black":
            template = "plotly_dark"

            paper_color = "#0B0F14"

            plot_color = "#0B0F14"

            text_color = "#F8FAFC"

            grid_color = (
                "rgba(148, 163, 184, 0.25)"
            )

            axis_line_color = "#CBD5E1"

        else:
            template = "plotly_white"

            paper_color = "#FFFFFF"

            plot_color = "#FFFFFF"

            text_color = "#111827"

            grid_color = (
                "rgba(100, 116, 139, 0.22)"
            )

            axis_line_color = "#334155"

        show_grid = settings.get(
            "show_grid",
            True,
        )

        left_axis_series = get_axis_series(
            settings,
            y_columns,
            "Left Axis",
        )

        right_axis_series = get_axis_series(
            settings,
            y_columns,
            "Right Axis",
        )

        left_axis_color = determine_axis_color(
            settings,
            left_axis_series,
            axis_line_color,
        )

        right_axis_color = determine_axis_color(
            settings,
            right_axis_series,
            axis_line_color,
        )

        left_axis_title = settings.get(
            "left_axis_title",
            settings.get(
                "y_axis_title",
                "Primary Y-axis",
            ),
        )

        right_axis_title = settings.get(
            "right_axis_title",
            "Secondary Y-axis",
        )

        # ====================================================
        # FIGURE LAYOUT
        # ====================================================

        figure.update_layout(
            template=template,

            title={
                "text": settings.get(
                    "figure_title",
                    "Scientific Figure",
                ),
                "x": 0.5,
                "xanchor": "center",
                "font": {
                    "size": int(
                        settings.get(
                            "title_font_size",
                            20,
                        )
                    ),
                    "color": text_color,
                },
            },

            xaxis={
                "title": {
                    "text": settings.get(
                        "x_axis_title",
                        x_column,
                    ),
                    "font": {
                        "size": int(
                            settings.get(
                                "axis_font_size",
                                14,
                            )
                        ),
                        "color": text_color,
                    },
                },
                "tickfont": {
                    "size": int(
                        settings.get(
                            "tick_font_size",
                            11,
                        )
                    ),
                    "color": text_color,
                },
                "type": (
                    "log"
                    if settings.get(
                        "x_scale"
                    )
                    == "Logarithmic"
                    else "linear"
                ),
                "showgrid": show_grid,
                "gridcolor": grid_color,
                "zeroline": False,
                "showline": True,
                "linecolor": axis_line_color,
                "ticks": "outside",
            },

            yaxis={
                "title": {
                    "text": left_axis_title,
                    "font": {
                        "size": int(
                            settings.get(
                                "axis_font_size",
                                14,
                            )
                        ),
                        "color": left_axis_color,
                    },
                },
                "tickfont": {
                    "size": int(
                        settings.get(
                            "tick_font_size",
                            11,
                        )
                    ),
                    "color": left_axis_color,
                },
                "type": (
                    "log"
                    if settings.get(
                        "y_scale"
                    )
                    == "Logarithmic"
                    else "linear"
                ),
                "showgrid": show_grid,
                "gridcolor": grid_color,
                "zeroline": False,
                "showline": True,
                "linecolor": left_axis_color,
                "ticks": "outside",
                "side": "left",
            },

            yaxis2={
                "title": {
                    "text": right_axis_title,
                    "font": {
                        "size": int(
                            settings.get(
                                "axis_font_size",
                                14,
                            )
                        ),
                        "color": right_axis_color,
                    },
                },
                "tickfont": {
                    "size": int(
                        settings.get(
                            "tick_font_size",
                            11,
                        )
                    ),
                    "color": right_axis_color,
                },
                "type": (
                    "log"
                    if settings.get(
                        "right_y_scale",
                        settings.get(
                            "y_scale",
                            "Linear",
                        ),
                    )
                    == "Logarithmic"
                    else "linear"
                ),
                "overlaying": "y",
                "side": "right",
                "showgrid": False,
                "zeroline": False,
                "showline": True,
                "linecolor": right_axis_color,
                "ticks": "outside",
                "visible": settings.get(
                    "show_right_axis",
                    False,
                ),
            },

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

            showlegend=settings.get(
                "show_legend",
                True,
            ),

            barmode="group",

            hovermode="x unified",

            paper_bgcolor=paper_color,

            plot_bgcolor=plot_color,

            font={
                "color": text_color,
                "size": int(
                    settings.get(
                        "tick_font_size",
                        11,
                    )
                ),
            },

            margin={
                "l": 90,
                "r": (
                    90
                    if settings.get(
                        "show_right_axis",
                        False,
                    )
                    else 45
                ),
                "t": 90,
                "b": 80,
            },

            legend={
                "title": {
                    "text": "Series",
                },
                "bgcolor": (
                    "rgba(255,255,255,0)"
                ),
            },
        )

        return figure, fit_results, None

    except MemoryError:
        return None, [], (
            "The selected data is too large to plot."
        )

    except Exception as error:
        return None, [], (
            "Figure generation failed. "
            f"Details: {type(error).__name__}: {error}"
        )