"""Utilidades numéricas y de formato compartidas por todos los generadores."""

import math
import re

import sympy as sp


TOLERANCIA_COMPLEJA = 1e-14


def _simbolo_x():
    return sp.Symbol("x", real=True)


def _formatear(valor, decimales=6):
    if isinstance(valor, complex):
        if abs(valor.imag) < TOLERANCIA_COMPLEJA:
            return f"{valor.real:.{decimales}f}"
        signo = "+" if valor.imag >= 0 else "-"
        return f"{valor.real:.{decimales}f} {signo} {abs(valor.imag):.{decimales}f}i"
    if isinstance(valor, float):
        if not math.isfinite(valor):
            return "No disponible"
        return f"{valor:.{decimales}f}"
    if isinstance(valor, int):
        return str(valor)
    return str(valor)


def _valor_display(valor, decimales=6):
    if isinstance(valor, complex):
        if abs(valor.imag) < TOLERANCIA_COMPLEJA:
            valor = valor.real
        else:
            return _formatear(valor, decimales)
    if isinstance(valor, float):
        if not math.isfinite(valor):
            return "No disponible"
        if not valor.is_integer():
            return f"{valor:.{decimales}f}"
        valor = int(valor)
    if isinstance(valor, int):
        return str(valor)
    return str(valor)


def _es_complejo_significativo(valor):
    return isinstance(valor, complex) and abs(valor.imag) >= TOLERANCIA_COMPLEJA


def _es_finito(valor):
    if isinstance(valor, complex):
        return math.isfinite(valor.real) and math.isfinite(valor.imag)
    if isinstance(valor, (int, float)):
        return math.isfinite(valor)
    return False


def _latex_num(valor, decimales=6):
    """Número para LaTeX, con formato amigable de complejos (a + bi)."""
    if isinstance(valor, complex) and abs(valor.imag) >= TOLERANCIA_COMPLEJA:
        real = valor.real
        imag = valor.imag
        if abs(real) < TOLERANCIA_COMPLEJA:
            return f"{imag:.{decimales}f}i" if imag >= 0 else f"-{abs(imag):.{decimales}f}i"
        signo = "+" if imag >= 0 else "-"
        return f"{real:.{decimales}f} {signo} {abs(imag):.{decimales}f}i"
    return _valor_display(valor, decimales)


def _paren(valor, decimales=6):
    """Envuelve en paréntesis un valor negativo o complejo para operar con él."""
    texto = _latex_num(valor, decimales).strip()
    if _es_complejo_significativo(valor):
        return f"\\left({texto}\\right)"
    if texto.startswith("-"):
        return f"\\left({texto}\\right)"
    return texto


def _parentizar(texto):
    return f"\\left({texto}\\right)"


def _diferencia_latex(valor_1, valor_2, decimales=6):
    return f"{_latex_num(valor_1, decimales)} - {_paren(valor_2, decimales)}"


def _formatear_error(valor, decimales=6):
    if valor is None:
        return "No disponible"
    if isinstance(valor, float) and not math.isfinite(valor):
        return "No disponible"
    if isinstance(valor, (int, float)):
        return f"{valor:.{decimales}f} %"
    return str(valor)


def _expresion_con_valor(texto_expr, valor, decimales=6):
    valor_txt = _valor_display(valor, decimales)
    cadena = texto_expr.replace("**", "^")
    cadena = re.sub(r"(?<![A-Za-z0-9_])x(?![A-Za-z0-9_])", f"({valor_txt})", cadena)
    cadena = re.sub(r"(?<=\d)\*\((?=\d)", "(", cadena)
    cadena = cadena.replace(f"(({valor_txt}))", f"({valor_txt})")
    return cadena


def _unir_con_signos(partes):
    if not partes:
        return ""
    resultado = partes[0]
    for parte in partes[1:]:
        if parte.startswith("-"):
            resultado += " - " + parte[1:].lstrip()
        else:
            resultado += " + " + parte
    return resultado


def _resta(izquierda, derecha):
    if derecha.startswith("-"):
        return f"{izquierda} + {derecha[1:]}"
    return f"{izquierda} - {derecha}"


def _obtener_simbolo(expresion):
    return next((s for s in getattr(expresion, "free_symbols", []) if getattr(s, "name", None) == "x"), None)


def _desglose_polinomio(expresion, valor, decimales=6):
    try:
        simbolo = _obtener_simbolo(expresion)
        if simbolo is None:
            return None
        if _es_complejo_significativo(valor):
            return None
        expandida = sp.expand(expresion)
        if not expandida.is_polynomial(simbolo):
            return None
        terminos = expandida.as_ordered_terms()
        if not (2 <= len(terminos) <= 10):
            return None
    except Exception:
        return None

    textos = []
    valores = []
    total = 0.0
    try:
        for termino in terminos:
            valor_complejo = complex(termino.subs(simbolo, sp.Float(valor)).evalf())
            if abs(valor_complejo.imag) > 1e-12:
                return None
            valor_termino = float(valor_complejo.real)
            if abs(valor_termino) < 1e-14:
                return None
            textos.append(_expresion_con_valor(str(termino), valor, decimales))
            valores.append(_valor_display(valor_termino, decimales))
            total += valor_termino
    except Exception:
        return None

    return (_unir_con_signos(textos), _unir_con_signos(valores), _valor_display(total, decimales))


def _evaluar_expresion(expresion, valor):
    """Evalúa una expresión de SymPy en un valor real o complejo."""
    try:
        simbolo = _obtener_simbolo(expresion)
        if simbolo is None:
            return None
        if _es_complejo_significativo(valor):
            return complex(expresion.subs(simbolo, complex(valor)).evalf())
        return float(expresion.subs(simbolo, sp.Float(valor)).evalf())
    except Exception:
        return None


def _latex_funcion(expresion):
    if expresion is None:
        return "?"
    try:
        return sp.latex(expresion)
    except Exception:
        return str(expresion)


def _derivada_de(expresion, parametros=None):
    if parametros and parametros.get("derivada") is not None:
        return parametros["derivada"]
    if expresion is None:
        return None
    try:
        return sp.diff(expresion, _simbolo_x())
    except Exception:
        return None


def _texto_comparacion_error(ea, error_permitido, criterio, decimales):
    if criterio != "error" or error_permitido is None:
        return "El criterio de parada es por número fijo de iteraciones; el error solo describe el avance entre pasos."
    if not (isinstance(ea, (int, float)) and math.isfinite(ea)):
        return "No existe un valor anterior con el que comparar en esta primera aproximación."
    ea_txt = _valor_display(ea, decimales)
    ep_txt = _valor_display(error_permitido, decimales)
    if ea < error_permitido:
        return (
            f"Como $Ea = {ea_txt}\\,\\% < {ep_txt}\\,\\%$ (error permitido), "
            "**se cumple el criterio y el método puede detenerse**."
        )
    return (
        f"Como $Ea = {ea_txt}\\,\\% \\ge {ep_txt}\\,\\%$ (error permitido), "
        "**todavía no se cumple el criterio**, por lo que se continúa."
    )
