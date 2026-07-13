from __future__ import annotations

from typing import Any

import streamlit as st


AXIS_ASSIGNMENTS = [
    "Left Axis",
    "Right Axis",
]


def make_safe_axis_key(
    index: int,
    column_name: str,
) -> str:
    """
    Create a stable Streamlit key for one data series.
    """

    cleaned_name = "".join(
        character
        if character.isalnum()
        else "_"
        for character in column_name
    )

    return f"axis_{index}_{cleaned_name}"


def render_axis_controls(
    y_columns: list[str],
) -> dict[str, Any]:
    """
    Render safe left/right Y-axis assignment controls.

    The first selected Y-series defaults to the left axis.
    Additional Y-series also default to the left axis until
    the user explicitly assigns them to the right axis.
    """

    axis_assignments: dict[str, str] = {}

    with st.expander(
        "Axis Assignment",
        expanded=False,
    ):
        if not y_columns:
            st.info(
                "Select at least one Y-axis series."
            )

            return {
                "axis_assignments": {},
                "left_axis_title": "Primary Y-axis",
                "right_axis_title": "Secondary Y-axis",
                "show_right_axis": False,
                "match_axis_colors": False,
            }

        st.caption(
            "Assign each selected data series to the left or right Y-axis."
        )

        for index, y_column in enumerate(
            y_columns
        ):
            axis_key = make_safe_axis_key(
                index,
                y_column,
            )

            assignment = st.selectbox(
                f"Axis for {y_column}",
                options=AXIS_ASSIGNMENTS,
                index=0,
                key=axis_key,
            )

            axis_assignments[
                y_column
            ] = assignment

        show_right_axis = any(
            assignment == "Right Axis"
            for assignment in axis_assignments.values()
        )

        left_axis_title = st.text_input(
            "Left Y-axis title",
            value=(
                ", ".join(
                    column
                    for column in y_columns
                    if axis_assignments.get(
                        column
                    ) == "Left Axis"
                )
                or "Primary Y-axis"
            ),
        )

        right_axis_title = st.text_input(
            "Right Y-axis title",
            value=(
                ", ".join(
                    column
                    for column in y_columns
                    if axis_assignments.get(
                        column
                    ) == "Right Axis"
                )
                or "Secondary Y-axis"
            ),
            disabled=not show_right_axis,
        )

        match_axis_colors = st.toggle(
            "Match axis titles to series colors",
            value=False,
            key="axes_match_axis_colors",
            help=(
                "When each axis contains one series, its title and ticks "
                "can use that series color."
            ),
        )

    return {
        "axis_assignments": axis_assignments,
        "left_axis_title": left_axis_title,
        "right_axis_title": right_axis_title,
        "show_right_axis": show_right_axis,
        "match_axis_colors": match_axis_colors,
    }