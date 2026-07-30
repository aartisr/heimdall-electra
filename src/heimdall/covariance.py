"""Small dependency-free validation for 3×3 covariance matrices."""

from __future__ import annotations

from math import isfinite, sqrt


def validate_covariance_3x3(values: tuple[float, ...], tolerance: float = 1e-12) -> None:
    if len(values) != 9 or not all(isfinite(value) for value in values):
        raise ValueError("covariance must contain nine finite values")
    matrix = (values[0:3], values[3:6], values[6:9])
    if any(matrix[index][index] < -tolerance for index in range(3)):
        raise ValueError("covariance diagonal must be non-negative")
    if any(abs(matrix[row][column] - matrix[column][row]) > tolerance for row in range(3) for column in range(3)):
        raise ValueError("covariance must be symmetric")
    # Cholesky-style PSD test; zero pivots are allowed only with a zero residual row.
    lower = [[0.0] * 3 for _ in range(3)]
    for row in range(3):
        for column in range(row + 1):
            residual = matrix[row][column] - sum(lower[row][k] * lower[column][k] for k in range(column))
            if row == column:
                if residual < -tolerance:
                    raise ValueError("covariance must be positive semidefinite")
                lower[row][column] = sqrt(max(0.0, residual))
            elif lower[column][column] > tolerance:
                lower[row][column] = residual / lower[column][column]
            elif abs(residual) > tolerance:
                raise ValueError("covariance must be positive semidefinite")
