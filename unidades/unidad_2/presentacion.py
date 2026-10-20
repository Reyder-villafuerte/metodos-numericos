"""Preparación de resultados académicos para sistemas lineales.

Este módulo no resuelve nuevamente el sistema. Solo transforma el resultado
canónico del método seleccionado en etiquetas, tablas y comprobaciones.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

import numpy as np
import pandas as pd


_SUBINDICES = str.maketrans("0123456789-", "₀₁₂₃₄₅₆₇₈₉₋")


def subindice(numero: int) -> str:
    return str(numero).translate(_SUBINDICES)


def etiqueta_variable(indice: int) -> str:
    return f"x{subindice(indice)}"


def etiquetas_variables(n: int) -> list[str]:
    return [etiqueta_variable(i) for i in range(1, n + 1)]


def etiquetas_ecuaciones(n: int) -> list[str]:
    return [f"Ecuación {i}" for i in range(1, n + 1)]


def dataframe_matriz(
    matriz: Any,
    *,
    columnas_variables: bool = True,
    filas_ecuaciones: bool = True,
) -> pd.DataFrame:
    datos = np.asarray(matriz, dtype=float)
    if datos.ndim != 2:
        raise ValueError("Se esperaba una matriz bidimensional.")
    filas, columnas = datos.shape
    nombres_columnas = (
        etiquetas_variables(columnas)
        if columnas_variables
        else [f"Columna {i}" for i in range(1, columnas + 1)]
    )
    nombres_filas = (
        etiquetas_ecuaciones(filas)
        if filas_ecuaciones
        else [f"Fila {i}" for i in range(1, filas + 1)]
    )
    return pd.DataFrame(datos, index=nombres_filas, columns=nombres_columnas)


def dataframe_vector(vector: Any, nombre: str) -> pd.DataFrame:
    datos = np.asarray(vector, dtype=float).reshape(-1)
    return pd.DataFrame({nombre: datos}, index=etiquetas_ecuaciones(len(datos)))


def clasificar_sistema(A: Any, b: Any, tolerancia: float) -> str:
    matriz = np.asarray(A, dtype=float)
    vector = np.asarray(b, dtype=float).reshape(-1)
    rango_a = int(np.linalg.matrix_rank(matriz, tol=tolerancia))
    rango_ampliada = int(
        np.linalg.matrix_rank(np.column_stack((matriz, vector)), tol=tolerancia)
    )
    n = matriz.shape[1]
    if rango_a < rango_ampliada:
        return "Sin solución"
    if rango_a < n:
        return "Infinitas soluciones"
    return "Solución única"


def solucion_racional_verificada(
    A: Any,
    b: Any,
    x: Any,
    *,
    maximo_denominador: int = 1_000_000,
) -> list[Fraction] | None:
    """Reconoce una forma racional solo si satisface exactamente el sistema.

    Los coeficientes se interpretan como los números decimales ingresados. Las
    fracciones candidatas se obtienen de la solución del método y se aceptan
    únicamente si la igualdad racional ``Ax=b`` se cumple fila por fila.
    """

    matriz = np.asarray(A, dtype=float)
    vector = np.asarray(b, dtype=float).reshape(-1)
    solucion = np.asarray(x, dtype=float).reshape(-1)
    if not (
        np.isfinite(matriz).all()
        and np.isfinite(vector).all()
        and np.isfinite(solucion).all()
    ):
        return None

    matriz_exacta = [
        [Fraction(str(float(valor))) for valor in fila] for fila in matriz
    ]
    vector_exacto = [Fraction(str(float(valor))) for valor in vector]
    candidatos = [
        Fraction(float(valor)).limit_denominator(maximo_denominador)
        for valor in solucion
    ]

    if not np.allclose(
        np.asarray([float(valor) for valor in candidatos]),
        solucion,
        rtol=1e-10,
        atol=1e-12,
    ):
        return None

    for fila, termino in zip(matriz_exacta, vector_exacto):
        if sum(coeficiente * valor for coeficiente, valor in zip(fila, candidatos)) != termino:
            return None
    return candidatos


def texto_fraccion(valor: Fraction) -> str:
    if valor.denominator == 1:
        return str(valor.numerator)
    return f"{valor.numerator}/{valor.denominator}"


def latex_fraccion(valor: Fraction) -> str:
    if valor.denominator == 1:
        return str(valor.numerator)
    return rf"\frac{{{valor.numerator}}}{{{valor.denominator}}}"


def _numero_latex(valor: float, cifras: int = 12) -> str:
    if abs(valor) < 10 ** (-(cifras + 1)):
        valor = 0.0
    return f"{valor:.{cifras}g}"


def ecuacion_latex(coeficientes: Any, termino: float, cifras: int = 10) -> str:
    piezas: list[str] = []
    for indice, coeficiente in enumerate(np.asarray(coeficientes, dtype=float), start=1):
        if coeficiente == 0:
            continue
        magnitud = _numero_latex(abs(float(coeficiente)), cifras)
        termino_variable = rf"{magnitud}x_{{{indice}}}"
        if not piezas:
            piezas.append(("-" if coeficiente < 0 else "") + termino_variable)
        else:
            piezas.append((" - " if coeficiente < 0 else " + ") + termino_variable)
    lado_izquierdo = "".join(piezas) if piezas else "0"
    return rf"{lado_izquierdo}={_numero_latex(float(termino), cifras)}"


def sustitucion_latex(
    coeficientes: Any,
    solucion: Any,
    termino: float,
    cifras: int = 12,
) -> str:
    piezas: list[str] = []
    for coeficiente, valor in zip(
        np.asarray(coeficientes, dtype=float), np.asarray(solucion, dtype=float)
    ):
        if coeficiente == 0:
            continue
        magnitud = _numero_latex(abs(float(coeficiente)), cifras)
        factor = rf"{magnitud}\left({_numero_latex(float(valor), cifras)}\right)"
        if not piezas:
            piezas.append(("-" if coeficiente < 0 else "") + factor)
        else:
            piezas.append((" - " if coeficiente < 0 else " + ") + factor)
    lado_izquierdo = "".join(piezas) if piezas else "0"
    return rf"{lado_izquierdo}={_numero_latex(float(termino), cifras)}"


def filas_comprobacion(A: Any, b: Any, x: Any) -> list[dict[str, Any]]:
    matriz = np.asarray(A, dtype=float)
    vector = np.asarray(b, dtype=float).reshape(-1)
    solucion = np.asarray(x, dtype=float).reshape(-1)
    calculados = matriz @ solucion
    filas: list[dict[str, Any]] = []
    for indice, (coeficientes, esperado, calculado) in enumerate(
        zip(matriz, vector, calculados), start=1
    ):
        filas.append(
            {
                "ecuacion": indice,
                "simbolica": ecuacion_latex(coeficientes, esperado),
                "sustitucion": sustitucion_latex(coeficientes, solucion, calculado),
                "lado_izquierdo": float(calculado),
                "lado_derecho": float(esperado),
                "residuo": float(calculado - esperado),
            }
        )
    return filas


def conclusion_resultado(resultado: Any) -> str:
    umbral = max(resultado.tolerancia * 10, 1e-14)
    if resultado.norma_residuo <= umbral:
        comprobacion = (
            "El residuo es numéricamente compatible con cero dentro de la "
            "tolerancia empleada; no se interpreta como cero algebraico absoluto."
        )
    else:
        comprobacion = (
            "El residuo supera la tolerancia de referencia y conviene revisar el "
            "condicionamiento del sistema."
        )
    return (
        f"La matriz A es invertible y el método {resultado.metodo} produjo una "
        f"solución única. {comprobacion}"
    )


__all__ = [
    "clasificar_sistema",
    "conclusion_resultado",
    "dataframe_matriz",
    "dataframe_vector",
    "ecuacion_latex",
    "etiqueta_variable",
    "etiquetas_ecuaciones",
    "etiquetas_variables",
    "filas_comprobacion",
    "latex_fraccion",
    "solucion_racional_verificada",
    "subindice",
    "sustitucion_latex",
    "texto_fraccion",
]
