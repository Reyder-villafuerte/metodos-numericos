"""Explicaciones paso a paso de Bisección y Regla falsa."""

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
    _desglose_polinomio,
    _expresion_con_valor,
    _latex_funcion,
    _resta,
    _texto_comparacion_error,
    _valor_display,
)


def _iteraciones_intervalo(metodo, filas, expresion, decimales, criterio, error_permitido):
    bloques = ["### 4. Explicación completa de cada iteración\n"]
    if not filas:
        bloques.append("No se realizaron iteraciones.\n")
        return "\n".join(bloques)

    bloques.append(
        "Cada paso se detalla a continuación. Despliegue cada iteración para ver el procedimiento "
        "matemático completo.\n"
    )

    texto_expr = str(expresion)
    expr_latex = _latex_funcion(expresion)

    for i, fila in enumerate(filas):
        numero = fila["i"]
        a = fila["ai"]
        b = fila["bi"]
        m = fila["mi"]
        fa = fila["f(ai)"]
        fb = fila["f(bi)"]
        fm = fila["f(mi)"]
        ea = fila["Ea (%)"]

        a_txt = _valor_display(a, decimales)
        b_txt = _valor_display(b, decimales)
        m_txt = _valor_display(m, decimales)
        fa_txt = _valor_display(fa, decimales)
        fb_txt = _valor_display(fb, decimales)
        fm_txt = _valor_display(fm, decimales)

        bloques.append(f"<details><summary><b>Iteración {numero}</b></summary>\n")
        bloques.append(f"#### Iteración {numero}\n")

        bloques.append("**1. Intervalo actual:**\n")
        bloques.append(f"$$[a_{{{numero}}},\\; b_{{{numero}}}] = [{a_txt},\\; {b_txt}]$$\n")

        bloques.append("**2. Evaluación en los extremos:**\n")
        bloques.append(f"$$f(x) = {expr_latex}$$\n")
        fa_sust = _expresion_con_valor(texto_expr, a, decimales)
        bloques.append(f"$$f(a_{{{numero}}}) = f({a_txt}) = {fa_sust}$$\n")
        desglose_a = _desglose_polinomio(expresion, a, decimales)
        if desglose_a is not None:
            terminos, valores, total = desglose_a
            bloques.append(f"$$f({a_txt}) = {terminos} = {valores} = {total}$$\n")
        bloques.append(f"$$f(a_{{{numero}}}) = {fa_txt}$$\n")
        fb_sust = _expresion_con_valor(texto_expr, b, decimales)
        bloques.append(f"$$f(b_{{{numero}}}) = f({b_txt}) = {fb_sust}$$\n")
        desglose_b = _desglose_polinomio(expresion, b, decimales)
        if desglose_b is not None:
            terminos, valores, total = desglose_b
            bloques.append(f"$$f({b_txt}) = {terminos} = {valores} = {total}$$\n")
        bloques.append(f"$$f(b_{{{numero}}}) = {fb_txt}$$\n")

        if metodo == "Bisección":
            bloques.append("**3. Punto medio del intervalo:**\n")
            bloques.append("$$m_i = \\frac{a_i + b_i}{2}$$\n")
            suma = a + b
            bloques.append(
                f"$$m_{{{numero}}} = \\frac{{{a_txt} + {b_txt}}}{{2}} = "
                f"\\frac{{{_valor_display(suma, decimales)}}}{{2}}$$\n"
            )
            bloques.append(f"$$m_{{{numero}}} = {m_txt}$$\n")
            etiqueta = "m"
            descripcion_paso = "punto medio"
        else:
            bloques.append("**3. Aplicación de la regla falsa:**\n")
            bloques.append("$$x_r = b - \\frac{f(b)\\,(b - a)}{f(b) - f(a)}$$\n")
            bloques.append(
                f"$$x_r = {b_txt} - \\frac{{{fb_txt}\\,({b_txt} - {a_txt})}}{{{fb_txt} - {fa_txt}}}$$\n"
            )
            numerador = fb * (b - a)
            denominador = fb - fa
            bloques.append(
                f"$$x_r = {b_txt} - \\frac{{{_valor_display(numerador, decimales)}}}"
                f"{{{_valor_display(denominador, decimales)}}}$$\n"
            )
            if denominador != 0:
                cociente = numerador / denominador
                cociente_txt = _valor_display(cociente, decimales)
                bloques.append(f"$$x_r = {_resta(b_txt, cociente_txt)}$$\n")
            bloques.append(f"$$x_r = {m_txt}$$\n")
            etiqueta = "x_r"
            descripcion_paso = "aproximación de regla falsa"

        bloques.append(f"**4. Evaluación de la nueva aproximación ({descripcion_paso}):**\n")
        fm_sust = _expresion_con_valor(texto_expr, m, decimales)
        bloques.append(f"$$f({etiqueta}) = f({m_txt}) = {fm_sust}$$\n")
        desglose_m = _desglose_polinomio(expresion, m, decimales)
        if desglose_m is not None:
            terminos, valores, total = desglose_m
            bloques.append(f"$$f({m_txt}) = {terminos} = {valores} = {total}$$\n")
        bloques.append(f"$$f({m_txt}) = {fm_txt}$$\n")

        bloques.append("**5. Análisis de signos y decisión del nuevo intervalo:**\n")
        producto = fa * fm
        bloques.append(
            f"$$f(a_{{{numero}}})\\cdot f({etiqueta}) = ({fa_txt})\\cdot({fm_txt}) = "
            f"{_valor_display(producto, decimales)}$$\n"
        )
        if fm == 0:
            bloques.append(
                "Como $f$ evaluada en la nueva aproximación es **exactamente cero**, este punto es la "
                "raíz y el método finaliza.\n"
            )
        elif producto < 0:
            bloques.append(
                "El producto es **negativo**, lo que significa que $f(a_i)$ y $f(m_i)$ tienen signos "
                "opuestos. Por lo tanto, la raíz está dentro de $[a_i, m_i]$ y **se conserva ese "
                "subintervalo**: el extremo superior pasa a ser $b = m$.\n"
            )
        else:
            bloques.append(
                "El producto es **positivo**, lo que significa que $f(a_i)$ y $f(m_i)$ tienen el mismo "
                "signo. Por lo tanto, la raíz no está entre $a_i$ y $m_i$; **se conserva $[m_i, b_i]$**: "
                "el extremo inferior pasa a ser $a = m$.\n"
            )

        bloques.append("**6. Cálculo del error aproximado:**\n")
        bloques.append("$$E_a = \\left| \\frac{x_{\\text{nuevo}} - x_{\\text{anterior}}}{x_{\\text{nuevo}}} \\right| \\times 100$$\n")
        if isinstance(ea, (int, float)) and math.isfinite(ea):
            if i == 0:
                bloques.append(
                    "En la **primera iteración** no existe una aproximación anterior, por lo que el "
                    "error se reporta como **No disponible**.\n"
                )
            else:
                anterior = filas[i - 1]["mi"]
                anterior_txt = _valor_display(anterior, decimales)
                bloques.append(
                    f"$$E_a = \\left| \\frac{{{m_txt} - {anterior_txt}}}{{{m_txt}}} \\right| "
                    "\\times 100$$\n"
                )
                bloques.append(f"$$E_a = {_valor_display(ea, decimales)} \\%$$\n")
            bloques.append(_texto_comparacion_error(ea, error_permitido, criterio, decimales) + "\n")
        else:
            bloques.append("En esta iteración el error es **No disponible** (es la primera aproximación).\n")

        bloques.append("</details>\n")
        bloques.append("")

    return "\n".join(bloques)


def _seccion_interpretacion_intervalo(metodo, filas, decimales):
    bloques = ["### 6. Interpretación geométrica\n"]
    if not filas:
        return "\n".join(bloques)
    if metodo == "Bisección":
        bloques.append(
            "Geométricamente, cada iteración divide el intervalo a la mitad. La raíz queda siempre "
            "atrapada en la mitad que conserva el cambio de signo, de modo que la longitud del intervalo "
            "se reduce a la mitad en cada paso. Esa reducción garantiza la convergencia, aunque puede ser "
            "más lenta que los métodos abiertos.\n"
        )
        ancho_inicial = filas[0]["bi"] - filas[0]["ai"]
        ancho_final = filas[-1]["bi"] - filas[-1]["ai"]
        bloques.append(
            f"- Ancho del intervalo inicial: ${_valor_display(ancho_inicial, decimales)}$\n"
            f"- Ancho del último intervalo registrado: ${_valor_display(ancho_final, decimales)}$\n"
        )
    else:
        bloques.append(
            "Geométricamente, la regla falsa traza la **cuerda** (recta secante) entre los dos extremos "
            "del intervalo y toma su cruce con el eje $x$. Como la cuerda sigue la forma de la función, "
            "suele acercarse a la raíz más rápido que la bisección.\n"
        )
        bloques.append(
            "Un extremo puede permanecer fijo durante varias iteraciones; eso indica que la función es "
            "muy curvada en un lado del intervalo.\n"
        )
    bloques.append("")
    return "\n".join(bloques)


def _generar_explicacion_intervalo(metodo, expresion, filas, resultado, parametros,
                                   funcion_texto, error_permitido, max_iteraciones,
                                   criterio, decimales):
    secciones = []
    secciones.append(_seccion_presentacion_generica(metodo, expresion, parametros, funcion_texto,
                                                    error_permitido, max_iteraciones, criterio, decimales))
    secciones.append(_seccion_objetivo(metodo))
    secciones.append(_seccion_formula_general(metodo))
    if filas:
        secciones.append(_iteraciones_intervalo(metodo, filas, expresion, decimales, criterio, error_permitido))
        secciones.append(_seccion_error(filas, error_permitido, criterio, decimales,
                                        clave="mi", clave_funcion="f(mi)", etiqueta="$m$"))
        secciones.append(_seccion_interpretacion_intervalo(metodo, filas, decimales))
        secciones.append(_seccion_convergencia(resultado, filas, error_permitido, criterio, decimales, metodo))
    else:
        secciones.append(_seccion_sin_iteraciones(metodo, expresion, resultado, parametros, decimales))
    secciones.append(_seccion_resultado_final(resultado, expresion, decimales, metodo, criterio, parametros, len(filas)))
    return "\n".join(secciones)


def generar_explicacion_biseccion(expresion, filas, resultado, parametros, funcion_texto,
                                  error_permitido, max_iteraciones, criterio, decimales):
    return _generar_explicacion_intervalo(
        "Bisección", expresion, filas, resultado, parametros, funcion_texto,
        error_permitido, max_iteraciones, criterio, decimales,
    )


def generar_explicacion_regla_falsa(expresion, filas, resultado, parametros, funcion_texto,
                                    error_permitido, max_iteraciones, criterio, decimales):
    return _generar_explicacion_intervalo(
        "Regla falsa", expresion, filas, resultado, parametros, funcion_texto,
        error_permitido, max_iteraciones, criterio, decimales,
    )
