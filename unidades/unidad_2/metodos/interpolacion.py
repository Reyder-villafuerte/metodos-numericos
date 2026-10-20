"""Interpolación polinómica de Newton mediante diferencias divididas."""
from __future__ import annotations

import numpy as np


def _datos(x, y):
    x = np.asarray(x, dtype=float).reshape(-1)
    y = np.asarray(y, dtype=float).reshape(-1)
    if len(x) == 0 or len(x) != len(y) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("x e y deben ser vectores finitos de igual longitud no vacía.")
    if len(np.unique(x)) != len(x):
        raise ValueError("Los nodos x deben ser distintos.")
    return x, y


def diferencias_divididas(x, y):
    x, y = _datos(x, y)
    tabla = np.zeros((len(x), len(x)), dtype=float)
    tabla[:, 0] = y
    for j in range(1, len(x)):
        tabla[j:, j] = (tabla[j:, j - 1] - tabla[j - 1:-1, j - 1]) / (x[j:] - x[:len(x) - j])
    return tabla


def coeficientes_newton(x, y):
    return np.diag(diferencias_divididas(x, y))


def evaluar_newton(x, y, valores):
    nodos, _ = _datos(x, y)
    coef = coeficientes_newton(nodos, y)
    valores = np.asarray(valores, dtype=float)
    resultado = np.zeros_like(valores, dtype=float) + coef[-1]
    for i in range(len(coef) - 2, -1, -1):
        resultado = resultado * (valores - nodos[i]) + coef[i]
    return resultado.item() if resultado.ndim == 0 else resultado


def interpolacion_newton(x, y):
    """Devuelve una función evaluable y sus coeficientes de Newton."""
    coef = coeficientes_newton(x, y)
    return lambda valores: evaluar_newton(x, y, valores), coef
