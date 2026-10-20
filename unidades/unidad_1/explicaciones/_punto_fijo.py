"""Explicación paso a paso del método de Punto fijo."""

import math

import sympy as sp

from ._comunes import (
    _seccion_convergencia,
    _seccion_error,
    _seccion_formula_general,
    _seccion_objetivo,
    _seccion_presentacion_generica,
    _seccion_resultado_final,
    _seccion_sin_iteraciones,
)
from ._formato import (
    _desglose_polinomio,
    _expresion_con_valor,
    _latex_funcion,
    _simbolo_x,
    _texto_comparacion_error,
    _valor_display,
)


def _iteraciones_punto_fijo(filas, despeje, decimales, criterio, error_permitido):
    bloques = ["### 4. Explicación completa de cada iteración\n"]
    if not filas:
        bloques.append("No se realizaron iteraciones.\n")
        return "\n".join(bloques)

    bloques.append(
        "Recuerde que aquí se trabaja con el despeje $g(x)$, no directamente con $f(x)$. "
        "Cada iteración evalúa $g$ en el valor actual.\n"
    )

    texto_g = str(despeje) if despeje is not None else "g(x)"
    g_latex = _latex_funcion(despeje)

    for i, fila in enumerate(filas):
        numero = fila["i"]
        xi = fila["xi"]
        gxi = fila["g(xi)"]
        ea = fila["Ea (%)"]

        xi_txt = _valor_display(xi, decimales)
        gxi_txt = _valor_display(gxi, decimales)

        bloques.append(f"<details><summary><b>Iteración {numero}</b></summary>\n")
        bloques.append(f"#### Iteración {numero}\n")

        bloques.append("**1. Valor actual:**\n")
        if i == 0:
            bloques.append(f"$$x_0 = {xi_txt}$$\n")
            bloques.append("Partimos del valor inicial $x_0$.\n")
        else:
            bloques.append(f"$$x_{{{numero}}} = {xi_txt}$$\n")
            bloques.append("Utilizamos el valor obtenido en la iteración anterior.\n")

        bloques.append("**2. Fórmula de actualización:**\n")
        bloques.append("$$x_{n+1} = g(x_n)$$\n")
        bloques.append(f"$$x_{{{numero}}} = g(x_{{{numero - 1}}})$$\n")

        bloques.append("**3. Sustitución en $g(x)$:**\n")
        bloques.append(f"$$g(x) = {g_latex}$$\n")
        g_sust = _expresion_con_valor(texto_g, xi, decimales)
        bloques.append(f"$$g({xi_txt}) = {g_sust}$$\n")
        desglose = _desglose_polinomio(despeje, xi, decimales) if despeje is not None else None
        if desglose is not None:
            terminos, valores, total = desglose
            bloques.append(f"$$g({xi_txt}) = {terminos} = {valores} = {total}$$\n")

        bloques.append("**4. Resultado de la iteración:**\n")
        bloques.append(f"$$x_{{{numero}}} = {gxi_txt}$$\n")
        bloques.append(f"> $x_{{{numero - 1}}} = {xi_txt}$ → $x_{{{numero}}} = {gxi_txt}$\n")

        bloques.append("**5. Cálculo del error aproximado:**\n")
        bloques.append(
            "$$E_a = \\left| \\frac{x_{\\text{nuevo}} - x_{\\text{anterior}}}{x_{\\text{nuevo}}} "
            "\\right| \\times 100$$\n"
        )
        if isinstance(ea, (int, float)) and math.isfinite(ea):
            bloques.append(
                f"$$E_a = \\left| \\frac{{{gxi_txt} - {xi_txt}}}{{{gxi_txt}}} \\right| \\times 100$$\n"
            )
            bloques.append(f"$$E_a = {_valor_display(ea, decimales)} \\%$$\n")
            bloques.append(_texto_comparacion_error(ea, error_permitido, criterio, decimales) + "\n")
        else:
            bloques.append(f"$$E_a = {_valor_display(ea, decimales)}$$\n")

        bloques.append("</details>\n")
        bloques.append("")

    return "\n".join(bloques)


def _seccion_convergencia_punto_fijo(despeje, filas, resultado, decimales):
    bloques = ["### 6. Criterio de convergencia: $|g'(x)| < 1$\n"]
    if despeje is None:
        bloques.append("No hay un despeje $g(x)$ disponible para analizar su derivada.\n")
        return "\n".join(bloques)

    try:
        derivada_g = sp.diff(despeje, _simbolo_x())
        bloques.append("La derivada del despeje es:\n")
        bloques.append(f"$$g'(x) = {_latex_funcion(derivada_g)}$$\n")
    except Exception:
        derivada_g = None

    if derivada_g is not None and filas:
        try:
            valor_inicial = float(derivada_g.subs(_simbolo_x(), sp.Float(filas[0]["xi"])).evalf())
            bloques.append(
                f"Evaluando en el valor inicial $x_0 = {_valor_display(filas[0]['xi'], decimales)}$:\n"
            )
            bloques.append(
                f"$$|g'(x_0)| = {_valor_display(abs(valor_inicial), decimales)}$$\n"
            )
            if abs(valor_inicial) < 1:
                bloques.append(
                    "Como $|g'(x_0)| < 1$, el criterio **sugiere** convergencia local. Tenga en cuenta "
                    "que este criterio es local y orientativo; el estado real del método se reporta al final.\n"
                )
            else:
                bloques.append(
                    "Como $|g'(x_0)| \\ge 1$, el criterio **no garantiza** la convergencia y el método "
                    "podría oscilar o divergir.\n"
                )
        except Exception:
            pass

    if resultado.convergio is False:
        bloques.append(
            "El método **no alcanzó** el criterio de parada. Esto puede deberse a un despeje poco "
            "adecuado o a que $|g'(x)|$ no es suficientemente pequeño en la zona de trabajo.\n"
        )
    else:
        bloques.append(
            "El resultado real del método se describe en la sección de análisis de convergencia y en el "
            "resultado final.\n"
        )
    bloques.append("")
    return "\n".join(bloques)


def generar_explicacion_punto_fijo(expresion, filas, resultado, parametros, funcion_texto,
                                   error_permitido, max_iteraciones, criterio, decimales):
    parametros = parametros or {}
    despeje = parametros.get("despeje")
    secciones = []
    secciones.append(_seccion_presentacion_generica("Punto fijo", expresion, parametros, funcion_texto,
                                                    error_permitido, max_iteraciones, criterio, decimales))
    secciones.append(_seccion_objetivo("Punto fijo"))
    secciones.append(_seccion_formula_general("Punto fijo"))
    if filas:
        secciones.append(_iteraciones_punto_fijo(filas, despeje, decimales, criterio, error_permitido))
        secciones.append(_seccion_error(filas, error_permitido, criterio, decimales,
                                        clave="g(xi)", clave_funcion="g(xi)", etiqueta="$g(x)$"))
        secciones.append(_seccion_convergencia_punto_fijo(despeje, filas, resultado, decimales))
        secciones.append(_seccion_convergencia(resultado, filas, error_permitido, criterio, decimales, "Punto fijo"))
    else:
        secciones.append(_seccion_sin_iteraciones("Punto fijo", expresion, resultado, parametros, decimales))
    secciones.append(_seccion_resultado_final(resultado, expresion, decimales, "Punto fijo", criterio, parametros, len(filas)))
    return "\n".join(secciones)
