"""Regresión por mínimos cuadrados polinomial y lineal múltiple."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class ResultadoRegresion:
    coeficientes: np.ndarray
    predicciones: np.ndarray
    residuos: np.ndarray
    r2: float
    error_cuadratico: float
    rango: int


def _resultado(X, y, grado=None):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).reshape(-1)
    if X.ndim != 2 or y.ndim != 1 or X.shape[0] != len(y) or not np.isfinite(X).all() or not np.isfinite(y).all():
        raise ValueError("Los datos deben ser matrices/vectores finitos y compatibles.")
    if X.shape[0] < X.shape[1]:
        raise ValueError("Se requieren al menos tantas observaciones como parámetros.")
    coef, _, rango, _ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    residuos = y - pred
    total = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 if total == 0 and np.linalg.norm(residuos) == 0 else 1 - float(residuos @ residuos) / total if total else 0.0
    return ResultadoRegresion(coef, pred, residuos, r2, float(residuos @ residuos), int(rango))


def regresion_polinomial(x, y, grado):
    x = np.asarray(x, dtype=float).reshape(-1)
    if int(grado) < 0 or int(grado) >= len(x):
        raise ValueError("El grado debe ser no negativo y menor que el número de datos.")
    X = np.vander(x, int(grado) + 1, increasing=True)
    return _resultado(X, y)


def regresion_lineal_multiple(X, y):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError("X debe ser una matriz de predictores.")
    return _resultado(np.column_stack((np.ones(X.shape[0]), X)), y)


minimos_cuadrados_polinomial = regresion_polinomial
minimos_cuadrados_multiple = regresion_lineal_multiple
