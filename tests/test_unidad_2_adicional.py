import numpy as np

from unidades.unidad_2.metodos import (
    evaluar_newton,
    regresion_lineal_multiple,
    regresion_polinomial,
    resolver_gauss_seidel,
    resolver_jacobi,
    resolver_newton_raphson,
)


def test_metodos_iterativos_lineales_convergen():
    A = np.array([[10.0, 1.0], [2.0, 8.0]])
    b = np.array([11.0, 10.0])
    referencia = np.linalg.solve(A, b)

    for resolver in (resolver_jacobi, resolver_gauss_seidel):
        resultado = resolver(A, b, tolerancia=1e-10, max_iter=100)
        assert resultado.convergio
        assert np.allclose(resultado.x, referencia, atol=1e-8)


def test_newton_raphson_para_sistemas_converge():
    funciones = [
        lambda x: x[0] ** 2 + x[1] ** 2 - 1,
        lambda x: x[0] - x[1],
    ]
    resultado = resolver_newton_raphson(funciones, [0.7, 0.6], tolerancia=1e-10)

    assert resultado.convergio
    assert np.allclose(resultado.x, [2 ** -0.5, 2 ** -0.5], atol=1e-8)


def test_interpolacion_y_regresiones():
    assert np.isclose(evaluar_newton([0, 1, 2], [1, 3, 7], 1.5), 4.75)

    polinomio = regresion_polinomial([1, 2, 3, 4], [3, 5, 7, 9], 1)
    assert np.allclose(polinomio.coeficientes, [1, 2], atol=1e-10)
    assert np.isclose(polinomio.r2, 1.0)

    multiple = regresion_lineal_multiple(
        [[1, 2], [2, 1], [3, 4], [4, 3]],
        [5, 4, 9, 8],
    )
    assert multiple.coeficientes.shape == (3,)
    assert multiple.rango == 3
