import re
import math
import cmath
import logging
import threading

import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


LOGGER = logging.getLogger("metodos_numericos.parser")

X = sp.Symbol("x", real=True)

# Límites de seguridad para evitar que expresiones patológicas
# (por ejemplo, torres de potencias numéricas) bloquen la aplicación.
_LIMITE_CARACTERES = 400
_MAX_OPERADORES_POTENCIA = 8
_LIMITE_DIGITOS_EXPONENTE = 6
_SEGUNDOS_MAXIMOS_PARSEO = 3.0

# Funciones matemáticas permitidas
FUNCIONES_PERMITIDAS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "exp": sp.exp,
    "log": sp.log,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
}

LOCALES = {
    "x": X,
    "e": sp.E,
    "pi": sp.pi,
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
    "Number": sp.Number,
}


def normalizar_expresion(texto: str) -> str:
    """Convierte diferentes notaciones a un formato reconocido por SymPy."""

    texto = texto.strip()

    # Normalizar símbolos especiales
    texto = texto.replace("−", "-")
    texto = texto.replace("×", "*")
    texto = texto.replace("÷", "/")
    texto = texto.replace("π", "pi")
    texto = texto.replace("√", "sqrt")
    
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

    # Normalizar espacios múltiples
    texto = re.sub(r"\s+", " ", texto).strip()
    
    # Nombres alternativos de funciones
    texto = re.sub(r"\bsen\b", "sin", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\barcsen\b", "asin", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\barcsin\b", "asin", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\barccos\b", "acos", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\barcacos\b", "acos", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\barctan\b", "atan", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\barcatn\b", "atan", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bln\b", "log", texto, flags=re.IGNORECASE)

    # Convertir funciones sin paréntesis de forma más completa
    # Patrón: sin x -> sin(x), cos x -> cos(x), etc.
    # Usar un patrón que captura: función + espacio(s) + argumento
    
    # sin x, cos x, tan x -> sin(x), cos(x), tan(x)
    texto = re.sub(r"\b(sin|cos|tan)\s+([x]|pi|\d+\.?\d*|sqrt)", r"\1(\2)", texto, flags=re.IGNORECASE)
    
    # asin x, acos x, atan x -> asin(x), acos(x), atan(x)
    texto = re.sub(r"\b(asin|acos|atan)\s+([x]|pi|\d+\.?\d*|sqrt)", r"\1(\2)", texto, flags=re.IGNORECASE)
    
    # log x -> log(x)
    texto = re.sub(r"\b(log)\s+([x]|pi|\d+\.?\d*|sqrt)", r"\1(\2)", texto, flags=re.IGNORECASE)
    
    # sqrt x -> sqrt(x)
    texto = re.sub(r"\b(sqrt)\s+([x]|pi|\d+\.?\d*)", r"\1(\2)", texto, flags=re.IGNORECASE)

    # Convertir e^(expresión) en exp(expresión)
    texto = re.sub(
        r"\be\s*\^\s*\(([^()]*)\)",
        r"exp(\1)",
        texto,
        flags=re.IGNORECASE,
    )

    # Convertir e^x, e^-x, e^2x en exp(x), exp(-x), exp(2*x)
    def convertir_exp(match):
        exp_content = match.group(1)
        # Si no tiene paréntesis y empieza con -, agregar paréntesis
        if exp_content.startswith('-') and not exp_content.startswith('(-'):
            # Extraer el contenido después del -
            contenido = exp_content[1:].strip()
            # Si es algo como 2x, convertir a 2*x
            if contenido and contenido[0].isdigit() and len(contenido) > 1 and contenido[1] in 'xyzabcABCXYZ':
                contenido = contenido[0] + '*' + contenido[1:]
            return f"exp(-({contenido}))"
        # Si empieza con dígito seguido de x sin *, agregar *
        if exp_content and exp_content[0].isdigit() and len(exp_content) > 1 and exp_content[1] in 'xyzabcABCXYZ':
            exp_content = exp_content[0] + '*' + exp_content[1:]
        return f"exp({exp_content})"
    
    texto = re.sub(
        r"\be\s*\^\s*(-?[a-zA-Z0-9_.*\-+/()]+)",
        convertir_exp,
        texto,
        flags=re.IGNORECASE,
    )

    # SymPy utiliza ** para las potencias
    texto = texto.replace("^", "**")

    return texto


class _ExpresionDemasiadoCompleja(Exception):
    """Indica que una expresión supera los límites de seguridad del análisis."""


def _guardar_contra_expresiones_explosivas(normalizada):
    """
    Rechaza de inmediato expresiones que podrían generar cálculos numéricos
    explosivos al ser evaluadas por SymPy (por ejemplo, torres de potencias
    como 3^(3^(3^3))), que consumirían tiempo o memoria de forma indefinida.
    """

    if len(normalizada) > _LIMITE_CARACTERES:
        raise _ExpresionDemasiadoCompleja("La expresión es demasiado larga.")

    if normalizada.count("**") > _MAX_OPERADORES_POTENCIA:
        raise _ExpresionDemasiadoCompleja("Demasiados exponentes en la expresión.")

    # Potencia con base numérica y exponente numérico (o paréntesis numérico),
    # por ejemplo 3**3, 3**(3**3) o 2**10. SymPy las evaluaría a constantes
    # enormes que pueden bloquear el cálculo.
    if re.search(r"\d+\s*\*\*\s*\(?\s*\d+", normalizada):
        raise _ExpresionDemasiadoCompleja("Exponentes numéricos demasiado grandes.")

    # Exponentes literales con muchos dígitos (por ejemplo 2**1234567890).
    if re.search(r"(?<=\*\*)-?\d{%d,}" % _LIMITE_DIGITOS_EXPONENTE, normalizada):
        raise _ExpresionDemasiadoCompleja("Exponente numérico demasiado grande.")


def _parsear_con_limite_de_tiempo(normalizada):
    """
    Ejecuta parse_expr en un hilo con un límite de tiempo.
    Si el análisis no termina en el tiempo previsto, se aborta para
    evitar que una entrada maliciosa o demasiado compleja bloqueé
    la aplicación.
    """

    caja = {}

    def trabajo():
        try:
            caja["expresion"] = parse_expr(
                normalizada,
                local_dict=LOCALES,
                global_dict=GLOBALES,
                transformations=TRANSFORMACIONES,
                evaluate=True,
            )
        except Exception as error:
            caja["error"] = error

    hilo = threading.Thread(target=trabajo, daemon=True)
    hilo.start()
    hilo.join(_SEGUNDOS_MAXIMOS_PARSEO)

    if hilo.is_alive():
        raise _ExpresionDemasiadoCompleja("El análisis de la expresión agotó el tiempo.")

    if "error" in caja:
        raise caja["error"]

    return caja["expresion"]


def analizar_funcion(texto: str):
    """
    Analiza y valida la función ingresada por el usuario.

    Cualquier entrada malformada o ininterpretable se convierte en un
    ValueError con un mensaje educativo; nunca se expone el detalle
    técnico del error al usuario.
    """

    if not texto or not texto.strip():
        raise ValueError("Escriba una función antes de continuar.")

    if len(texto) > _LIMITE_CARACTERES:
        raise ValueError(
            "La función es demasiado larga. Revise la expresión e intente de nuevo."
        )

    normalizada = normalizar_expresion(texto)

    try:
        _guardar_contra_expresiones_explosivas(normalizada)
        expresion = _parsear_con_limite_de_tiempo(normalizada)
    except _ExpresionDemasiadoCompleja as exc:
        raise ValueError(
            "La expresión es demasiado compleja y no pudo analizarse. "
            "Simplifíquela, por ejemplo reduciendo los exponentes."
        ) from exc
    except Exception as exc:
        LOGGER.warning(
            "No fue posible interpretar la función %r: %s: %s",
            texto,
            type(exc).__name__,
            exc,
        )
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


def funcion_numerica_compleja(expresion):
    """Convierte una expresión de SymPy en una función apta para valores complejos."""
    funciones = {
        "sin": cmath.sin, "cos": cmath.cos, "tan": cmath.tan,
        "asin": cmath.asin, "acos": cmath.acos, "atan": cmath.atan,
        "exp": cmath.exp, "log": cmath.log, "sqrt": cmath.sqrt,
        "Abs": abs,
    }
    evaluador = sp.lambdify(X, expresion, modules=[funciones])

    def evaluar(valor):
        try:
            resultado = complex(evaluador(complex(valor)))
            if not (math.isfinite(resultado.real) and math.isfinite(resultado.imag)):
                raise ValueError("La evaluación produjo un valor no finito.")
            return resultado
        except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
            raise ValueError("La función no puede evaluarse en ese valor.") from exc

    return evaluar
