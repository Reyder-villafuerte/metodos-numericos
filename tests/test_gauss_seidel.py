"""Pruebas del método iterativo de Gauss-Seidel (Unidad 2)."""

from fractions import Fraction

import numpy as np
import pytest

from unidades.unidad_2.metodos.gauss_seidel import (
    ErrorGaussSeidel,
    analizar_dominancia,
    buscar_reordenacion,
    descomposicion_ldu,
    matriz_iteracion_gauss_seidel,
    resolver_gauss_seidel_detallado,
)
from unidades.unidad_2.metodos.iterativos import resolver_gauss_seidel, resolver_jacobi


A_EJEMPLO = [[10.0, -1.0, 2.0], [-1.0, 11.0, -1.0], [2.0, -1.0, 10.0]]
B_EJEMPLO = [6.0, 25.0, -11.0]


def _solucion_exacta_fracciones(A, b):
    """Eliminación de Gauss-Jordan con fracciones: referencia independiente."""

    n = len(b)
    M = [[Fraction(str(v)) for v in fila] + [Fraction(str(t))] for fila, t in zip(A, b)]
    for c in range(n):
        p = next(f for f in range(c, n) if M[f][c] != 0)
        M[c], M[p] = M[p], M[c]
        M[c] = [v / M[c][c] for v in M[c]]
        for f in range(n):
            if f != c and M[f][c] != 0:
                factor = M[f][c]
                M[f] = [a - factor * b_ for a, b_ in zip(M[f], M[c])]
    return [fila[-1] for fila in M]


def _gauss_seidel_manual(A, b, x0, iteraciones):
    """Implementación mínima e independiente, solo para comparar."""

    x = list(map(float, x0))
    for _ in range(iteraciones):
        for i in range(len(b)):
            s = sum(A[i][j] * x[j] for j in range(len(b)) if j != i)
            x[i] = (b[i] - s) / A[i][i]
    return np.array(x)


# --- Ejercicio de la exposición -------------------------------------------

def test_ejemplo_exposicion_converge_y_coincide_con_referencia():
    r = resolver_gauss_seidel_detallado(A_EJEMPLO, B_EJEMPLO, [0, 0, 0], 0.001, 50)
    exacta = np.array([float(v) for v in _solucion_exacta_fracciones(A_EJEMPLO, B_EJEMPLO)])

    assert r.convergio
    assert r.iteraciones == 4
    assert r.error <= 0.001
    assert np.allclose(r.x, np.linalg.solve(A_EJEMPLO, B_EJEMPLO), atol=1e-3)
    assert np.allclose(r.x, exacta, atol=1e-3)
    assert r.estrictamente_dominante
    assert r.radio_espectral < 1


def test_primera_iteracion_usa_valores_nuevos_inmediatamente():
    r = resolver_gauss_seidel_detallado(A_EJEMPLO, B_EJEMPLO, [0, 0, 0], 0.001, 50)
    it1 = r.historial_detallado[0]

    # Cálculo a mano: x1 = 6/10; x2 = (25 + x1)/11; x3 = (-11 - 2x1 + x2)/10
    x1 = 6 / 10
    x2 = (25 + x1) / 11
    x3 = (-11 - 2 * x1 + x2) / 10
    assert np.allclose(it1.x, [x1, x2, x3])

    # x2 usa x1^(1) (nuevo) y x3^(0) (anterior)
    terminos_x2 = it1.pasos[1].terminos
    assert [(t.j, t.nuevo) for t in terminos_x2] == [(0, True), (2, False)]
    assert terminos_x2[0].valor == pytest.approx(x1)

    # Jacobi daría x2 = 25/11 en la primera iteración: no se confunden.
    jacobi = resolver_jacobi(A_EJEMPLO, B_EJEMPLO, [0, 0, 0], 1e-3, 1)
    assert jacobi.x[1] == pytest.approx(25 / 11)
    assert it1.x[1] != pytest.approx(jacobi.x[1])


def test_coincide_con_implementacion_independiente_en_cada_iteracion():
    r = resolver_gauss_seidel_detallado(A_EJEMPLO, B_EJEMPLO, [0, 0, 0], 1e-12, 30)
    for it in r.historial_detallado:
        esperado = _gauss_seidel_manual(A_EJEMPLO, B_EJEMPLO, [0, 0, 0], it.k)
        assert np.allclose(it.x, esperado, rtol=0, atol=1e-14)


def test_errores_y_residuos_de_cada_iteracion_son_correctos():
    A = np.array(A_EJEMPLO)
    b = np.array(B_EJEMPLO)
    r = resolver_gauss_seidel_detallado(A, b, [0, 0, 0], 1e-8, 50)
    anterior = r.x0
    for it in r.historial_detallado:
        assert np.array_equal(it.x_anterior, anterior)
        assert it.norma_cambio == pytest.approx(np.max(np.abs(it.x - anterior)))
        assert it.residuo == pytest.approx(np.max(np.abs(A @ it.x - b)))
        assert it.error_relativo == pytest.approx(it.norma_cambio / np.max(np.abs(it.x)))
        for paso in it.pasos:
            assert paso.numerador == pytest.approx(paso.b_i - paso.suma_nuevos - paso.suma_anteriores)
            assert paso.valor == pytest.approx(paso.numerador / paso.a_ii)
        anterior = it.x
    assert r.residuo_inicial == pytest.approx(np.max(np.abs(b)))
    # Solo la última iteración cumple el criterio.
    assert all(it.error > 1e-8 for it in r.historial_detallado[:-1])
    assert r.historial_detallado[-1].error <= 1e-8


# --- Sistemas 2x2 / 3x3 ---------------------------------------------------

@pytest.mark.parametrize(
    "A, b",
    [
        ([[4.0, 1.0], [2.0, 3.0]], [1.0, 2.0]),
        ([[10.0, 1.0], [2.0, 8.0]], [11.0, 10.0]),
        ([[4.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 4.0]], [15.0, 10.0, 10.0]),
    ],
)
@pytest.mark.parametrize("criterio", ["absoluto", "relativo", "residuo"])
def test_sistemas_2x2_y_3x3_convergen_con_cada_criterio(A, b, criterio):
    r = resolver_gauss_seidel_detallado(A, b, None, 1e-10, 200, criterio=criterio)
    assert r.convergio
    assert np.allclose(r.x, np.linalg.solve(A, b), atol=1e-8)
    assert r.norma_residuo == pytest.approx(np.max(np.abs(np.array(A) @ r.x - np.array(b))))


def test_criterio_residuo_detiene_segun_el_residuo():
    r = resolver_gauss_seidel_detallado(A_EJEMPLO, B_EJEMPLO, None, 1e-6, 50, criterio="residuo")
    assert r.convergio
    assert r.historial_detallado[-1].residuo <= 1e-6
    assert all(it.residuo > 1e-6 for it in r.historial_detallado[:-1])


# --- No convergencia ------------------------------------------------------

def test_sistema_que_no_converge_se_informa_sin_presentarlo_como_solucion():
    A = [[1.0, 3.0], [4.0, 1.0]]
    b = [4.0, 5.0]
    r = resolver_gauss_seidel_detallado(A, b, [0, 0], 1e-6, 25, reordenar="nunca")
    assert not r.convergio
    assert r.iteraciones == 25
    assert r.radio_espectral > 1
    assert "iteraciones permitidas" in r.motivo


def test_divergencia_extrema_se_detiene_sin_valores_infinitos():
    A = [[1.0, 10.0], [10.0, 1.0]]
    r = resolver_gauss_seidel_detallado(A, [1.0, 1.0], [1, 1], 1e-6, 1000, reordenar="nunca")
    assert not r.convergio
    assert r.iteraciones < 1000
    assert "diverge" in r.motivo


def test_no_dominante_pero_convergente():
    # Simétrica definida positiva, no estrictamente dominante: Gauss-Seidel converge.
    A = np.array([[1.0, 2.0], [2.0, 5.0]])
    b = np.array([1.0, 1.0])
    _, dominante = analizar_dominancia(A)
    r = resolver_gauss_seidel_detallado(A, b, None, 1e-10, 500, reordenar="nunca")
    assert not dominante
    assert r.convergio
    assert r.radio_espectral < 1


# --- Diagonal cero y reordenación ----------------------------------------

def test_diagonal_cero_sin_reordenar_produce_error_claro():
    with pytest.raises(ErrorGaussSeidel, match="a11"):
        resolver_gauss_seidel_detallado([[0.0, 2.0], [3.0, 1.0]], [2.0, 4.0], reordenar="nunca")


def test_diagonal_cero_se_reordena_y_conserva_la_solucion():
    A = [[0.0, 2.0, 1.0], [5.0, 1.0, 1.0], [1.0, 1.0, 4.0]]
    b = [5.0, 9.0, 10.0]
    r = resolver_gauss_seidel_detallado(A, b, None, 1e-10, 200)
    assert r.hubo_reordenacion
    assert r.permutacion == [1, 0, 2]
    assert np.array_equal(r.A, np.array(A)[r.permutacion])
    assert np.allclose(r.x, np.linalg.solve(A, b), atol=1e-8)


def test_sin_reordenamiento_posible():
    with pytest.raises(ErrorGaussSeidel, match="No existe un reordenamiento"):
        resolver_gauss_seidel_detallado([[0.0, 1.0], [0.0, 2.0]], [1.0, 2.0])


def test_buscar_orden_dominante():
    A = [[1.0, 5.0, 1.0], [6.0, 1.0, 1.0], [1.0, 1.0, 7.0]]
    assert buscar_reordenacion(A) == [1, 0, 2]
    r = resolver_gauss_seidel_detallado(A, [7.0, 8.0, 9.0], None, 1e-8, 100, reordenar="dominante")
    assert r.estrictamente_dominante and r.convergio


# --- Validación de entradas ----------------------------------------------

@pytest.mark.parametrize(
    "A, b, x0, tol, max_iter, mensaje",
    [
        ([[1, 2, 3], [4, 5, 6]], [1, 2], None, 1e-3, 10, "cuadrada"),
        ([[4, 1], [1, 3]], [1, 2, 3], None, 1e-3, 10, "b debe tener 2"),
        ([[4, 1], [1, 3]], [1, 2], [0, 0, 0], 1e-3, 10, "inicial"),
        ([[4, "a"], [1, 3]], [1, 2], None, 1e-3, 10, "numéricos"),
        ([[4, np.nan], [1, 3]], [1, 2], None, 1e-3, 10, "finitos"),
        ([[4, 1], [1, 3]], [1, None], None, 1e-3, 10, "b"),
        ([[4, 1], [1, 3]], [1, 2], None, "abc", 10, "tolerancia"),
        ([[4, 1], [1, 3]], [1, 2], None, -1, 10, "positivo"),
        ([[4, 1], [1, 3]], [1, 2], None, 1e-3, 0, "entero positivo"),
        ([[4, 1], [1, 3]], [1, 2], None, 1e-3, 2.5, "entero positivo"),
        ([[4]], [1], None, 1e-3, 10, "al menos dos"),
    ],
)
def test_entradas_invalidas(A, b, x0, tol, max_iter, mensaje):
    with pytest.raises(ErrorGaussSeidel, match=mensaje):
        resolver_gauss_seidel_detallado(A, b, x0, tol, max_iter)


# --- Análisis matricial ---------------------------------------------------

def test_descomposicion_y_matriz_de_iteracion():
    A = np.array(A_EJEMPLO)
    b = np.array(B_EJEMPLO)
    D, L, U = descomposicion_ldu(A)
    assert np.array_equal(L + D + U, A)
    T, c, valores, radio = matriz_iteracion_gauss_seidel(A, b)
    # Una iteración matricial coincide con una iteración componente a componente.
    r = resolver_gauss_seidel_detallado(A, b, [1, 1, 1], 1e-12, 3)
    x = np.array([1.0, 1.0, 1.0])
    for it in r.historial_detallado:
        x = T @ x + c
        assert np.allclose(it.x, x, atol=1e-13)
    assert radio == pytest.approx(np.max(np.abs(np.linalg.eigvals(T))))


def test_resolvedor_existente_sigue_funcionando():
    r = resolver_gauss_seidel(A_EJEMPLO, B_EJEMPLO, tolerancia=1e-10, max_iter=100)
    assert r.convergio
    detallado = resolver_gauss_seidel_detallado(A_EJEMPLO, B_EJEMPLO, None, 1e-10, 100)
    assert np.allclose(r.x, detallado.x, atol=1e-12)
