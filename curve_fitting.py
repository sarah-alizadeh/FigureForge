from __future__ import annotations

import math
from typing import Any, Optional


# ============================================================
# BASIC HELPERS
# ============================================================

def to_float(
    value: Any,
) -> Optional[float]:
    """
    Convert a value to a finite float.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    try:
        number = float(text)

    except (TypeError, ValueError):
        return None

    if not math.isfinite(number):
        return None

    return number


def format_number(
    value: float,
) -> str:
    """
    Format fitted coefficients for readable equations.
    """

    if not math.isfinite(value):
        return "undefined"

    absolute_value = abs(value)

    if (
        absolute_value != 0
        and (
            absolute_value >= 10000
            or absolute_value < 0.001
        )
    ):
        return f"{value:.4e}"

    return f"{value:.6g}"


def calculate_statistics(
    observed: list[float],
    predicted: list[float],
) -> dict[str, float]:
    """
    Calculate R², RMSE, and MAE.
    """

    if not observed:
        return {
            "r_squared": float("nan"),
            "rmse": float("nan"),
            "mae": float("nan"),
        }

    if len(observed) != len(predicted):
        return {
            "r_squared": float("nan"),
            "rmse": float("nan"),
            "mae": float("nan"),
        }

    mean_observed = sum(observed) / len(observed)

    squared_residuals = [
        (actual - estimate) ** 2
        for actual, estimate in zip(
            observed,
            predicted,
        )
    ]

    absolute_residuals = [
        abs(actual - estimate)
        for actual, estimate in zip(
            observed,
            predicted,
        )
    ]

    residual_sum_of_squares = sum(
        squared_residuals
    )

    total_sum_of_squares = sum(
        (
            actual
            - mean_observed
        )
        ** 2
        for actual in observed
    )

    if math.isclose(
        total_sum_of_squares,
        0.0,
        abs_tol=1e-15,
    ):
        r_squared = (
            1.0
            if math.isclose(
                residual_sum_of_squares,
                0.0,
                abs_tol=1e-15,
            )
            else 0.0
        )

    else:
        r_squared = (
            1.0
            - residual_sum_of_squares
            / total_sum_of_squares
        )

    rmse = math.sqrt(
        residual_sum_of_squares
        / len(observed)
    )

    mae = sum(
        absolute_residuals
    ) / len(observed)

    return {
        "r_squared": r_squared,
        "rmse": rmse,
        "mae": mae,
    }


# ============================================================
# LINEAR ALGEBRA
# ============================================================

def solve_linear_system(
    matrix: list[list[float]],
    vector: list[float],
) -> Optional[list[float]]:
    """
    Solve A*x=b using Gaussian elimination with partial pivoting.

    This avoids NumPy and SciPy.
    """

    size = len(vector)

    if size == 0:
        return None

    if len(matrix) != size:
        return None

    augmented = [
        [
            float(value)
            for value in matrix[row]
        ]
        + [
            float(vector[row])
        ]
        for row in range(size)
    ]

    try:
        for pivot_column in range(size):
            pivot_row = max(
                range(
                    pivot_column,
                    size,
                ),
                key=lambda row: abs(
                    augmented[row][
                        pivot_column
                    ]
                ),
            )

            pivot_value = augmented[
                pivot_row
            ][
                pivot_column
            ]

            if math.isclose(
                pivot_value,
                0.0,
                abs_tol=1e-14,
            ):
                return None

            if pivot_row != pivot_column:
                augmented[
                    pivot_column
                ], augmented[
                    pivot_row
                ] = (
                    augmented[
                        pivot_row
                    ],
                    augmented[
                        pivot_column
                    ],
                )

            pivot_value = augmented[
                pivot_column
            ][
                pivot_column
            ]

            for column in range(
                pivot_column,
                size + 1,
            ):
                augmented[
                    pivot_column
                ][column] /= pivot_value

            for row in range(size):
                if row == pivot_column:
                    continue

                elimination_factor = augmented[
                    row
                ][
                    pivot_column
                ]

                for column in range(
                    pivot_column,
                    size + 1,
                ):
                    augmented[
                        row
                    ][column] -= (
                        elimination_factor
                        * augmented[
                            pivot_column
                        ][column]
                    )

        solution = [
            augmented[row][size]
            for row in range(size)
        ]

        if not all(
            math.isfinite(value)
            for value in solution
        ):
            return None

        return solution

    except (
        ArithmeticError,
        IndexError,
        TypeError,
        ValueError,
    ):
        return None


# ============================================================
# POLYNOMIAL FITTING
# ============================================================

def polynomial_fit(
    x_values: list[float],
    y_values: list[float],
    degree: int,
) -> tuple[
    Optional[list[float]],
    Optional[str],
]:
    """
    Fit a polynomial using least-squares normal equations.

    Coefficients are returned from lowest to highest power:
    c0 + c1*x + c2*x² + ...
    """

    if degree < 1:
        return None, (
            "Polynomial degree must be at least 1."
        )

    if len(x_values) != len(y_values):
        return None, (
            "X and Y contain different numbers of values."
        )

    minimum_points = degree + 1

    if len(x_values) < minimum_points:
        return None, (
            f"A degree-{degree} polynomial requires "
            f"at least {minimum_points} points."
        )

    if len(set(x_values)) < minimum_points:
        return None, (
            f"A degree-{degree} polynomial requires "
            f"at least {minimum_points} unique X values."
        )

    matrix_size = degree + 1

    matrix: list[list[float]] = [
        [0.0] * matrix_size
        for _ in range(matrix_size)
    ]

    vector: list[float] = [
        0.0
    ] * matrix_size

    try:
        for row in range(matrix_size):
            for column in range(
                matrix_size
            ):
                power = row + column

                matrix[row][column] = sum(
                    x_value ** power
                    for x_value in x_values
                )

            vector[row] = sum(
                y_value
                * (
                    x_value ** row
                )
                for x_value, y_value
                in zip(
                    x_values,
                    y_values,
                )
            )

    except OverflowError:
        return None, (
            "Polynomial fitting overflowed. "
            "Try a lower degree or smaller X values."
        )

    coefficients = solve_linear_system(
        matrix,
        vector,
    )

    if coefficients is None:
        return None, (
            "The polynomial fit could not be solved. "
            "The data may be singular or poorly conditioned."
        )

    return coefficients, None


def evaluate_polynomial(
    x_value: float,
    coefficients: list[float],
) -> float:
    """
    Evaluate a polynomial using Horner's method.
    """

    result = 0.0

    for coefficient in reversed(
        coefficients
    ):
        result = (
            result * x_value
            + coefficient
        )

    return result


def polynomial_equation(
    coefficients: list[float],
) -> str:
    """
    Convert polynomial coefficients to an equation string.
    """

    terms: list[str] = []

    for power in reversed(
        range(
            len(coefficients)
        )
    ):
        coefficient = coefficients[
            power
        ]

        coefficient_text = format_number(
            coefficient
        )

        if power == 0:
            term = coefficient_text

        elif power == 1:
            term = (
                f"({coefficient_text})x"
            )

        else:
            term = (
                f"({coefficient_text})x^{power}"
            )

        terms.append(term)

    return "y = " + " + ".join(terms)


# ============================================================
# TRANSFORMED MODELS
# ============================================================

def fit_linear_transformed_model(
    transformed_x: list[float],
    transformed_y: list[float],
) -> tuple[
    Optional[float],
    Optional[float],
    Optional[str],
]:
    """
    Fit transformed_y = slope*transformed_x + intercept.
    """

    coefficients, error = polynomial_fit(
        transformed_x,
        transformed_y,
        degree=1,
    )

    if error:
        return None, None, error

    if coefficients is None:
        return None, None, (
            "The transformed linear model could not be solved."
        )

    intercept = coefficients[0]
    slope = coefficients[1]

    return slope, intercept, None


# ============================================================
# MOVING AVERAGE
# ============================================================

def moving_average(
    x_values: list[float],
    y_values: list[float],
    window_size: int,
) -> tuple[
    Optional[list[float]],
    Optional[list[float]],
    Optional[str],
]:
    """
    Calculate a centered moving average.
    """

    if window_size < 2:
        return None, None, (
            "The moving-average window must be at least 2."
        )

    if window_size > len(y_values):
        return None, None, (
            "The moving-average window is larger than "
            "the number of available points."
        )

    smooth_x: list[float] = []
    smooth_y: list[float] = []

    for start_index in range(
        0,
        len(y_values)
        - window_size
        + 1,
    ):
        end_index = (
            start_index
            + window_size
        )

        x_window = x_values[
            start_index:end_index
        ]

        y_window = y_values[
            start_index:end_index
        ]

        smooth_x.append(
            sum(x_window)
            / len(x_window)
        )

        smooth_y.append(
            sum(y_window)
            / len(y_window)
        )

    return smooth_x, smooth_y, None


# ============================================================
# MAIN FIT FUNCTION
# ============================================================

def fit_curve(
    x_values: list[float],
    y_values: list[float],
    model_name: str,
    polynomial_degree: int = 2,
    moving_average_window: int = 3,
    fit_points: int = 300,
) -> tuple[
    Optional[dict[str, Any]],
    Optional[str],
]:
    """
    Fit one selected model.

    Supported:
    - Linear
    - Polynomial
    - Exponential
    - Logarithmic
    - Power Law
    - Moving Average
    """

    try:
        if len(x_values) != len(y_values):
            return None, (
                "X and Y contain different numbers of values."
            )

        finite_pairs = [
            (
                float(x_value),
                float(y_value),
            )
            for x_value, y_value
            in zip(
                x_values,
                y_values,
            )
            if (
                math.isfinite(
                    float(x_value)
                )
                and math.isfinite(
                    float(y_value)
                )
            )
        ]

        if len(finite_pairs) < 2:
            return None, (
                "At least two finite numeric points are required."
            )

        finite_pairs.sort(
            key=lambda pair: pair[0]
        )

        clean_x = [
            pair[0]
            for pair in finite_pairs
        ]

        clean_y = [
            pair[1]
            for pair in finite_pairs
        ]

        x_minimum = min(clean_x)
        x_maximum = max(clean_x)

        if math.isclose(
            x_minimum,
            x_maximum,
            abs_tol=1e-15,
        ):
            return None, (
                "Curve fitting requires at least two unique X values."
            )

        dense_count = max(
            50,
            min(
                int(fit_points),
                2000,
            ),
        )

        dense_x = [
            x_minimum
            + (
                x_maximum
                - x_minimum
            )
            * index
            / (
                dense_count - 1
            )
            for index in range(
                dense_count
            )
        ]

        # ----------------------------------------------------
        # LINEAR
        # ----------------------------------------------------

        if model_name == "Linear":
            coefficients, error = polynomial_fit(
                clean_x,
                clean_y,
                degree=1,
            )

            if error:
                return None, error

            if coefficients is None:
                return None, (
                    "Linear fitting failed."
                )

            predicted_observed = [
                evaluate_polynomial(
                    x_value,
                    coefficients,
                )
                for x_value in clean_x
            ]

            dense_y = [
                evaluate_polynomial(
                    x_value,
                    coefficients,
                )
                for x_value in dense_x
            ]

            equation = polynomial_equation(
                coefficients
            )

            parameters = {
                "intercept": coefficients[0],
                "slope": coefficients[1],
            }

        # ----------------------------------------------------
        # POLYNOMIAL
        # ----------------------------------------------------

        elif model_name == "Polynomial":
            degree = max(
                2,
                min(
                    int(
                        polynomial_degree
                    ),
                    5,
                ),
            )

            coefficients, error = polynomial_fit(
                clean_x,
                clean_y,
                degree=degree,
            )

            if error:
                return None, error

            if coefficients is None:
                return None, (
                    "Polynomial fitting failed."
                )

            predicted_observed = [
                evaluate_polynomial(
                    x_value,
                    coefficients,
                )
                for x_value in clean_x
            ]

            dense_y = [
                evaluate_polynomial(
                    x_value,
                    coefficients,
                )
                for x_value in dense_x
            ]

            equation = polynomial_equation(
                coefficients
            )

            parameters = {
                f"coefficient_x^{power}": coefficient
                for power, coefficient
                in enumerate(
                    coefficients
                )
            }

        # ----------------------------------------------------
        # EXPONENTIAL
        # y = A * exp(Bx)
        # ----------------------------------------------------

        elif model_name == "Exponential":
            valid_pairs = [
                (
                    x_value,
                    y_value,
                )
                for x_value, y_value
                in zip(
                    clean_x,
                    clean_y,
                )
                if y_value > 0
            ]

            if len(valid_pairs) < 2:
                return None, (
                    "Exponential fitting requires at least "
                    "two positive Y values."
                )

            transformed_x = [
                pair[0]
                for pair in valid_pairs
            ]

            transformed_y = [
                math.log(
                    pair[1]
                )
                for pair in valid_pairs
            ]

            slope, intercept, error = (
                fit_linear_transformed_model(
                    transformed_x,
                    transformed_y,
                )
            )

            if error:
                return None, error

            if (
                slope is None
                or intercept is None
            ):
                return None, (
                    "Exponential fitting failed."
                )

            amplitude = math.exp(
                intercept
            )

            predicted_observed = [
                amplitude
                * math.exp(
                    slope * x_value
                )
                for x_value in clean_x
            ]

            dense_y = [
                amplitude
                * math.exp(
                    slope * x_value
                )
                for x_value in dense_x
            ]

            equation = (
                "y = "
                f"{format_number(amplitude)}"
                " exp("
                f"{format_number(slope)}x)"
            )

            parameters = {
                "amplitude": amplitude,
                "rate": slope,
            }

        # ----------------------------------------------------
        # LOGARITHMIC
        # y = A ln(x) + B
        # ----------------------------------------------------

        elif model_name == "Logarithmic":
            valid_pairs = [
                (
                    x_value,
                    y_value,
                )
                for x_value, y_value
                in zip(
                    clean_x,
                    clean_y,
                )
                if x_value > 0
            ]

            if len(valid_pairs) < 2:
                return None, (
                    "Logarithmic fitting requires at least "
                    "two positive X values."
                )

            transformed_x = [
                math.log(
                    pair[0]
                )
                for pair in valid_pairs
            ]

            transformed_y = [
                pair[1]
                for pair in valid_pairs
            ]

            slope, intercept, error = (
                fit_linear_transformed_model(
                    transformed_x,
                    transformed_y,
                )
            )

            if error:
                return None, error

            if (
                slope is None
                or intercept is None
            ):
                return None, (
                    "Logarithmic fitting failed."
                )

            positive_dense_x = [
                x_value
                for x_value in dense_x
                if x_value > 0
            ]

            if not positive_dense_x:
                return None, (
                    "No positive X range is available "
                    "for the logarithmic curve."
                )

            predicted_observed = [
                (
                    slope
                    * math.log(
                        x_value
                    )
                    + intercept
                )
                if x_value > 0
                else float("nan")
                for x_value in clean_x
            ]

            dense_x = positive_dense_x

            dense_y = [
                slope
                * math.log(
                    x_value
                )
                + intercept
                for x_value in dense_x
            ]

            equation = (
                "y = "
                f"{format_number(slope)}"
                " ln(x) + "
                f"{format_number(intercept)}"
            )

            parameters = {
                "coefficient": slope,
                "intercept": intercept,
            }

        # ----------------------------------------------------
        # POWER LAW
        # y = A*x^B
        # ----------------------------------------------------

        elif model_name == "Power Law":
            valid_pairs = [
                (
                    x_value,
                    y_value,
                )
                for x_value, y_value
                in zip(
                    clean_x,
                    clean_y,
                )
                if (
                    x_value > 0
                    and y_value > 0
                )
            ]

            if len(valid_pairs) < 2:
                return None, (
                    "Power-law fitting requires at least "
                    "two points with positive X and Y values."
                )

            transformed_x = [
                math.log(
                    pair[0]
                )
                for pair in valid_pairs
            ]

            transformed_y = [
                math.log(
                    pair[1]
                )
                for pair in valid_pairs
            ]

            exponent, log_amplitude, error = (
                fit_linear_transformed_model(
                    transformed_x,
                    transformed_y,
                )
            )

            if error:
                return None, error

            if (
                exponent is None
                or log_amplitude is None
            ):
                return None, (
                    "Power-law fitting failed."
                )

            amplitude = math.exp(
                log_amplitude
            )

            positive_dense_x = [
                x_value
                for x_value in dense_x
                if x_value > 0
            ]

            if not positive_dense_x:
                return None, (
                    "No positive X range is available "
                    "for the power-law curve."
                )

            predicted_observed = [
                (
                    amplitude
                    * (
                        x_value ** exponent
                    )
                )
                if x_value > 0
                else float("nan")
                for x_value in clean_x
            ]

            dense_x = positive_dense_x

            dense_y = [
                amplitude
                * (
                    x_value ** exponent
                )
                for x_value in dense_x
            ]

            equation = (
                "y = "
                f"{format_number(amplitude)}"
                " x^"
                f"{format_number(exponent)}"
            )

            parameters = {
                "amplitude": amplitude,
                "exponent": exponent,
            }

        # ----------------------------------------------------
        # MOVING AVERAGE
        # ----------------------------------------------------

        elif model_name == "Moving Average":
            (
                smooth_x,
                smooth_y,
                moving_error,
            ) = moving_average(
                clean_x,
                clean_y,
                window_size=int(
                    moving_average_window
                ),
            )

            if moving_error:
                return None, moving_error

            if (
                smooth_x is None
                or smooth_y is None
            ):
                return None, (
                    "Moving-average calculation failed."
                )

            statistics = {
                "r_squared": float("nan"),
                "rmse": float("nan"),
                "mae": float("nan"),
            }

            return {
                "model": model_name,
                "x_fit": smooth_x,
                "y_fit": smooth_y,
                "equation": (
                    "Centered moving average, "
                    f"window = {int(moving_average_window)}"
                ),
                "parameters": {
                    "window_size": int(
                        moving_average_window
                    ),
                },
                "r_squared": statistics[
                    "r_squared"
                ],
                "rmse": statistics[
                    "rmse"
                ],
                "mae": statistics[
                    "mae"
                ],
                "point_count": len(
                    clean_x
                ),
            }, None

        else:
            return None, (
                f'Unknown fitting model: "{model_name}".'
            )

        valid_statistics_pairs = [
            (
                actual,
                estimate,
            )
            for actual, estimate
            in zip(
                clean_y,
                predicted_observed,
            )
            if (
                math.isfinite(actual)
                and math.isfinite(
                    estimate
                )
            )
        ]

        observed_for_statistics = [
            pair[0]
            for pair
            in valid_statistics_pairs
        ]

        predicted_for_statistics = [
            pair[1]
            for pair
            in valid_statistics_pairs
        ]

        statistics = calculate_statistics(
            observed_for_statistics,
            predicted_for_statistics,
        )

        if not all(
            math.isfinite(value)
            for value in dense_y
        ):
            return None, (
                "The fitted model produced invalid values."
            )

        return {
            "model": model_name,
            "x_fit": dense_x,
            "y_fit": dense_y,
            "equation": equation,
            "parameters": parameters,
            "r_squared": statistics[
                "r_squared"
            ],
            "rmse": statistics[
                "rmse"
            ],
            "mae": statistics[
                "mae"
            ],
            "point_count": len(
                observed_for_statistics
            ),
        }, None

    except OverflowError:
        return None, (
            "The selected model overflowed numerically. "
            "Try another model or reduce the data range."
        )

    except (
        ArithmeticError,
        TypeError,
        ValueError,
    ) as error:
        return None, (
            "Curve fitting failed. "
            f"Details: {type(error).__name__}: {error}"
        )

    except Exception as error:
        return None, (
            "Unexpected fitting error. "
            f"Details: {type(error).__name__}: {error}"
        )