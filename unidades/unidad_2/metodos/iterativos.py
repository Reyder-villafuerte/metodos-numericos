"""Métodos iterativos para sistemas lineales.

Las funciones de este módulo no dependen de Streamlit y conservan el historial
de iteraciones para que pueda presentarse en una interfaz o exportarse.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .sistemas_lineales import ErrorSistemaLineal, validar_sistema


@dataclass
class ResultadoIterativo:
    metodo: str
    A: np.ndarray
    b: np.ndarray
    x: np.ndarray
    iteraciones: int
    convergio: bool
    error: float
    historial: list[dict[str, Any]]


def _validar_iterativo(A: Any, b: Any, x0: Any | None, tolerancia: float, max_iter: int):
    matriz, vector = validar_sistema(A, b)
    if not np.isfinite(tolerancia) or tolerancia <= 0:
        raise ErrorSistemaLineal("La tolerancia debe ser positiva y finita.")
    if max_iter < 1:
        raise ErrorSistemaLineal("max_iter debe ser un entero positivo.")
    if np.any(np.abs(np.diag(matriz)) <= np.finfo(float).eps):
        raise ErrorSistemaLineal("Jacobi y Gauss-Seidel requieren una diagonal no nula.")
    inicial = np.zeros_like(vector) if x0 is None else np.asarray(x0, dtype=float).reshape(-1)
    if inicial.shape != vector.shape or not np.isfinite(inicial).all():
        raise ErrorSistemaLineal("x0 debe ser un vector finito del tamaño de b.")
    return matriz, vector, inicial


def _resolver(A, b, x0=None, tolerancia=1e-10, max_iter=100, gauss_seidel=False):
    matriz, vector, anterior = _validar_iterativo(A, b, x0, tolerancia, max_iter)
    historial = []
    for k in range(1, int(max_iter) + 1):
        actual = anterior.copy()
        for i in range(len(vector)):
            suma = np.dot(matriz[i, :i], actual[:i] if gauss_seidel else anterior[:i])
            suma += np.dot(matriz[i, i + 1 :], anterior[i + 1 :])
            actual[i] = (vector[i] - suma) / matriz[i, i]
        error = float(np.linalg.norm(actual - anterior, ord=np.inf))
        residuo = float(np.linalg.norm(matriz @ actual - vector, ord=np.inf))
        historial.append({"iteracion": k, "x": actual.copy(), "error": error, "residuo": residuo})
        if error <= tolerancia:
            return ResultadoIterativo(
                "Gauss-Seidel" if gauss_seidel else "Jacobi",
                matriz, vector, actual, k, True, error, historial,
            )
        anterior = actual
    return ResultadoIterativo(
        "Gauss-Seidel" if gauss_seidel else "Jacobi",
        matriz, vector, anterior, int(max_iter), False,
        historial[-1]["error"], historial,
    )


def resolver_jacobi(A, b, x0=None, tolerancia=1e-10, max_iter=100):
    return _resolver(A, b, x0, tolerancia, max_iter, False)


def resolver_gauss_seidel(A, b, x0=None, tolerancia=1e-10, max_iter=100):
    return _resolver(A, b, x0, tolerancia, max_iter, True)


RESOLUTORES_ITERATIVOS = {"Jacobi": resolver_jacobi, "Gauss-Seidel": resolver_gauss_seidel}

jacobi = resolver_jacobi
gauss_seidel = resolver_gauss_seidel
