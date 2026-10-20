from fractions import Fraction

import numpy as np

from unidades.unidad_2.metodos import resolver_doolittle
from unidades.unidad_2.presentacion import (
    clasificar_sistema,
    conclusion_resultado,
    dataframe_matriz,
    dataframe_vector,
    filas_comprobacion,
    solucion_racional_verificada,
)


def test_dataframe_matriz_usa_encabezados_academicos():
    tabla = dataframe_matriz([[1, 2], [3, 4]])

    assert list(tabla.columns) == ["x₁", "x₂"]
    assert list(tabla.index) == ["Ecuación 1", "Ecuación 2"]


def test_dataframe_vector_usa_nombres_de_ecuacion():
    tabla = dataframe_vector([5, 6, 7], "b")

    assert list(tabla.columns) == ["b"]
    assert list(tabla.index) == ["Ecuación 1", "Ecuación 2", "Ecuación 3"]


def test_solucion_racional_se_muestra_solo_si_se_verifica_exactamente():
    A = np.array([[2.0, 1.0], [0.0, 3.0]])
    b = np.array([5.0, 6.0])
    x = np.array([1.5, 2.0])

    assert solucion_racional_verificada(A, b, x) == [Fraction(3, 2), Fraction(2, 1)]

    aproximacion_no_exacta = np.array([np.sqrt(2), 2.0])
    assert solucion_racional_verificada(A, b, aproximacion_no_exacta) is None


def test_clasificacion_distingue_los_tres_estados():
    identidad = np.eye(2)
    singular = np.array([[1.0, 2.0], [2.0, 4.0]])

    assert clasificar_sistema(identidad, [1, 2], 1e-12) == "Solución única"
    assert clasificar_sistema(singular, [3, 6], 1e-12) == "Infinitas soluciones"
    assert clasificar_sistema(singular, [3, 7], 1e-12) == "Sin solución"


def test_comprobacion_detalla_cada_ecuacion_y_residuo():
    A = np.array([[2.0, 1.0], [0.0, 3.0]])
    b = np.array([5.0, 6.0])
    x = np.array([1.5, 2.0])

    filas = filas_comprobacion(A, b, x)

    assert len(filas) == 2
    assert "x_{1}" in filas[0]["simbolica"]
    assert "\\left(1.5\\right)" in filas[0]["sustitucion"]
    assert filas[0]["lado_izquierdo"] == 5.0
    assert filas[1]["residuo"] == 0.0


def test_conclusion_no_afirma_cero_absoluto_por_redondeo():
    resultado = resolver_doolittle([[3.0, 1.0], [1.0, 3.0]], [1.0, 2.0])

    conclusion = conclusion_resultado(resultado)

    assert "solución única" in conclusion.lower()
    assert "no se interpreta como cero algebraico absoluto" in conclusion
