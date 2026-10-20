import numpy as np
import pytest

from unidades.unidad_2.explicaciones import generar_explicacion
from unidades.unidad_2.metodos import (
    ErrorSistemaLineal,
    MatrizSingularError,
    determinante_eliminacion,
    resolver_sistema,
    validar_sistema,
)


METODOS = ["Matriz inversa", "Regla de Cramer", "Doolittle", "Crout"]

SISTEMAS = [
    (
        np.array([[4.0, 7.0], [2.0, 6.0]]),
        np.array([1.0, 0.0]),
    ),
    (
        np.array([[0.0, 2.0, 1.0], [1.0, -2.0, -3.0], [2.0, 3.0, 1.0]]),
        np.array([3.0, -4.0, 7.0]),
    ),
    (
        np.array(
            [
                [10.0, 2.0, -1.0, 1.0],
                [1.0, 8.0, 2.0, -2.0],
                [-1.0, 1.0, 7.0, 1.0],
                [2.0, -1.0, 1.0, 9.0],
            ]
        ),
        np.array([12.0, 17.0, 5.0, 20.0]),
    ),
]


@pytest.mark.parametrize("metodo", METODOS)
@pytest.mark.parametrize("A,b", SISTEMAS)
def test_metodos_resuelven_sistemas_2x2_3x3_y_4x4(metodo, A, b):
    resultado = resolver_sistema(metodo, A, b)
    referencia = np.linalg.solve(A, b)

    assert np.allclose(resultado.x, referencia, rtol=1e-9, atol=1e-10)
    assert np.allclose(resultado.comprobacion, b, rtol=1e-9, atol=1e-10)
    assert resultado.norma_residuo < 1e-9


@pytest.mark.parametrize("metodo", ["Doolittle", "Crout"])
def test_lu_con_pivoteo_registra_pa_igual_lu(metodo):
    A = np.array([[0.0, 2.0, 1.0], [1.0, -2.0, -3.0], [2.0, 3.0, 1.0]])
    b = np.array([3.0, -4.0, 7.0])

    resultado = resolver_sistema(metodo, A, b)

    assert resultado.hubo_pivoteo
    assert np.allclose(resultado.P @ A, resultado.L @ resultado.U)
    assert any(paso["intercambio"] for paso in resultado.pasos)
    if metodo == "Doolittle":
        assert np.allclose(np.diag(resultado.L), 1.0)
        assert all("calculos_L" in paso for paso in resultado.pasos)
    else:
        assert np.allclose(np.diag(resultado.U), 1.0)
        assert all("calculos_U" in paso for paso in resultado.pasos)


def test_matriz_inversa_se_construye_columna_por_columna():
    A = np.array([[4.0, 7.0], [2.0, 6.0]])
    b = np.array([1.0, 0.0])

    resultado = resolver_sistema("Matriz inversa", A, b)

    assert len(resultado.columnas_inversa) == 2
    assert np.allclose(A @ resultado.inversa, np.eye(2))
    assert all(columna["pasos_y"] and columna["pasos_z"] for columna in resultado.columnas_inversa)


def test_cramer_construye_todas_las_matrices_y_determinantes():
    A, b = SISTEMAS[1]

    resultado = resolver_sistema("Regla de Cramer", A, b)

    assert len(resultado.matrices_cramer) == 3
    assert len(resultado.determinantes_cramer) == 3
    for indice, Ai in enumerate(resultado.matrices_cramer):
        assert np.allclose(Ai[:, indice], b)
        assert np.isclose(resultado.x[indice], resultado.determinantes_cramer[indice] / resultado.determinante)


def test_determinante_usa_eliminacion_y_registra_operaciones():
    A = np.array([[0.0, 2.0, 1.0], [1.0, -2.0, -3.0], [2.0, 3.0, 1.0]])

    determinante, pasos = determinante_eliminacion(A)

    assert np.isclose(determinante, np.linalg.det(A))
    assert len(pasos) == 3
    assert pasos[0]["intercambio"] is not None
    assert all("matriz_triangular" in paso for paso in pasos)


@pytest.mark.parametrize("metodo", METODOS)
def test_matriz_singular_consistente_no_ofrece_solucion_unica(metodo):
    A = np.array([[1.0, 2.0], [2.0, 4.0]])
    b = np.array([3.0, 6.0])

    with pytest.raises(MatrizSingularError, match="no tiene una solución única"):
        resolver_sistema(metodo, A, b)


@pytest.mark.parametrize("metodo", METODOS)
def test_sistema_incompatible_se_identifica(metodo):
    A = np.array([[1.0, 2.0], [2.0, 4.0]])
    b = np.array([3.0, 7.0])

    with pytest.raises(MatrizSingularError, match="incompatible"):
        resolver_sistema(metodo, A, b)


@pytest.mark.parametrize(
    "A,b,mensaje",
    [
        ([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], [1.0, 2.0], "cuadrada"),
        ([[1.0, 0.0], [0.0, 1.0]], [1.0], "exactamente 2"),
        ([[1.0, "dato"], [0.0, 1.0]], [1.0, 2.0], "numéricos"),
        ([[1.0, np.inf], [0.0, 1.0]], [1.0, 2.0], "finitos"),
    ],
)
def test_validaciones_de_dimensiones_y_datos(A, b, mensaje):
    with pytest.raises(ErrorSistemaLineal, match=mensaje):
        validar_sistema(A, b)


def test_cramer_no_confunde_determinante_pequeno_con_matriz_singular():
    A = np.diag([1e-6, 1e-6])
    b = np.array([1e-6, 2e-6])

    resultado = resolver_sistema("Regla de Cramer", A, b)

    assert np.allclose(resultado.x, [1.0, 2.0])
    assert np.isclose(resultado.determinante, 1e-12)


@pytest.mark.parametrize("metodo", METODOS)
def test_tolerancia_explicita_detecta_pivote_demasiado_pequeno(metodo):
    A = np.diag([1e-8, 1.0])
    b = np.array([1.0, 1.0])

    with pytest.raises(MatrizSingularError):
        resolver_sistema(metodo, A, b, tolerancia=1e-6)


@pytest.mark.parametrize("metodo", METODOS)
def test_explicacion_incluye_operaciones_resultado_y_verificacion(metodo):
    A, b = SISTEMAS[1]
    resultado = resolver_sistema(metodo, A, b)

    secciones = generar_explicacion(resultado)
    titulos = " ".join(seccion.titulo for seccion in secciones)
    formulas = " ".join(formula for seccion in secciones for formula in seccion.formulas)

    assert "Resultado" in titulos
    assert "Verificación" in titulos
    assert "Ax-b" in formulas
    if metodo == "Matriz inversa":
        assert "Columna 1 de la inversa" in titulos
        assert "P e_{1}" in formulas
    elif metodo == "Regla de Cramer":
        assert "A_{1}" in formulas
        assert "det(A_{1})" in formulas
    else:
        assert "Sustitución progresiva" in titulos
        assert "Sustitución regresiva" in titulos
        assert "\\frac" in formulas
