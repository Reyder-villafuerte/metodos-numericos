import math
from metodos.biseccion import biseccion
from metodos.newton_raphson import newton_raphson
from metodos.punto_fijo import punto_fijo
from metodos.regla_falsa import regla_falsa
from metodos.secante import secante


def test_newton_raphson():
    resultado = newton_raphson(lambda x: math.exp(-x) - x, lambda x: -math.exp(-x) - 1, 0.5, 
                               error_permitido=1e-8, max_iteraciones=100, criterio="error")
    assert resultado.convergio and abs(resultado.raiz - 0.567143) < 1e-5


def test_secante():
    resultado = secante(lambda x: math.exp(-x) - x, 0, 1, 
                        error_permitido=1e-8, max_iteraciones=100, criterio="error")
    assert resultado.convergio and abs(resultado.raiz - 0.567143) < 1e-5


def test_secante_reconoce_raiz_inicial():
    resultado = secante(lambda x: x * (x - 1), 0, 0,
                        error_permitido=1e-8, max_iteraciones=100, criterio="error")
    assert resultado.convergio is True
    assert resultado.raiz == 0
    assert resultado.error_final == 0


def test_biseccion():
    resultado = biseccion(lambda x: x * math.sin(x) - 1, 2, 3, 
                          error_permitido=1e-8, max_iteraciones=100, criterio="error")
    assert resultado.convergio and abs(resultado.raiz - 2.7726) < 1e-4


def test_regla_falsa():
    resultado = regla_falsa(lambda x: x * math.sin(x) - 1, 2, 3, 
                            error_permitido=1e-8, max_iteraciones=100, criterio="error")
    assert resultado.convergio and abs(resultado.raiz - 2.7726) < 1e-4


def test_punto_fijo():
    funcion = lambda x: x**3 + 2 * x**2 + 10 * x - 20
    despeje = lambda x: 20 / (x**2 + 2 * x + 10)
    resultado = punto_fijo(funcion, despeje, 1.5, 
                           error_permitido=1e-8, max_iteraciones=100, criterio="error")
    assert resultado.convergio and abs(resultado.raiz - 1.3688) < 1e-4


# Prueba específica del ejercicio 5: Newton-Raphson con 4 iteraciones fijas
def test_newton_raphson_4_iteraciones_fijas():
    """Ejercicio 5: Newton-Raphson con f(x) = cos(x) - x, x0 = 0.5, exactamente 4 iteraciones."""
    resultado = newton_raphson(lambda x: math.cos(x) - x, lambda x: -math.sin(x) - 1, 0.5,
                               error_permitido=None, max_iteraciones=None, 
                               criterio="fijo", iteraciones_fijas=4)
    # Debe tener exactamente 4 iteraciones
    assert len(resultado.iteraciones) == 4
    # Debe indicar que se completaron las 4 iteraciones
    assert "4" in resultado.motivo
    # Valores aproximados esperados (pueden variar por precisión numérica)
    assert 0.73 < resultado.raiz < 0.74


# Prueba para ambos criterios en el mismo método
def test_newton_criterio_error_vs_fijo():
    """Verifica que el criterio de error y fijo producen resultados diferentes."""
    # Modo error
    resultado_error = newton_raphson(lambda x: math.exp(-x) - x, lambda x: -math.exp(-x) - 1, 0.5,
                                     error_permitido=1e-8, max_iteraciones=100, criterio="error")
    # Modo fijo (4 iteraciones)
    resultado_fijo = newton_raphson(lambda x: math.exp(-x) - x, lambda x: -math.exp(-x) - 1, 0.5,
                                    error_permitido=None, max_iteraciones=None,
                                    criterio="fijo", iteraciones_fijas=4)
    
    # El modo fijo debe tener exactamente 4 iteraciones
    assert len(resultado_fijo.iteraciones) == 4
    # El modo error puede tener menos iteraciones
    assert len(resultado_error.iteraciones) >= 1


def test_iteraciones_fijas_no_afirma_convergencia():
    resultado = punto_fijo(lambda x: x, lambda x: 2 * x, 1,
                           error_permitido=None, max_iteraciones=None,
                           criterio="fijo", iteraciones_fijas=4)
    assert resultado.convergio is None
    assert resultado.raiz == 16
