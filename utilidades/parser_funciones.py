import re
import math

import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


X = sp.Symbol("x", real=True)

# Funciones matemáticas permitidas
FUNCIONES_PERMITIDAS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
}

LOCALES = {
    "x": X,
    "e": sp.E,
    **FUNCIONES_PERMITIDAS,
}

TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application,
)

GLOBALES = {
    "__builtins__": {},
    "Integer": sp.Integer,
    "Float": sp.Float,
    "Rational": sp.Rational,
    "Add": sp.Add,
    "Mul": sp.Mul,
    "Pow": sp.Pow,
    "Symbol": sp.Symbol,
}


def normalizar_expresion(texto: str) -> str:
    """Convierte diferentes notaciones a un formato reconocido por SymPy."""

    texto = texto.strip()

    # Normalizar símbolos
    texto = texto.replace("−", "-")
    texto = texto.replace("×", "*")
    texto = texto.replace("÷", "/")

    # Convertir superíndices
    texto = texto.translate(
        str.maketrans(
            {
                "²": "^2",
                "³": "^3",
                "⁴": "^4",
            }
        )
    )

    # Nombres alternativos de funciones
    texto = re.sub(r"\bsen\b", "sin", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bln\b", "log", texto, flags=re.IGNORECASE)

    # Convertir e^(expresión) en exp(expresión)
    texto = re.sub(
        r"\be\s*\^\s*\(([^()]*)\)",
        r"exp(\1)",
        texto,
        flags=re.IGNORECASE,
    )

    # Convertir e^x en exp(x)
    texto = re.sub(
        r"\be\s*\^\s*([a-zA-Z0-9_.+-]+)",
        r"exp(\1)",
        texto,
        flags=re.IGNORECASE,
    )

    # SymPy utiliza ** para las potencias
    texto = texto.replace("^", "**")

    return texto


def analizar_funcion(texto: str):
    """Analiza y valida la función ingresada por el usuario."""

    if not texto or not texto.strip():
        raise ValueError("Escriba una función antes de continuar.")

    normalizada = normalizar_expresion(texto)

    try:
        expresion = parse_expr(
            normalizada,
            local_dict=LOCALES,
            global_dict=GLOBALES,
            transformations=TRANSFORMACIONES,
            evaluate=True,
        )
    except (SyntaxError, TypeError, ValueError, sp.SympifyError) as exc:
        raise ValueError(
            "La expresión no es válida. Revise los paréntesis, "
            "operadores y funciones permitidas."
        ) from exc

    simbolos_no_permitidos = expresion.free_symbols - {X}

    if simbolos_no_permitidos:
        raise ValueError(
            "La función contiene símbolos no permitidos; "
            "solo se admite la variable x."
        )

    if not expresion.has(X):
        raise ValueError("La expresión debe depender de x.")

    return expresion


def funcion_numerica(expresion):
    """Convierte una expresión de SymPy en una función numérica."""

    evaluador = sp.lambdify(X, expresion, modules=["math"])

    def evaluar(valor):
        try:
            resultado = evaluador(float(valor))

            if isinstance(resultado, complex):
                raise ValueError(
                    "La evaluación produjo un valor complejo."
                )

            resultado = float(resultado)

            if not math.isfinite(resultado):
                raise ValueError(
                    "La evaluación produjo un valor no finito."
                )

            return resultado

        except (
            ValueError,
            TypeError,
            ZeroDivisionError,
            OverflowError,
        ) as exc:
            raise ValueError(
                "La función no puede evaluarse en ese valor real."
            ) from exc

    return evaluar