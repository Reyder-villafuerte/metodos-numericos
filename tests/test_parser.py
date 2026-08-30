"""Pruebas para el parser de funciones con escritura natural."""
import math
import sympy as sp
from utilidades.parser_funciones import analizar_funcion, normalizar_expresion, X


def test_normalizar_sin_espacios():
    """Convertir sin x en sin(x)."""
    resultado = normalizar_expresion("sin x")
    assert "sin(" in resultado.lower()


def test_normalizar_cos_espacios():
    """Convertir cos x en cos(x)."""
    resultado = normalizar_expresion("cos x")
    assert "cos(" in resultado.lower()


def test_normalizar_ln_basico():
    """Convertir ln x en log(x)."""
    resultado = normalizar_expresion("ln x")
    assert "log(" in resultado


def test_normalizar_ln_parentesis():
    """Convertir ln(x) en log(x)."""
    resultado = normalizar_expresion("ln(x)")
    assert "log(" in resultado


def test_normalizar_pi_simbolo():
    """Convertir π en pi."""
    resultado = normalizar_expresion("π*x")
    assert "pi" in resultado


def test_normalizar_raiz():
    """Convertir √x en sqrt(x)."""
    resultado = normalizar_expresion("√x")
    assert "sqrt" in resultado


def test_normalizar_e_exp():
    """Convertir e^x en exp(x)."""
    resultado = normalizar_expresion("e^x")
    assert "exp(" in resultado


def test_normalizar_e_exp_negativo():
    """Convertir e^-x en exp(-x)."""
    resultado = normalizar_expresion("e^-x")
    assert "exp(" in resultado


def test_analizar_ln_x():
    """Analizar ln(x) correctamente."""
    expresion = analizar_funcion("ln(x)")
    # Debe ser equivalente a log(x)
    x_val = 2.5
    resultado_expr = float(expresion.subs(X, x_val))
    esperado = math.log(x_val)
    assert abs(resultado_expr - esperado) < 1e-10


def test_analizar_sin_x():
    """Analizar sin(x) correctamente."""
    expresion = analizar_funcion("sin(x)")
    x_val = 0.5
    resultado_expr = float(expresion.subs(X, x_val))
    esperado = math.sin(x_val)
    assert abs(resultado_expr - esperado) < 1e-10


def test_analizar_ln_x_natural():
    """Analizar ln x (sin paréntesis) correctamente."""
    expresion = analizar_funcion("ln x")
    x_val = 2.5
    resultado_expr = float(expresion.subs(X, x_val))
    esperado = math.log(x_val)
    assert abs(resultado_expr - esperado) < 1e-10


def test_analizar_sin_x_natural():
    """Analizar sin x (sin paréntesis) correctamente."""
    expresion = analizar_funcion("sin x")
    x_val = 0.5
    resultado_expr = float(expresion.subs(X, x_val))
    esperado = math.sin(x_val)
    assert abs(resultado_expr - esperado) < 1e-10


def test_analizar_expresion_compleja():
    """Analizar: ln(x)+2*x-4."""
    expresion = analizar_funcion("ln(x)+2*x-4")
    x_val = 2.0
    resultado = float(expresion.subs(X, x_val))
    esperado = math.log(2.0) + 2*2.0 - 4
    assert abs(resultado - esperado) < 1e-10


def test_analizar_expresion_natural():
    """Analizar: ln x + 2x - 4 (con escritura natural)."""
    expresion = analizar_funcion("ln x + 2x - 4")
    x_val = 2.0
    resultado = float(expresion.subs(X, x_val))
    esperado = math.log(2.0) + 2*2.0 - 4
    assert abs(resultado - esperado) < 1e-10


def test_analizar_sin_suma():
    """Analizar: sin(x)+x-1."""
    expresion = analizar_funcion("sin(x)+x-1")
    x_val = 0.5
    resultado = float(expresion.subs(X, x_val))
    esperado = math.sin(0.5) + 0.5 - 1
    assert abs(resultado - esperado) < 1e-10


def test_analizar_arcsin():
    """Analizar arcsin(x)."""
    expresion = analizar_funcion("arcsin(x)")
    x_val = 0.5
    resultado = float(expresion.subs(X, x_val))
    esperado = math.asin(0.5)
    assert abs(resultado - esperado) < 1e-10


def test_analizar_exp():
    """Analizar exp(-2*x)."""
    expresion = analizar_funcion("exp(-2*x)")
    x_val = 1.0
    resultado = float(expresion.subs(X, x_val))
    esperado = math.exp(-2.0)
    assert abs(resultado - esperado) < 1e-10


def test_analizar_e_exp_natural():
    """Analizar e^(-2*x)."""
    expresion = analizar_funcion("e^(-2*x)")
    x_val = 1.0
    resultado = float(expresion.subs(X, x_val))
    esperado = math.exp(-2.0)
    assert abs(resultado - esperado) < 1e-10


def test_analizar_sqrt():
    """Analizar sqrt(x)."""
    expresion = analizar_funcion("sqrt(x)")
    x_val = 4.0
    resultado = float(expresion.subs(X, x_val))
    esperado = math.sqrt(4.0)
    assert abs(resultado - esperado) < 1e-10


def test_analizar_potencia():
    """Analizar x^2."""
    expresion = analizar_funcion("x^2")
    x_val = 3.0
    resultado = float(expresion.subs(X, x_val))
    esperado = 9.0
    assert abs(resultado - esperado) < 1e-10


def test_normalizar_superindice():
    """Convertir x² en x^2."""
    resultado = normalizar_expresion("x²")
    assert "^2" in resultado or "**2" in resultado


def test_ejemplo_5_coseno():
    """Ejemplo 5: cos(x) - x."""
    expresion = analizar_funcion("cos(x)-x")
    x_val = 0.73908513
    resultado = float(expresion.subs(X, x_val))
    assert abs(resultado) < 0.001  # Debe estar cercano a 0 (es una raíz)


def test_ejemplo_1_completo():
    """Ejemplo: 1-x^2-arctan(x)."""
    expresion = analizar_funcion("1-x^2-arctan(x)")
    # Verificar que se puede evaluar
    x_val = 0.5
    resultado = float(expresion.subs(X, x_val))
    esperado = 1 - 0.5**2 - math.atan(0.5)
    assert abs(resultado - esperado) < 1e-10


def test_ejemplo_2_completo():
    """Ejemplo: asin(x)-exp(-2*x)."""
    expresion = analizar_funcion("asin(x)-exp(-2*x)")
    x_val = 0.5
    resultado = float(expresion.subs(X, x_val))
    esperado = math.asin(0.5) - math.exp(-2*0.5)
    assert abs(resultado - esperado) < 1e-10
