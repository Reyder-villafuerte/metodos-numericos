"""Solución de sistemas no lineales mediante iteraciones y Newton."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


class ErrorSistemaNoLineal(ValueError):
    """Entrada inválida o paso numéricamente imposible."""


@dataclass
class ResultadoSistemaNoLineal:
    metodo: str
    x: np.ndarray
    iteraciones: int
    convergio: bool
    error: float
    residuo: float
    historial: list[dict]


def _vectorizar(funciones: Sequence[Callable], x):
    try:
        y = np.asarray([f(x) for f in funciones], dtype=float)
    except Exception as exc:
        raise ErrorSistemaNoLineal("No se pudieron evaluar las funciones.") from exc
    if y.shape != (len(funciones),) or not np.isfinite(y).all():
        raise ErrorSistemaNoLineal("Las funciones deben devolver valores finitos.")
    return y


def _validar(funciones, x0, tolerancia, max_iter):
    if not funciones or not all(callable(f) for f in funciones):
        raise ErrorSistemaNoLineal("Se requiere una función callable por ecuación.")
    x = np.asarray(x0, dtype=float).reshape(-1)
    if len(funciones) != len(x) or not np.isfinite(x).all():
        raise ErrorSistemaNoLineal("x0 debe tener una entrada por ecuación.")
    if tolerancia <= 0 or not np.isfinite(tolerancia) or max_iter < 1:
        raise ErrorSistemaNoLineal("tolerancia y max_iter deben ser positivos.")
    return x


def _iterar_mapa(maps, x0, metodo, tolerancia, max_iter, gauss_seidel):
    x = _validar(maps, x0, tolerancia, max_iter)
    historial = []
    for k in range(1, max_iter + 1):
        nuevo = x.copy()
        for i, mapa in enumerate(maps):
            valor = mapa(nuevo if gauss_seidel else x)
            if not np.isfinite(valor):
                raise ErrorSistemaNoLineal("Una iteración produjo un valor no finito.")
            nuevo[i] = float(valor)
        error = float(np.linalg.norm(nuevo - x, ord=np.inf))
        historial.append({"iteracion": k, "x": nuevo.copy(), "error": error})
        if error <= tolerancia:
            return ResultadoSistemaNoLineal(metodo, nuevo, k, True, error, error, historial)
        x = nuevo
    return ResultadoSistemaNoLineal(metodo, x, max_iter, False, historial[-1]["error"],
                                    historial[-1]["error"], historial)


def resolver_jacobi(funciones, x0, tolerancia=1e-10, max_iter=100):
    """Resuelve una forma de punto fijo x_i = g_i(x) simultáneamente."""
    return _iterar_mapa(funciones, x0, "Jacobi no lineal", tolerancia, max_iter, False)


def resolver_gauss_seidel(funciones, x0, tolerancia=1e-10, max_iter=100):
    """Resuelve una forma de punto fijo actualizando x_i inmediatamente."""
    return _iterar_mapa(funciones, x0, "Gauss-Seidel no lineal", tolerancia, max_iter, True)


def _jacobiano_numerico(funciones, x, paso=1e-6):
    base = _vectorizar(funciones, x)
    J = np.empty((len(x), len(x)))
    for j in range(len(x)):
        delta = paso * max(1.0, abs(x[j]))
        xp = x.copy(); xm = x.copy()
        xp[j] += delta; xm[j] -= delta
        J[:, j] = (_vectorizar(funciones, xp) - _vectorizar(funciones, xm)) / (2 * delta)
    return J, base


def resolver_newton_raphson(funciones, x0, jacobiano=None, tolerancia=1e-10,
                            max_iter=50, paso_derivada=1e-6):
    """Resuelve F(x)=0 con Jacobiano analítico o diferencias centradas."""
    x = _validar(funciones, x0, tolerancia, max_iter)
    historial = []
    for k in range(1, max_iter + 1):
        J, F = (np.asarray(jacobiano(x), dtype=float), _vectorizar(funciones, x)) if jacobiano else _jacobiano_numerico(funciones, x, paso_derivada)
        if J.shape != (len(x), len(x)) or not np.isfinite(J).all():
            raise ErrorSistemaNoLineal("El Jacobiano debe ser cuadrado y finito.")
        try:
            delta = np.linalg.solve(J, -F)
        except np.linalg.LinAlgError as exc:
            raise ErrorSistemaNoLineal("El Jacobiano es singular en la iteración actual.") from exc
        nuevo = x + delta
        error = float(np.linalg.norm(delta, ord=np.inf))
        residuo = float(np.linalg.norm(_vectorizar(funciones, nuevo), ord=np.inf))
        historial.append({"iteracion": k, "x": nuevo.copy(), "error": error, "residuo": residuo})
        if max(error, residuo) <= tolerancia:
            return ResultadoSistemaNoLineal("Newton-Raphson", nuevo, k, True, error, residuo, historial)
        x = nuevo
    return ResultadoSistemaNoLineal("Newton-Raphson", x, max_iter, False,
                                    historial[-1]["error"], historial[-1]["residuo"], historial)


jacobi_nolineal = resolver_jacobi
gauss_seidel_nolineal = resolver_gauss_seidel
newton_raphson_sistema = resolver_newton_raphson
