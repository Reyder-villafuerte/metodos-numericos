import numpy as np
import plotly.graph_objects as go
import pytest

from unidades.unidad_2.graficas import (
    construir_figuras,
    crear_grafica_sistema_2d,
    crear_grafica_sistema_3d,
    crear_mapa_calor,
)
from unidades.unidad_2.metodos import resolver_sistema


def test_grafica_2d_muestra_dos_rectas_y_punto_solucion():
    A = np.array([[1.0, 1.0], [2.0, -1.0]])
    b = np.array([3.0, 0.0])
    x = np.linalg.solve(A, b)

    figura = crear_grafica_sistema_2d(A, b, x)

    assert len(figura.data) == 3
    assert [traza.name for traza in figura.data] == ["Ecuación 1", "Ecuación 2", "Solución"]
    assert np.isclose(figura.data[-1].x[0], x[0])
    assert np.isclose(figura.data[-1].y[0], x[1])


def test_grafica_2d_maneja_recta_vertical_y_horizontal():
    A = np.array([[1.0, 0.0], [0.0, 1.0]])
    b = np.array([2.0, -3.0])
    x = np.array([2.0, -3.0])

    figura = crear_grafica_sistema_2d(A, b, x)

    assert np.allclose(np.asarray(figura.data[0].x, dtype=float), 2.0)
    assert np.allclose(np.asarray(figura.data[1].y, dtype=float), -3.0)


def test_grafica_3d_parametriza_planos_sin_requerir_z_como_dependiente():
    A = np.array([[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [1.0, 1.0, 1.0]])
    b = np.array([1.0, 4.0, 6.0])
    x = np.array([1.0, 2.0, 3.0])

    figura = crear_grafica_sistema_3d(A, b, x)

    assert len(figura.data) == 4
    assert all(isinstance(traza, go.Surface) for traza in figura.data[:3])
    assert isinstance(figura.data[-1], go.Scatter3d)
    for traza in figura.data[:3]:
        assert np.isfinite(np.asarray(traza.x, dtype=float)).all()
        assert np.isfinite(np.asarray(traza.y, dtype=float)).all()
        assert np.isfinite(np.asarray(traza.z, dtype=float)).all()


@pytest.mark.parametrize("n", range(4, 9))
def test_sistemas_4x4_hasta_8x8_usan_visualizaciones_correctas(n):
    A = np.diag(np.arange(2.0, n + 2.0)) + 0.05 * np.ones((n, n))
    x_esperada = np.arange(1.0, n + 1.0)
    b = A @ x_esperada
    resultado = resolver_sistema("Doolittle", A, b)

    claves = {clave for clave, _, _ in construir_figuras(resultado)}

    assert {"matriz-a", "solucion", "residuos", "lu-l", "lu-u"}.issubset(claves)
    assert "sistema-3d" not in claves


def test_lu_con_pivoteo_agrega_mapa_de_calor_de_p():
    A = np.array([[0.0, 2.0], [1.0, 1.0]])
    b = np.array([4.0, 3.0])
    resultado = resolver_sistema("Doolittle", A, b)

    claves = {clave for clave, _, _ in construir_figuras(resultado)}

    assert resultado.hubo_pivoteo
    assert {"lu-l", "lu-u", "lu-p"}.issubset(claves)


def test_inversa_y_cramer_agregan_sus_mapas_especificos():
    A = np.array([[2.0, 1.0], [1.0, 3.0]])
    b = np.array([4.0, 7.0])

    inversa = resolver_sistema("Matriz inversa", A, b)
    cramer = resolver_sistema("Regla de Cramer", A, b)

    claves_inversa = {clave for clave, _, _ in construir_figuras(inversa)}
    claves_cramer = {clave for clave, _, _ in construir_figuras(cramer)}
    assert "inversa" in claves_inversa
    assert {"cramer-a", "cramer-a-1", "cramer-a-2"}.issubset(claves_cramer)


def test_mapa_calor_conserva_etiquetas_de_variables_y_ecuaciones():
    figura = crear_mapa_calor([[1.0, 2.0], [3.0, 4.0]], "A")

    assert list(figura.data[0].x) == ["x₁", "x₂"]
    assert list(figura.data[0].y) == ["Ecuación 1", "Ecuación 2"]
