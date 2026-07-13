from __future__ import annotations

from typing import Any, Optional

import plotly.graph_objects as go
import plotly.io as pio


SUPPORTED_EXPORT_FORMATS = {
    "PNG": {
        "extension": "png",
        "mime": "image/png",
        "static": True,
    },
    "JPEG": {
        "extension": "jpg",
        "mime": "image/jpeg",
        "static": True,
    },
    "WebP": {
        "extension": "webp",
        "mime": "image/webp",
        "static": True,
    },
    "SVG": {
        "extension": "svg",
        "mime": "image/svg+xml",
        "static": True,
    },
    "PDF": {
        "extension": "pdf",
        "mime": "application/pdf",
        "static": True,
    },
    "Interactive HTML": {
        "extension": "html",
        "mime": "text/html",
        "static": False,
    },
}


def clean_filename(
    filename: str,
) -> str:
    """
    Create a safe export filename.
    """

    cleaned = "".join(
        character
        if character.isalnum()
        or character in {
            "-",
            "_",
        }
        else "_"
        for character in str(filename).strip()
    )

    cleaned = cleaned.strip("_")

    if not cleaned:
        return "figureforge_figure"

    return cleaned


def export_figure(
    figure: go.Figure,
    export_format: str,
    filename: str,
    width: int,
    height: int,
    scale: float = 2.0,
) -> tuple[
    Optional[bytes],
    Optional[str],
    Optional[str],
    Optional[str],
]:
    """
    Convert a Plotly figure into downloadable data.

    Returns:
        file_data
        completed_filename
        MIME type
        error_message
    """

    if export_format not in SUPPORTED_EXPORT_FORMATS:
        return (
            None,
            None,
            None,
            f'Unsupported export format: "{export_format}".',
        )

    format_information = SUPPORTED_EXPORT_FORMATS[
        export_format
    ]

    extension = format_information[
        "extension"
    ]

    mime_type = format_information[
        "mime"
    ]

    safe_filename = clean_filename(
        filename
    )

    completed_filename = (
        f"{safe_filename}.{extension}"
    )

    try:
        if export_format == "Interactive HTML":
            html_text = figure.to_html(
                full_html=True,
                include_plotlyjs=True,
                config={
                    "displaylogo": False,
                    "responsive": True,
                    "scrollZoom": True,
                },
            )

            return (
                html_text.encode("utf-8"),
                completed_filename,
                mime_type,
                None,
            )

        plotly_format = (
            "jpeg"
            if export_format == "JPEG"
            else extension
        )

        image_bytes = pio.to_image(
            figure,
            format=plotly_format,
            width=int(width),
            height=int(height),
            scale=float(scale),
            engine="kaleido",
        )

        if not image_bytes:
            return (
                None,
                None,
                None,
                "The exporter returned an empty file.",
            )

        return (
            image_bytes,
            completed_filename,
            mime_type,
            None,
        )

    except MemoryError:
        return (
            None,
            None,
            None,
            "The export used too much memory. "
            "Reduce the figure dimensions or export scale.",
        )

    except Exception as error:
        return (
            None,
            None,
            None,
            "Export failed. "
            f"Details: {type(error).__name__}: {error}",
        )