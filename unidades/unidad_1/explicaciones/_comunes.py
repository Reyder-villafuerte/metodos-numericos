"""Secciones comunes a todos los métodos (presentación, objetivo, fórmula, etc.)."""

import math

import sympy as sp

from ._formato import (
    _derivada_de,
    _es_finito,
    _evaluar_expresion,
    _expresion_con_valor,
    _formatear,
    _formatear_error,
    _latex_funcion,
    _valor_display,
)


def _cerca_de_cero(valor, decimales):
    try:
        return abs(valor) < 10 ** (-decimales)
    except Exception:
        return False


def _lineas_parametros(metodo, parametros, decimales):
    parametros = parametros or {}
    lineas = []
    fmt = lambda valor: _formatear(valor, decimales)
    if metodo in ("Bisección", "Regla falsa"):
        lineas.append(f"- **Extremo inferior** $a$ = {fmt(parametros.get('a', '?'))}")
        lineas.append(f"- **Extremo superior** $b$ = {fmt(parametros.get('b', '?'))}")
    elif metodo == "Punto fijo":
        lineas.append(f"- **Valor inicial** $x_0$ = {fmt(parametros.get('x0', '?'))}")
    elif metodo == "Newton-Raphson":
        lineas.append(f"- **Valor inicial** $x_0$ = {fmt(parametros.get('x0', '?'))}")
    elif metodo == "Secante":
        lineas.append(f"- **Primer valor inicial** $x_0$ = {fmt(parametros.get('x0', '?'))}")
        lineas.append(f"- **Segundo valor inicial** $x_1$ = {fmt(parametros.get('x1', '?'))}")
    elif metodo == "Müller":
        lineas.append(f"- **Primer valor inicial** $x_0$ = {fmt(parametros.get('x0', '?'))}")
        lineas.append(f"- **Segundo valor inicial** $x_1$ = {fmt(parametros.get('x1', '?'))}")
        lineas.append(f"- **Tercer valor inicial** $x_2$ = {fmt(parametros.get('x2', '?'))}")
    return lineas


def _seccion_presentacion_generica(metodo, expresion, parametros, funcion_texto,
                                   error_permitido, max_iteraciones, criterio, decimales):
    parametros = parametros or {}
    bloques = ["### 1. Presentación del ejercicio\n"]
    bloques.append(f"**Método seleccionado:** {metodo}\n")
    if funcion_texto:
        bloques.append(f"**Función ingresada:** `{funcion_texto}`\n")
    if expresion is not None:
        bloques.append(f"$$f(x) = {_latex_funcion(expresion)}$$\n")

    if metodo == "Punto fijo":
        despeje = parametros.get("despeje")
        if despeje is not None:
            bloques.append(f"**Despeje ingresado:** $$g(x) = {_latex_funcion(despeje)}$$\n")
    if metodo == "Newton-Raphson":
        derivada = _derivada_de(expresion, parametros)
        if derivada is not None:
            bloques.append(f"**Derivada calculada con SymPy:** $$f'(x) = {_latex_funcion(derivada)}$$\n")

    bloques.append("**Parámetros iniciales:**\n")
    bloques.extend(_lineas_parametros(metodo, parametros, decimales))
    if criterio == "error":
        error_txt = _formatear(error_permitido, decimales) if error_permitido is not None else "N/A"
        bloques.append("- **Criterio de parada:** error porcentual permitido")
        bloques.append(f"- **Error permitido** = {error_txt} %")
        bloques.append(f"- **Máximo de iteraciones (seguridad)** = {max_iteraciones}")
    else:
        bloques.append("- **Criterio de parada:** número fijo de iteraciones")
        bloques.append(f"- **Iteraciones solicitadas** = {max_iteraciones}")
    bloques.append(f"- **Decimales para visualizar** = {decimales}")
    bloques.append("")
    return "\n".join(bloques)


_OBJETIVOS = {
    "Bisección": (
        "### 2. ¿Qué busca el método de Bisección?\n",
        [
            "El método de bisección busca un valor de $x$ tal que $f(x)$ sea **igual o muy cercano a cero**, "
            "es decir, una **raíz** de la función: el punto donde la gráfica cruza el eje horizontal.",
            "La raíz puede ser positiva, negativa o cero; lo que debe acercarse a cero es el valor de $f(x)$, "
            "no necesariamente $x$.",
            "Para funcionar necesita un intervalo $[a, b]$ donde la función **cambia de signo** "
            "($f(a)$ y $f(b)$ tienen signos opuestos), lo que garantiza que hay al menos una raíz dentro. "
            "En cada paso parte el intervalo por la mitad: el punto medio $m$ es la nueva aproximación y se "
            "conserva la mitad que sigue conteniendo el cambio de signo.",
        ],
    ),
    "Regla falsa": (
        "### 2. ¿Qué busca el método de Regla falsa?\n",
        [
            "El método de regla falsa busca un valor de $x$ tal que $f(x) = 0$, partiendo de un intervalo "
            "$[a, b]$ con cambio de signo.",
            "En lugar de cortar el intervalo por la mitad, traza la **recta secante** que une los puntos "
            "$(a, f(a))$ y $(b, f(b))$, y toma como nueva aproximación el punto donde esa recta cruza el eje "
            "$x$. Por eso también se conoce como método de la falsa posición.",
            "Como usa la forma de la función a través de los extremos, suele acercarse a la raíz más rápido "
            "que la bisección, manteniendo el intervalo con cambio de signo para no perder la raíz.",
        ],
    ),
    "Punto fijo": (
        "### 2. ¿Qué busca el método de Punto fijo?\n",
        [
            "El método de punto fijo busca un valor de $x$ que cumpla $x = g(x)$. Cuando $g$ proviene de "
            "despejar $f(x) = 0$, ese punto fijo es precisamente una **raíz** de $f$.",
            "La idea es transformar la ecuación original en una **regla de actualización**: se toma una "
            "aproximación $x_i$, se evalúa $g(x_i)$ y ese resultado se convierte en la siguiente aproximación "
            "$x_{i+1}$. Repitiendo el proceso, la sucesión puede acercarse al punto fijo.",
            "La convergencia depende de la forma del despeje: cerca de la raíz conviene que $|g'(x)| < 1$. "
            "Este criterio es una **indicación local**, no una garantía absoluta.",
        ],
    ),
    "Newton-Raphson": (
        "### 2. ¿Qué busca Newton-Raphson?\n",
        [
            "El método de Newton-Raphson busca encontrar un valor de $x$ tal que $f(x)$ sea **igual o muy "
            "cercano a cero**, es decir, la **raíz** de la función.",
            "La raíz puede ser positiva, negativa o cero. Lo que debe acercarse a cero es el valor de $f(x)$.",
            "La idea principal es partir de una estimación inicial $x_0$ e ir mejorándola usando la **recta "
            "tangente** de la función en cada punto.",
        ],
    ),
    "Secante": (
        "### 2. ¿Qué busca el método de la Secante?\n",
        [
            "El método de la secante busca un valor de $x$ tal que $f(x) = 0$ usando dos aproximaciones "
            "iniciales $x_0$ y $x_1$.",
            "Su idea es parecida a la de Newton-Raphson, pero en lugar de la derivada simbólica $f'(x)$ "
            "utiliza la **pendiente de la recta secante** que pasa por los dos puntos recientes. Así "
            "aproxima la derivada sin calcularla formalmente.",
            "Con esa pendiente trazada, se prolonga la recta hasta el eje $x$ y ese cruce es la nueva "
            "aproximación. Suele converger rápido, aunque no está garantizado.",
        ],
    ),
    "Müller": (
        "### 2. ¿Qué busca el método de Müller?\n",
        [
            "El método de Müller busca raíces de $f(x) = 0$, pero en lugar de una recta usa una **parábola** "
            "(interpolación cuadrática) que pasa por tres aproximaciones $x_0, x_1, x_2$.",
            "Con esa parábola se calcula dónde corta el eje $x$ y ese valor se convierte en la nueva "
            "aproximación $x_3$. Como una parábola puede no cortar el eje real, el método es capaz de "
            "encontrar **raíces complejas**.",
            "Requiere tres puntos distintos y es sensible a divisiones por números pequeños, por eso el "
            "algoritmo elige con cuidado el denominador de la fórmula.",
        ],
    ),
}


def _seccion_objetivo(metodo="Newton-Raphson"):
    titulo, parrafos = _OBJETIVOS.get(metodo, _OBJETIVOS["Newton-Raphson"])
    bloques = [titulo]
    for parrafo in parrafos:
        bloques.append(parrafo + "\n")
    bloques.append("")
    return "\n".join(bloques)


_FORMULAS = {
    "Bisección": (
        "### 3. Fórmula general de Bisección\n",
        "$$m = \\frac{a + b}{2}$$\n",
        [
            ("$a$", "Extremo inferior del intervalo actual"),
            ("$b$", "Extremo superior del intervalo actual"),
            ("$m$", "Punto medio, nueva aproximación de la raíz"),
        ],
        "En cada paso se corta el intervalo a la mitad. El criterio para elegir la mitad que se conserva "
        "es el signo de $f(a)\\cdot f(m)$: si es negativo, la raíz está entre $a$ y $m$; si es positivo, "
        "está entre $m$ y $b$.\n",
    ),
    "Regla falsa": (
        "### 3. Fórmula general de Regla falsa\n",
        "$$x_r = b - \\frac{f(b)\\,(b - a)}{f(b) - f(a)}$$\n",
        [
            ("$a$", "Extremo inferior del intervalo actual"),
            ("$b$", "Extremo superior del intervalo actual"),
            ("$f(a)$", "Función evaluada en el extremo inferior"),
            ("$f(b)$", "Función evaluada en el extremo superior"),
            ("$x_r$", "Intersección de la recta secante con el eje $x$"),
        ],
        "La expresión es la ecuación de la recta que une $(a, f(a))$ y $(b, f(b))$ evaluada donde cruza "
        "el eje $x$ ($y = 0$). Ese valor reemplaza a uno de los extremos conservando el cambio de signo.\n",
    ),
    "Punto fijo": (
        "### 3. Fórmula general de Punto fijo\n",
        "$$x_{n+1} = g(x_n)$$\n",
        [
            ("$g(x)$", "Despeje de la ecuación, obtenido de $x = g(x)$"),
            ("$x_n$", "Aproximación actual"),
            ("$x_{n+1}$", "Nueva aproximación, resultado de evaluar $g$ en $x_n$"),
        ],
        "Cada iteración consiste en aplicar la misma regla: el valor obtenido al evaluar $g$ reemplaza al "
        "valor anterior. El punto fijo $x = g(x)$ corresponde a la raíz de la ecuación original.\n",
    ),
    "Newton-Raphson": (
        "### 3. Fórmula general de Newton-Raphson\n",
        "$$x_{n+1} = x_n - \\frac{f(x_n)}{f'(x_n)}$$\n",
        [
            ("$x_n$", "Valor actual de la aproximación"),
            ("$f(x_n)$", "Función evaluada en $x_n$"),
            ("$f'(x_n)$", "Derivada evaluada en $x_n$"),
            ("$x_{n+1}$", "Nueva aproximación (mejor que $x_n$)"),
        ],
        "En cada paso, la fórmula toma el valor actual, le resta el cociente entre la función y su derivada, "
        "y produce una nueva aproximación más cercana a la raíz.\n",
    ),
    "Secante": (
        "### 3. Fórmula general de la Secante\n",
        "$$x_{n+1} = x_n - \\frac{f(x_n)\\,(x_n - x_{n-1})}{f(x_n) - f(x_{n-1})}$$\n",
        [
            ("$x_{n-1}$", "Penúltima aproximación"),
            ("$x_n$", "Aproximación actual"),
            ("$f(x_{n-1})$", "Función evaluada en $x_{n-1}$"),
            ("$f(x_n)$", "Función evaluada en $x_n$"),
            ("$x_{n+1}$", "Nueva aproximación"),
        ],
        "El cociente $\\dfrac{f(x_n) - f(x_{n-1})}{x_n - x_{n-1}}$ es la pendiente de la recta secante, "
        "que reemplaza a la derivada de Newton-Raphson. Así, el método no necesita la derivada simbólica.\n",
    ),
    "Müller": (
        "### 3. Fórmula general de Müller\n",
        "$$P(x) = a\\,(x - x_2)^2 + b\\,(x - x_2) + c \\qquad c = f(x_2)$$\n"
        "$$x_3 = x_2 - \\frac{2c}{b \\pm \\sqrt{b^2 - 4ac}}$$\n",
        [
            ("$x_0, x_1, x_2$", "Tres aproximaciones distintas"),
            ("$a, b, c$", "Coeficientes de la parábola interpoladora"),
            ("$b^2 - 4ac$", "Discriminante de la ecuación cuadrática"),
            ("$x_3$", "Nueva aproximación (puede ser compleja)"),
        ],
        "Los coeficientes se obtienen haciendo que la parábola pase por los tres puntos. Para evitar "
        "cancelaciones numéricas se elige el signo del denominador con mayor valor absoluto.\n",
    ),
}


def _seccion_formula_general(metodo="Newton-Raphson"):
    titulo, latex, tabla, nota = _FORMULAS.get(metodo, _FORMULAS["Newton-Raphson"])
    bloques = [titulo, latex]
    bloques.append("**Significado de cada elemento:**\n")
    bloques.append("| Símbolo | Significado |")
    bloques.append("|---------|-------------|")
    for simbolo, descripcion in tabla:
        bloques.append(f"| {simbolo} | {descripcion} |")
    bloques.append("")
    bloques.append(nota)
    bloques.append("")
    return "\n".join(bloques)


def _seccion_error(filas, error_permitido, criterio, decimales,
                   clave="xi+1", clave_funcion="f(xi)", etiqueta="$x$"):
    bloques = []
    bloques.append("### 5. Cálculo del error\n")
    bloques.append("**Fórmula del error aproximado porcentual:**\n")
    bloques.append("$$E_a = \\left| \\frac{x_{\\text{nuevo}} - x_{\\text{anterior}}}{x_{\\text{nuevo}}} \\right| \\times 100$$\n")
    bloques.append(
        "Este error mide qué tanto cambió la aproximación de un paso al siguiente. "
        "Si el cambio es pequeño, significa que estamos estabilizándonos.\n"
    )

    if criterio == "error" and error_permitido is not None:
        bloques.append(f"El criterio de parada es: **error < {_valor_display(error_permitido, decimales)} %**.\n")
    else:
        bloques.append("El criterio de parada es: **número fijo de iteraciones**.\n")

    if not filas:
        bloques.append("No hubo iteraciones, por lo que no se calcularon errores.\n")
        return "\n".join(bloques)

    bloques.append("**Errores en cada iteración:**\n")
    bloques.append(f"| Iteración | {etiqueta} nuevo | Error ($E_a$) | Estado |")
    bloques.append("|-----------|-----------|---------------|--------|")

    for i, fila in enumerate(filas):
        numero = fila["i"]
        xn1 = fila.get(clave)
        ea = fila["Ea (%)"]
        xn1_fmt = _formatear(xn1, decimales)
        valor_funcion = fila.get(clave_funcion)

        if isinstance(ea, float) and math.isfinite(ea):
            ea_fmt = f"{ea:.{decimales}f} %"
            if criterio == "error" and error_permitido is not None and i > 0 and ea < error_permitido:
                estado = "✅ Error alcanzado"
            elif ea == 0.0 and valor_funcion == 0:
                estado = "✅ Raíz exacta"
            else:
                estado = "⏳ Continúa"
        else:
            ea_fmt = "No disponible"
            estado = "⏳ Continúa"

        bloques.append(f"| {numero} | {xn1_fmt} | {ea_fmt} | {estado} |")

    bloques.append("")

    if criterio == "error" and error_permitido is not None and filas:
        ultimo_error = filas[-1]["Ea (%)"]
        if isinstance(ultimo_error, float) and math.isfinite(ultimo_error):
            if ultimo_error < error_permitido:
                bloques.append(
                    f"**Conclusión:** El error de la última iteración ({ultimo_error:.{decimales}f} %) "
                    f"es **menor** que el error permitido ({_valor_display(error_permitido, decimales)} %), "
                    "por lo que el método detuvo el cálculo.\n"
                )
            else:
                bloques.append(
                    f"**Conclusión:** El error de la última iteración ({ultimo_error:.{decimales}f} %) "
                    f"**no alcanzó** el criterio de {_valor_display(error_permitido, decimales)} %, por lo que "
                    "se detuvo por llegar al máximo de iteraciones.\n"
                )

    return "\n".join(bloques)


def _seccion_convergencia(resultado, filas, error_permitido, criterio, decimales, metodo=None):
    bloques = []
    bloques.append("### 7. Análisis de convergencia\n")

    if not filas:
        bloques.append(
            "No se realizaron iteraciones. El método encontró una raíz directamente "
            "o no pudo ejecutar ningún paso.\n"
        )
        return "\n".join(bloques)

    errores = []
    for fila in filas:
        ea = fila["Ea (%)"]
        if isinstance(ea, (int, float)) and math.isfinite(ea):
            errores.append(ea)

    if resultado.convergio is True:
        bloques.append(
            "El método **convergió** exitosamente. Las aproximaciones se estabilizaron "
            "y el error disminuyó hasta alcanzar el criterio de parada.\n"
        )
        if len(errores) >= 2:
            errores_mayores = sum(1 for i in range(1, len(errores)) if errores[i] < errores[i - 1])
            total_comparables = len(errores) - 1
            if total_comparables > 0 and errores_mayores == total_comparables:
                bloques.append(
                    "Los errores disminuyeron **en cada iteración**, lo cual confirma una "
                    "convergencia monotónica y estable.\n"
                )
            elif errores_mayores > total_comparables / 2:
                bloques.append(
                    "Los errores **en general disminuyeron**, aunque con algunas oscilaciones.\n"
                )
            else:
                bloques.append(
                    "Los errores **no siempre disminuyeron**, pero el método logró converger.\n"
                )
        if errores:
            bloques.append(
                f"El error comenzó en **{errores[0]:.{decimales}f} %** y terminó en "
                f"**{errores[-1]:.{decimales}f} %**.\n"
            )
    elif resultado.convergio is False:
        bloques.append(
            "El método **no convergió** dentro del máximo de iteraciones permitidas.\n"
        )
        if len(errores) >= 2:
            if errores[-1] < errores[0]:
                bloques.append(
                    "Aunque el error disminuyó respecto al inicio, no se alcanzó "
                    f"el criterio de {_valor_display(error_permitido, decimales)} % en el número de "
                    "iteraciones disponibles.\n"
                )
            else:
                bloques.append(
                    "El error no mostró una tendencia clara de disminución, lo que sugiere "
                    "que la función o los valores iniciales pueden no ser adecuados para este método.\n"
                )
        if errores:
            bloques.append(
                f"El error final fue **{errores[-1]:.{decimales}f} %**.\n"
            )
    else:
        bloques.append(
            "Se completaron las iteraciones solicitadas. El método finalizó con "
            f"**{len(filas)} pasos**."
        )
        if errores:
            bloques.append(f" El error aproximado final fue **{errores[-1]:.{decimales}f} %**.")
        bloques.append("\n")

    bloques.append("")
    return "\n".join(bloques)


def _seccion_resultado_final(resultado, expresion, decimales, metodo="Newton-Raphson",
                             criterio=None, parametros=None, numero_iteraciones=None):
    bloques = []
    raiz = resultado.raiz
    raiz_fmt = _formatear(raiz, decimales)
    error_fmt = _formatear(resultado.error_final, decimales)

    bloques.append("### 8. Resultado final\n")
    bloques.append(f"**Raíz aproximada:** $x = {raiz_fmt}$\n")
    bloques.append(f"**Última aproximación:** $x = {raiz_fmt}$\n")
    if numero_iteraciones is None:
        numero_iteraciones = len(resultado.iteraciones)
    bloques.append(f"**Número de iteraciones realizadas:** {numero_iteraciones}\n")
    bloques.append(f"**Error aproximado final:** {error_fmt} %\n")

    residuo_fmt = "No disponible"
    residuo = _evaluar_expresion(expresion, raiz) if expresion is not None else None
    if residuo is not None and _es_finito(residuo):
        residuo_fmt = _formatear(residuo, decimales)
        bloques.append(f"**Verificación:** $f({raiz_fmt}) = {residuo_fmt}$\n")
        if _cerca_de_cero(residuo, decimales):
            bloques.append(
                "El valor $f(x)$ es **cero o suficientemente cercano a cero**, "
                "lo que confirma que la raíz encontrada es **válida**.\n"
            )
        else:
            bloques.append(
                "El valor $f(x)$ no es exactamente cero; puede ser una aproximación razonable "
                "según la precisión utilizada o indicar que se detuvo por iteraciones fijas.\n"
            )
    elif expresion is not None:
        bloques.append("No fue posible evaluar la función en la raíz encontrada.\n")

    bloques.append(f"**Residuo $|f(x)|$:** {residuo_fmt}\n")

    if criterio == "error":
        bloques.append("**Criterio de parada utilizado:** error porcentual permitido.\n")
    elif criterio == "fijo":
        bloques.append("**Criterio de parada utilizado:** número fijo de iteraciones.\n")

    bloques.append(f"**Motivo reportado por el método:** {resultado.motivo}\n")

    bloques.append("**¿Por qué terminó el método?**\n")
    if resultado.convergio is True:
        bloques.append(
            "- Porque se cumplió el criterio de parada y el método reportó **convergencia**.\n"
        )
    elif resultado.convergio is False:
        bloques.append(
            "- Porque se alcanzó el **máximo de iteraciones** sin cumplir el criterio de error; "
            "el método reporta que **no convergió**.\n"
        )
        bloques.append(
            "- Esto no significa que el método sea incorrecto; puede necesitar más iteraciones, "
            "mejores valores iniciales o una función con mejores condiciones.\n"
        )
    else:
        bloques.append(
            "- Se completaron las iteraciones fijas solicitadas; **no se afirma convergencia**, "
            "solo que el número de pasos pedido fue ejecutado.\n"
        )

    bloques.append("")
    return "\n".join(bloques)


def _seccion_sin_iteraciones(metodo, expresion, resultado, parametros, decimales):
    parametros = parametros or {}
    bloques = ["### 4. Sin iteraciones: raíz detectada en los datos iniciales\n"]
    bloques.append(
        "El método no necesitó iterar porque detectó una raíz (o un final inmediato) en los datos "
        "iniciales. A continuación se comprueba matemáticamente.\n"
    )
    bloques.append(f"**Motivo reportado por el método:** {resultado.motivo}\n")

    raiz = resultado.raiz
    raiz_fmt = _formatear(raiz, decimales)
    bloques.append(f"**Valor identificado como raíz:** $x = {raiz_fmt}$\n")

    valor = _evaluar_expresion(expresion, raiz) if expresion is not None else None
    if valor is not None and _es_finito(valor):
        valor_fmt = _formatear(valor, decimales)
        if expresion is not None:
            sust = _expresion_con_valor(str(expresion), raiz, decimales)
            bloques.append(f"$$f({raiz_fmt}) = {sust}$$\n")
        bloques.append(f"$$f({raiz_fmt}) = {valor_fmt}$$\n")
        if _cerca_de_cero(valor, decimales):
            bloques.append(
                "Como $f$ evaluada en ese punto es prácticamente cero, se confirma que el dato "
                "inicial **ya es una raíz**.\n"
            )
        else:
            bloques.append(
                "El valor de $f$ en ese punto no es exactamente cero; revise la precisión o los "
                "parámetros ingresados.\n"
            )
    else:
        bloques.append("No fue posible evaluar la función en ese punto.\n")

    bloques.append("")
    return "\n".join(bloques)
def validar_estado_explicacion(expresion=None, filas=None, resultado=None, parametros=None, funcion_texto=None):
    problemas = []
    if expresion is None: problemas.append('expresion')
    if not filas: problemas.append('filas')
    if resultado is None or (hasattr(resultado, '__len__') and len(resultado) == 0 and not isinstance(resultado, str)): problemas.append('resultado')
    if not parametros: problemas.append('parametros')
    if not funcion_texto: problemas.append('funcion_texto')
    return problemas

