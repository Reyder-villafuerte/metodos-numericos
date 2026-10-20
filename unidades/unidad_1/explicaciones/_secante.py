"""Explicación paso a paso del método de la Secante."""

import math

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
    _diferencia_latex,
    _latex_funcion,
    _parentizar,
    _resta,
    _texto_comparacion_error,
    _valor_display,
)


def _iteraciones_secante(filas, expresion, decimales, criterio, error_permitido):
    bloques = ["### 4. Explicación completa de cada iteración\n"]
    if not filas:
        bloques.append("No se realizaron iteraciones.\n")
        return "\n".join(bloques)

    bloques.append(
        "En cada paso se usan dos aproximaciones y sus imágenes para estimar la pendiente de la secante. "
        "Despliegue cada iteración para ver los cálculos.\n"
    )

    expr_latex = _latex_funcion(expresion)

    for fila in filas:
        numero = fila["i"]
        x_prev = fila["xi-1"]
        x_act = fila["xi"]
        f_prev = fila["f(xi-1)"]
        f_act = fila["f(xi)"]
        x_nuevo = fila["xi+1"]
        ea = fila["Ea (%)"]

        xp_txt = _valor_display(x_prev, decimales)
        xa_txt = _valor_display(x_act, decimales)
        fp_txt = _valor_display(f_prev, decimales)
        fa_txt = _valor_display(f_act, decimales)
        xn_txt = _valor_display(x_nuevo, decimales)

        bloques.append(f"<details><summary><b>Iteración {numero}</b></summary>\n")
        bloques.append(f"#### Iteración {numero}\n")

        bloques.append("**1. Valores disponibles:**\n")
        bloques.append(f"$$x_{{{numero - 1}}} = {xp_txt}, \\qquad x_{{{numero}}} = {xa_txt}$$\n")
        bloques.append(f"$$f(x) = {expr_latex}$$\n")
        bloques.append(f"$$f(x_{{{numero - 1}}}) = f({xp_txt}) = {fp_txt}$$\n")
        bloques.append(f"$$f(x_{{{numero}}}) = f({xa_txt}) = {fa_txt}$$\n")

        bloques.append("**2. Fórmula de la secante:**\n")
        bloques.append(
            "$$x_{n+1} = x_n - \\frac{f(x_n)\\,(x_n - x_{n-1})}{f(x_n) - f(x_{n-1})}$$\n"
        )

        bloques.append("**3. Sustitución de los valores reales:**\n")
        bloques.append(
            f"$$x_{{{numero + 1}}} = {xa_txt} - \\frac{{{fa_txt}\\,"
            f"{_parentizar(_diferencia_latex(x_act, x_prev, decimales))}}}"
            f"{{{_diferencia_latex(f_act, f_prev, decimales)}}}$$\n"
        )
        numerador = f_act * (x_act - x_prev)
        denominador = f_act - f_prev
        bloques.append(
            f"$$x_{{{numero + 1}}} = {xa_txt} - \\frac{{{_valor_display(numerador, decimales)}}}"
            f"{{{_valor_display(denominador, decimales)}}}$$\n"
        )
        if denominador != 0:
            cociente = numerador / denominador
            cociente_txt = _valor_display(cociente, decimales)
            bloques.append(f"$$x_{{{numero + 1}}} = {_resta(xa_txt, cociente_txt)}$$\n")
        bloques.append(f"$$x_{{{numero + 1}}} = {xn_txt}$$\n")

        bloques.append("**4. Cálculo del error aproximado:**\n")
        bloques.append(
            "$$E_a = \\left| \\frac{x_{\\text{nuevo}} - x_{\\text{anterior}}}{x_{\\text{nuevo}}} "
            "\\right| \\times 100$$\n"
        )
        if isinstance(ea, (int, float)) and math.isfinite(ea):
            bloques.append(
                f"$$E_a = \\left| \\frac{{{xn_txt} - {xa_txt}}}{{{xn_txt}}} \\right| \\times 100$$\n"
            )
            bloques.append(f"$$E_a = {_valor_display(ea, decimales)} \\%$$\n")
            bloques.append(_texto_comparacion_error(ea, error_permitido, criterio, decimales) + "\n")
        else:
            bloques.append(f"$$E_a = {_valor_display(ea, decimales)}$$\n")

        bloques.append("</details>\n")
        bloques.append("")

    return "\n".join(bloques)


def _seccion_interpretacion_secante(filas, decimales):
    bloques = ["### 6. Interpretación geométrica y ausencia de derivada\n"]
    bloques.append(
        "La secante sustituye la derivada $f'(x_n)$ de Newton-Raphson por la **pendiente media** entre "
        "dos puntos:\n"
    )
    bloques.append(
        "$$f'(x_n) \\approx \\frac{f(x_n) - f(x_{n-1})}{x_n - x_{n-1}}$$\n"
    )
    bloques.append(
        "Esa es la pendiente de la recta secante que une $(x_{n-1}, f(x_{n-1}))$ y $(x_n, f(x_n))$. "
        "Por eso el método **no requiere** la derivada simbólica: solo necesita evaluar la función en dos "
        "puntos.\n"
    )
    if filas:
        primera = filas[0]
        delta = primera["xi"] - primera["xi-1"]
        if delta != 0:
            pendiente = (primera["f(xi)"] - primera["f(xi-1)"]) / delta
            bloques.append(
                f"En la primera iteración, la pendiente de la secante es "
                f"${_valor_display(pendiente, decimales)}$.\n"
            )
    bloques.append("")
    return "\n".join(bloques)


def generar_explicacion_secante(expresion, filas, resultado, parametros, funcion_texto,
                                error_permitido, max_iteraciones, criterio, decimales):
    secciones = []
    secciones.append(_seccion_presentacion_generica("Secante", expresion, parametros, funcion_texto,
                                                    error_permitido, max_iteraciones, criterio, decimales))
    secciones.append(_seccion_objetivo("Secante"))
    secciones.append(_seccion_formula_general("Secante"))
    if filas:
        secciones.append(_iteraciones_secante(filas, expresion, decimales, criterio, error_permitido))
        secciones.append(_seccion_error(filas, error_permitido, criterio, decimales,
                                        clave="xi+1", clave_funcion="f(xi)", etiqueta="$x$"))
        secciones.append(_seccion_interpretacion_secante(filas, decimales))
        secciones.append(_seccion_convergencia(resultado, filas, error_permitido, criterio, decimales, "Secante"))
    else:
        secciones.append(_seccion_sin_iteraciones("Secante", expresion, resultado, parametros, decimales))
    secciones.append(_seccion_resultado_final(resultado, expresion, decimales, "Secante", criterio, parametros, len(filas)))
    return "\n".join(secciones)
