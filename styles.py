from __future__ import annotations

import streamlit as st


def apply_app_styles() -> None:
    """
    Apply the FigureForge visual theme.

    This file changes appearance only.
    It does not modify CSV loading, plotting, curve fitting,
    exports, or sidebar behavior.
    """

    st.markdown(
        """
        <style>

        /* =====================================================
           FIGUREFORGE COLOR SYSTEM
        ===================================================== */

        :root {
            --ff-navy: #0f172a;
            --ff-blue-dark: #1e3a8a;
            --ff-blue: #2563eb;
            --ff-blue-medium: #3b82f6;
            --ff-blue-light: #dbeafe;
            --ff-blue-pale: #eff6ff;
            --ff-cyan: #0891b2;
            --ff-background: #f6f9ff;
            --ff-card: #ffffff;
            --ff-border: #dbe7f6;
            --ff-text: #1e293b;
            --ff-muted: #64748b;
            --ff-success: #15803d;
            --ff-shadow: rgba(15, 23, 42, 0.07);
        }


        /* =====================================================
           MAIN APPLICATION
        ===================================================== */

        .stApp {
            background:
                radial-gradient(
                    circle at 92% 4%,
                    rgba(37, 99, 235, 0.12),
                    transparent 26%
                ),
                radial-gradient(
                    circle at 5% 1%,
                    rgba(8, 145, 178, 0.08),
                    transparent 22%
                ),
                linear-gradient(
                    180deg,
                    #f8fbff 0%,
                    #f4f7fc 100%
                );

            color: var(--ff-text);
        }


        .block-container {
            max-width: 1500px;
            padding-top: 1.6rem;
            padding-left: 2.4rem;
            padding-right: 2.4rem;
            padding-bottom: 4rem;
        }


        /* =====================================================
           TEXT AND HEADINGS
        ===================================================== */

        h1 {
            color: var(--ff-navy) !important;
            font-size: 3.15rem !important;
            line-height: 1.05 !important;
            font-weight: 850 !important;
            letter-spacing: -0.045em !important;
            margin-bottom: 0.3rem !important;
        }


        h2 {
            color: var(--ff-blue-dark) !important;
            font-weight: 780 !important;
            letter-spacing: -0.025em !important;
            margin-top: 1.7rem !important;
        }


        h3 {
            color: var(--ff-blue) !important;
            font-weight: 720 !important;
            letter-spacing: -0.015em !important;
        }


        h4,
        h5,
        h6 {
            color: var(--ff-blue-dark) !important;
        }


        p,
        li,
        label {
            color: var(--ff-text);
        }


        [data-testid="stCaptionContainer"] {
            color: var(--ff-muted);
        }


        /* =====================================================
           SIDEBAR
        ===================================================== */

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #ffffff 0%,
                    #f7faff 100%
                );

            border-right: 1px solid var(--ff-border);

            box-shadow:
                8px 0 30px rgba(15, 23, 42, 0.04);
        }


        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.3rem;
        }


        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--ff-blue-dark) !important;
        }


        [data-testid="stSidebar"] hr {
            border-color: var(--ff-border);
            margin-top: 1.3rem;
            margin-bottom: 1.3rem;
        }


        /* =====================================================
           ALERTS
        ===================================================== */

        [data-testid="stAlert"] {
            border-radius: 15px;
            border: 1px solid var(--ff-border);

            box-shadow:
                0 8px 28px rgba(15, 23, 42, 0.055);

            padding: 1rem 1.1rem;
        }


        div[data-baseweb="notification"] {
            border-radius: 15px;
        }


        /* =====================================================
           WORKFLOW CARDS
        ===================================================== */

        div[data-testid="stHorizontalBlock"]
        [data-testid="stAlert"] {
            min-height: 120px;
        }


        /* =====================================================
           METRIC CARDS
        ===================================================== */

        [data-testid="stMetric"] {
            background:
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.98),
                    rgba(248, 251, 255, 0.98)
                );

            border: 1px solid var(--ff-border);
            border-radius: 16px;
            padding: 1.05rem 1.1rem;

            box-shadow:
                0 10px 30px rgba(15, 23, 42, 0.06);

            transition:
                transform 0.18s ease,
                box-shadow 0.18s ease;
        }


        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);

            box-shadow:
                0 14px 35px rgba(15, 23, 42, 0.09);
        }


        [data-testid="stMetricLabel"] {
            color: var(--ff-muted);
            font-weight: 650;
        }


        [data-testid="stMetricValue"] {
            color: var(--ff-navy);
            font-weight: 820;
        }


        /* =====================================================
           EXPANDERS
        ===================================================== */

        [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid var(--ff-border);
            border-radius: 15px;
            overflow: hidden;

            box-shadow:
                0 7px 24px rgba(15, 23, 42, 0.045);
        }


        [data-testid="stExpander"] summary {
            font-weight: 700;
            color: var(--ff-blue-dark);
        }


        /* =====================================================
           FILE UPLOADER
        ===================================================== */

        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid var(--ff-border);
            border-radius: 16px;
            padding: 0.45rem;

            box-shadow:
                0 8px 25px rgba(15, 23, 42, 0.045);
        }


        [data-testid="stFileUploaderDropzone"] {
            border-radius: 13px;
            border: 1.5px dashed #93c5fd;

            background:
                linear-gradient(
                    135deg,
                    rgba(239, 246, 255, 0.96),
                    rgba(248, 250, 252, 0.96)
                );
        }


        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: var(--ff-blue);
            background: #eff6ff;
        }


        /* =====================================================
           STANDARD BUTTONS
        ===================================================== */

        .stButton > button {
            min-height: 2.85rem;
            border-radius: 11px;
            font-weight: 750;
            border: 1px solid #93c5fd;

            transition:
                transform 0.15s ease,
                box-shadow 0.15s ease,
                background 0.15s ease;
        }


        .stButton > button:hover {
            transform: translateY(-1px);

            box-shadow:
                0 8px 20px rgba(37, 99, 235, 0.16);
        }


        .stButton > button[kind="primary"] {
            background:
                linear-gradient(
                    135deg,
                    #2563eb 0%,
                    #1d4ed8 55%,
                    #1e40af 100%
                );

            color: #ffffff;
            border: 1px solid #1d4ed8;

            box-shadow:
                0 10px 22px rgba(37, 99, 235, 0.24);
        }


        .stButton > button[kind="primary"]:hover {
            background:
                linear-gradient(
                    135deg,
                    #1d4ed8 0%,
                    #1e40af 100%
                );

            color: #ffffff;
        }


        /* =====================================================
           DOWNLOAD BUTTONS
        ===================================================== */

        .stDownloadButton > button {
            width: 100%;
            min-height: 2.85rem;
            border-radius: 11px;
            font-weight: 750;
            border: 1px solid #93c5fd;

            transition:
                transform 0.15s ease,
                box-shadow 0.15s ease;
        }


        .stDownloadButton > button:hover {
            transform: translateY(-1px);

            box-shadow:
                0 8px 20px rgba(37, 99, 235, 0.16);
        }


        /* =====================================================
           LINK BUTTONS
        ===================================================== */

        .stLinkButton > a {
            width: 100%;
            min-height: 2.85rem;
            border-radius: 11px;
            font-weight: 700;
            border: 1px solid #93c5fd;
            background: #eff6ff;
            color: #1e3a8a;

            display: flex;
            align-items: center;
            justify-content: center;

            text-decoration: none;

            transition:
                transform 0.15s ease,
                box-shadow 0.15s ease,
                background 0.15s ease;
        }


        .stLinkButton > a:hover {
            background: #dbeafe;
            color: #1e40af;
            transform: translateY(-1px);

            box-shadow:
                0 8px 20px rgba(37, 99, 235, 0.14);
        }


        /* =====================================================
           TEXT INPUTS, SELECTS, AND TEXT AREAS
        ===================================================== */

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div {
            border-radius: 11px;
            border-color: var(--ff-border);
            background: #ffffff;
        }


        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within {
            border-color: var(--ff-blue);

            box-shadow:
                0 0 0 2px rgba(37, 99, 235, 0.12);
        }


        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input {
            border-radius: 10px;
        }


        /* =====================================================
           MULTISELECT TAGS
        ===================================================== */

        span[data-baseweb="tag"] {
            background: #dbeafe !important;
            color: #1e3a8a !important;
            border-radius: 8px !important;
            font-weight: 650;
        }


        /* =====================================================
           SLIDERS
        ===================================================== */

        [data-testid="stSlider"] {
            padding-top: 0.2rem;
            padding-bottom: 0.2rem;
        }


        /* =====================================================
           TOGGLES
        ===================================================== */

        [data-testid="stToggle"] label {
            font-weight: 600;
        }


        /* =====================================================
           CODE BLOCKS
        ===================================================== */

        [data-testid="stCodeBlock"] {
            border-radius: 13px;
            border: 1px solid var(--ff-border);

            box-shadow:
                0 6px 18px rgba(15, 23, 42, 0.035);
        }


        pre {
            border-radius: 13px !important;
        }


        /* =====================================================
           PLOTLY CHART CONTAINER
        ===================================================== */

        [data-testid="stPlotlyChart"] {
            background: #ffffff;
            border: 1px solid var(--ff-border);
            border-radius: 18px;
            padding: 0.8rem;

            box-shadow:
                0 14px 38px rgba(15, 23, 42, 0.07);
        }


        /* =====================================================
           DATA TABLES
        ===================================================== */

        [data-testid="stTable"] {
            background: #ffffff;
            border: 1px solid var(--ff-border);
            border-radius: 14px;
            overflow: hidden;
        }


        [data-testid="stDataFrame"] {
            background: #ffffff;
            border: 1px solid var(--ff-border);
            border-radius: 14px;
            overflow: hidden;
        }


        /* =====================================================
           IMAGES
        ===================================================== */

        [data-testid="stImage"] img {
            border-radius: 14px;
        }


        [data-testid="stImage"] {
            max-width: 100%;
        }


        /* =====================================================
           DIVIDERS
        ===================================================== */

        hr {
            border: none;
            border-top: 1px solid var(--ff-border);
        }


        /* =====================================================
           FOOTER
        ===================================================== */

        .figureforge-footer {
            text-align: center;
            color: #475569;
            padding: 1.5rem 1rem 0.5rem 1rem;
            font-size: 0.98rem;
            line-height: 1.7;
        }


        .figureforge-footer strong {
            color: #1e3a8a;
            font-size: 1.08rem;
        }


        /* =====================================================
           MOBILE AND SMALL WINDOW SUPPORT
        ===================================================== */

        @media (max-width: 900px) {

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }


            h1 {
                font-size: 2.25rem !important;
            }


            div[data-testid="stHorizontalBlock"]
            [data-testid="stAlert"] {
                min-height: auto;
            }
        }


        </style>
        """,
        unsafe_allow_html=True,
    )