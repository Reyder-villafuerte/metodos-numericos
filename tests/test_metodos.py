import math
from metodos.biseccion import biseccion
from metodos.newton_raphson import newton_raphson
from metodos.punto_fijo import punto_fijo
from metodos.regla_falsa import regla_falsa
from metodos.secante import secante


def test_newton_raphson():
    resultado = newton_raphson(lambda x: math.exp(-x) - x, lambda x: -math.exp(-x) - 1, 0.5, 1e-8, 100)
    assert resultado.convergio and abs(resultado.raiz - 0.567143) < 1e-5


def test_secante():
    resultado = secante(lambda x: math.exp(-x) - x, 0, 1, 1e-8, 100)
    assert resultado.convergio and abs(resultado.raiz - 0.567143) < 1e-5


def test_biseccion():
    resultado = biseccion(lambda x: x * math.sin(x) - 1, 2, 3, 1e-8, 100)
    assert resultado.convergio and abs(resultado.raiz - 2.7726) < 1e-4


def test_regla_falsa():
    resultado = regla_falsa(lambda x: x * math.sin(x) - 1, 2, 3, 1e-8, 100)
    assert resultado.convergio and abs(resultado.raiz - 2.7726) < 1e-4


def test_punto_fijo():
    funcion = lambda x: x**3 + 2 * x**2 + 10 * x - 20
    despeje = lambda x: 20 / (x**2 + 2 * x + 10)
    resultado = punto_fijo(funcion, despeje, 1.5, 1e-8, 100)
    assert resultado.convergio and abs(resultado.raiz - 1.3688) < 1e-4
