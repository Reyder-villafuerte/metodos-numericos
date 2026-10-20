"""Interfaz Streamlit del método iterativo de Gauss-Seidel (Unidad 2).

Toda la matemática se calcula en ``metodos.gauss_seidel``; este módulo solo
recoge los datos del estudiante y presenta el resultado en seis pestañas:
Resumen, Resultados, Matrices y operaciones, Explicación paso a paso,
Comprobación y Gráficas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from .componentes_resultados import mostrar_matriz, mostrar_vector
from .graficas_gauss_seidel import (
    figura_convergencia_incognitas,
    figura_evolucion_error,
    figura_evolucion_residuo,
    puede_usar_log,
)
from .metodos.gauss_seidel import (
    CRITERIOS_GAUSS_SEIDEL,
    REORDENACIONES,
    ErrorGaussSeidel,
    ResultadoGaussSeidel,
    analizar_dominancia,
    diagonal_nula,
    resolver_gauss_seidel_detallado,
)
from .presentacion import dataframe_matriz, ecuacion_latex, etiqueta_variable, filas_comprobacion


# Ejercicio de la exposición: 10x₁ − x₂ + 2x₃ = 6; −x₁ + 11x₂ − x₃ = 25; 2x₁ − x₂ + 10x₃ = −11
EJEMPLO_GAUSS_SEIDEL = {
    "A": [[10.0, -1.0, 2.0], [-1.0, 11.0, -1.0], [2.0, -1.0, 10.0]],
    "b": [6.0, 25.0, -11.0],
    "x0": [0.0, 0.0, 0.0],
    "tolerancia": "0.001",
    "max_iter": 50,
    "criterio": "absoluto",
    "origen": (
        "Ejercicio de exposición: 10x₁ − x₂ + 2x₃ = 6 · −x₁ + 11x₂ − x₃ = 25 · "
        "2x₁ − x₂ + 10x₃ = −11, con X⁽⁰⁾ = [0, 0, 0]ᵀ y tolerancia 0.001."
    ),
}

CLAVES_RESULTADO_GS = ("gs_resultado", "gs_error", "gs_iter_sel")
COLOR_NUEVO = "#c4b5fd"  # morado claro: valores ya actualizados en la iteración k+1


# ---------------------------------------------------------------------------
# Formato numérico (solo presentación; nunca se redondean los cálculos)
# ---------------------------------------------------------------------------

def _num(valor: float, decimales: int) -> str:
    texto = f"{float(valor):.{decimales}f}"
    if float(texto) == 0:
        texto = f"{0.0:.{decimales}f}"
    return texto


def _par(valor: float, decimales: int, color: str | None = None) -> str:
    """Número entre paréntesis para LaTeX; opcionalmente coloreado."""

    texto = _num(valor, decimales)
    if color:
        texto = rf"\color{{{color}}}{{{texto}}}"
    return rf"\left({texto}\right)"


def _cientifico(valor: float | None, cifras: int = 4) -> str:
    """Notación científica en LaTeX: 3.0731 × 10^{-4}."""

    if valor is None:
        return r"\text{no definido}"
    if valor == 0:
        return "0"
    mantisa, exponente = f"{valor:.{cifras}e}".split("e")
    exponente_int = int(exponente)
    if -3 <= exponente_int <= 3:
        return f"{valor:.{cifras + 2}g}"
    return rf"{mantisa}\times 10^{{{exponente_int}}}"


def _texto_error(valor: float | None) -> str:
    return "no definido" if valor is None else f"{valor:.6e}"


def _vector_latex(vector, decimales: int, nombre: str | None = None) -> str:
    cuerpo = r"\begin{bmatrix}" + r" \\ ".join(_num(v, decimales) for v in vector) + r"\end{bmatrix}"
    return f"{nombre}={cuerpo}" if nombre else cuerpo


def _vector_fila_latex(vector, decimales: int) -> str:
    return r"\left[" + r",\ ".join(_num(v, decimales) for v in vector) + r"\right]^{T}"


def _matriz_latex(matriz, decimales: int) -> str:
    filas = [" & ".join(_num(v, decimales) for v in fila) for fila in np.asarray(matriz, dtype=float)]
    return r"\begin{bmatrix}" + r" \\ ".join(filas) + r"\end{bmatrix}"


# ---------------------------------------------------------------------------
# Estado del formulario
# ---------------------------------------------------------------------------

def limpiar_resultado_gauss_seidel() -> None:
    for clave in CLAVES_RESULTADO_GS:
        st.session_state.pop(clave, None)


def _dataframes(A, b, x0) -> tuple[pd.DataFrame, pd.DataFrame]:
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    indice = [f"Ecuación {i}" for i in range(1, n + 1)]
    columnas = [f"x{i}" for i in range(1, n + 1)]
    return (
        pd.DataFrame(A, index=indice, columns=columnas),
        pd.DataFrame({"b": np.asarray(b, dtype=float), "x0": np.asarray(x0, dtype=float)}, index=indice),
    )


def _establecer(A, b, x0, origen: str) -> None:
    st.session_state.gs_A_base, st.session_state.gs_bx_base = _dataframes(A, b, x0)
    st.session_state.gs_n = int(np.asarray(A).shape[0])
    st.session_state.gs_editor_version = st.session_state.get("gs_editor_version", 0) + 1
    st.session_state.gs_origen = origen
    limpiar_resultado_gauss_seidel()


def _nuevo_sistema() -> None:
    n = int(st.session_state.get("gs_n", 3))
    _establecer(np.eye(n), np.zeros(n), np.zeros(n), "Sistema nuevo: A inicializada como identidad, b = 0 y X⁽⁰⁾ = 0.")


def _cargar_ejemplo() -> None:
    ejemplo = EJEMPLO_GAUSS_SEIDEL
    _establecer(ejemplo["A"], ejemplo["b"], ejemplo["x0"], ejemplo["origen"])
    st.session_state.gs_tol = ejemplo["tolerancia"]
    st.session_state.gs_max = ejemplo["max_iter"]
    st.session_state.gs_criterio = ejemplo["criterio"]
    st.session_state.gs_resolver_auto = True


def _inicializar_estado() -> None:
    st.session_state.setdefault("gs_n", 3)
    st.session_state.setdefault("gs_editor_version", 0)
    st.session_state.setdefault("gs_tol", "0.001")
    st.session_state.setdefault("gs_max", 50)
    st.session_state.setdefault("gs_criterio", "absoluto")
    st.session_state.setdefault("gs_reordenar", "si_hay_ceros")
    st.session_state.setdefault("gs_decimales", 6)
    n = int(st.session_state.gs_n)
    if "gs_A_base" not in st.session_state or st.session_state.gs_A_base.shape != (n, n):
        st.session_state.gs_A_base, st.session_state.gs_bx_base = _dataframes(np.eye(n), np.zeros(n), np.zeros(n))
        st.session_state.gs_origen = "Sistema nuevo: A inicializada como identidad, b = 0 y X⁽⁰⁾ = 0."


def _resolver(A, b, x0) -> None:
    try:
        st.session_state.gs_resultado = resolver_gauss_seidel_detallado(
            A,
            b,
            x0,
            tolerancia=str(st.session_state.gs_tol).strip().replace(",", "."),
            max_iter=st.session_state.gs_max,
            criterio=st.session_state.gs_criterio,
            reordenar=st.session_state.gs_reordenar,
        )
        st.session_state.pop("gs_error", None)
    except ErrorGaussSeidel as exc:
        st.session_state.pop("gs_resultado", None)
        st.session_state.gs_error = str(exc)
    except Exception:  # pragma: no cover - salvaguarda de interfaz
        st.session_state.pop("gs_resultado", None)
        st.session_state.gs_error = "No fue posible completar el cálculo por un error numérico inesperado."


# ---------------------------------------------------------------------------
# Formulario
# ---------------------------------------------------------------------------

def _mostrar_formulario() -> None:
    _inicializar_estado()
    st.markdown('<div class="step-label">Paso 1 · Datos del sistema</div>', unsafe_allow_html=True)
    st.subheader("Configure el sistema de ecuaciones")

    with st.container(horizontal=True):
        st.button("✨ Cargar ejercicio de ejemplo", key="gs_cargar_ejemplo", on_click=_cargar_ejemplo)
        st.button("↻ Nuevo sistema", key="gs_nuevo_sistema", on_click=_nuevo_sistema)

    st.selectbox(
        "Número de incógnitas",
        list(range(2, 9)),
        key="gs_n",
        on_change=_nuevo_sistema,
        help="Sistemas cuadrados desde 2×2 hasta 8×8.",
    )
    st.caption(st.session_state.get("gs_origen", ""))

    version = st.session_state.gs_editor_version
    n = int(st.session_state.gs_n)
    columnas_A = {
        f"x{i}": st.column_config.NumberColumn(etiqueta_variable(i), format="%.8g", required=True)
        for i in range(1, n + 1)
    }
    st.markdown("#### Matriz de coeficientes A")
    A_editada = st.data_editor(
        st.session_state.gs_A_base,
        key=f"gs_A_editor_{version}",
        num_rows="fixed",
        column_config=columnas_A,
        on_change=limpiar_resultado_gauss_seidel,
        width="stretch",
    )
    st.markdown("#### Vector independiente b y vector inicial X⁽⁰⁾")
    bx_editado = st.data_editor(
        st.session_state.gs_bx_base,
        key=f"gs_bx_editor_{version}",
        num_rows="fixed",
        column_config={
            "b": st.column_config.NumberColumn("b", format="%.8g", required=True),
            "x0": st.column_config.NumberColumn("X⁽⁰⁾", format="%.8g", required=True),
        },
        on_change=limpiar_resultado_gauss_seidel,
        width="stretch",
    )

    st.markdown("#### Parámetros del método")
    cols = st.columns(2)
    cols[0].text_input(
        "Tolerancia",
        key="gs_tol",
        on_change=limpiar_resultado_gauss_seidel,
        help="Número positivo, por ejemplo 0.001 o 1e-6.",
    )
    cols[1].number_input(
        "Máximo de iteraciones",
        min_value=1,
        max_value=1000,
        step=1,
        key="gs_max",
        on_change=limpiar_resultado_gauss_seidel,
    )
    cols = st.columns(2)
    cols[0].selectbox(
        "Criterio de error (parada)",
        list(CRITERIOS_GAUSS_SEIDEL),
        format_func=CRITERIOS_GAUSS_SEIDEL.get,
        key="gs_criterio",
        on_change=limpiar_resultado_gauss_seidel,
        help="El método se detiene cuando el valor del criterio es menor o igual que la tolerancia.",
    )
    cols[1].selectbox(
        "Reordenación de ecuaciones",
        list(REORDENACIONES),
        format_func=REORDENACIONES.get,
        key="gs_reordenar",
        on_change=limpiar_resultado_gauss_seidel,
        help="Intercambiar ecuaciones no cambia la solución, pero sí la diagonal que usa el método.",
    )
    st.select_slider(
        "Decimales para mostrar",
        options=[2, 3, 4, 5, 6, 8, 10],
        key="gs_decimales",
        help="Solo afecta la presentación. Los cálculos internos usan precisión completa.",
    )

    A, b, x0 = None, None, None
    try:
        A = A_editada.to_numpy(dtype=float)
        bx = bx_editado.to_numpy(dtype=float)
        b, x0 = bx[:, 0], bx[:, 1]
        if not (np.isfinite(A).all() and np.isfinite(bx).all()):
            raise ValueError
        st.markdown("#### Sistema ingresado")
        st.latex(
            r"\begin{cases}"
            + r" \\ ".join(ecuacion_latex(fila, termino) for fila, termino in zip(A, b))
            + r"\end{cases}"
        )
        ceros = diagonal_nula(A)
        _, dominante = analizar_dominancia(A)
        if ceros:
            posiciones = ", ".join(f"a{i + 1}{i + 1}" for i in ceros)
            st.warning(
                f"La diagonal contiene ceros ({posiciones}). Gauss-Seidel divide entre aᵢᵢ, "
                "así que será necesario reordenar las ecuaciones.",
                icon=":material/warning:",
            )
        elif not dominante:
            st.info(
                "La matriz no es estrictamente diagonalmente dominante en este orden. "
                "El método puede converger igualmente; puede elegir «Buscar un orden "
                "diagonalmente dominante» para intentar mejorar la convergencia.",
                icon=":material/info:",
            )
    except (TypeError, ValueError):
        A = None
        st.warning("Complete todas las celdas de A, b y X⁽⁰⁾ con valores numéricos.", icon=":material/warning:")

    pulsado = st.button("Resolver sistema", type="primary", width="stretch", key="gs_resolver")
    if pulsado or st.session_state.pop("gs_resolver_auto", False):
        if A is None:
            st.session_state.pop("gs_resultado", None)
            st.session_state.gs_error = "Todos los valores de A, b y X⁽⁰⁾ deben ser numéricos; hay celdas vacías o inválidas."
        else:
            _resolver(A, b, x0)


# ---------------------------------------------------------------------------
# Pestañas de resultados
# ---------------------------------------------------------------------------

def _aviso_reordenacion(resultado: ResultadoGaussSeidel) -> None:
    if not resultado.hubo_reordenacion:
        return
    cambios = " · ".join(
        f"fila {nueva + 1} ← ecuación {original + 1}"
        for nueva, original in enumerate(resultado.permutacion)
        if nueva != original
    )
    st.warning(
        "Se reordenaron las ecuaciones para obtener una diagonal adecuada "
        f"({cambios}). La solución del sistema no cambia; las incógnitas conservan su orden.",
        icon=":material/swap_vert:",
    )


def _tab_resumen(resultado: ResultadoGaussSeidel, d: int) -> None:
    with st.container(horizontal=True):
        st.metric("Incógnitas", len(resultado.x), border=True)
        st.metric("Iteraciones", resultado.iteraciones, border=True)
        st.metric("Residuo máximo", f"{resultado.norma_residuo:.3e}", border=True,
                  help="‖AX − b‖∞ evaluado en la última aproximación.")
        st.metric("Convergencia", "Convergió" if resultado.convergio else "No convergió", border=True)

    if resultado.convergio:
        st.success(
            "El método de Gauss-Seidel alcanzó el criterio de parada configurado y se comprobó el residuo del sistema.",
            icon=":material/check_circle:",
        )
    else:
        st.error(
            "El método no alcanzó el criterio de parada dentro del máximo de iteraciones."
            if "iteraciones permitidas" in resultado.motivo
            else "El método no alcanzó el criterio de parada: " + resultado.motivo,
            icon=":material/cancel:",
        )
    st.caption(resultado.motivo)
    _aviso_reordenacion(resultado)

    titulo = "Vector solución aproximado" if resultado.convergio else "Última aproximación (no es una solución convergente)"
    st.markdown(f"#### {titulo}")
    st.latex(rf"X^{{({resultado.iteraciones})}}={_vector_latex(resultado.x, d)}")
    st.dataframe(
        pd.DataFrame(
            {
                "Incógnita": [etiqueta_variable(i) for i in range(1, len(resultado.x) + 1)],
                "Valor aproximado": resultado.x,
            }
        ),
        hide_index=True,
        column_config={"Valor aproximado": st.column_config.NumberColumn(format=f"%.{d}f")},
        width="stretch",
    )
    with st.container(horizontal=True):
        st.metric("Error final", _texto_error(resultado.error), border=True,
                  help=CRITERIOS_GAUSS_SEIDEL[resultado.criterio])
        st.metric("Tolerancia", f"{resultado.tolerancia:g}", border=True)
        st.metric("Criterio", resultado.criterio.capitalize(), border=True,
                  help=CRITERIOS_GAUSS_SEIDEL[resultado.criterio])


def _tabla_iteraciones(resultado: ResultadoGaussSeidel) -> pd.DataFrame:
    n = len(resultado.x)
    filas = [
        {"k": 0, **{etiqueta_variable(i + 1): resultado.x0[i] for i in range(n)},
         "‖ΔX‖∞": None, "Error relativo": None, "Residuo ‖AX−b‖∞": resultado.residuo_inicial,
         "Estado": "Inicial"}
    ]
    for it in resultado.historial_detallado:
        ultima = it.k == resultado.iteraciones
        filas.append(
            {
                "k": it.k,
                **{etiqueta_variable(i + 1): it.x[i] for i in range(n)},
                "‖ΔX‖∞": it.norma_cambio,
                "Error relativo": it.error_relativo,
                "Residuo ‖AX−b‖∞": it.residuo,
                "Estado": ("★ Final · convergió" if resultado.convergio else "★ Última · no convergió") if ultima else "",
            }
        )
    return pd.DataFrame(filas)


def _tab_resultados(resultado: ResultadoGaussSeidel, d: int) -> None:
    st.markdown("### Tabla de iteraciones de Gauss-Seidel")
    st.caption(
        f"Criterio de parada: {CRITERIOS_GAUSS_SEIDEL[resultado.criterio]} ≤ {resultado.tolerancia:g}. "
        "Los valores se muestran redondeados; los cálculos internos no se redondean."
    )
    tabla = _tabla_iteraciones(resultado)
    configuracion = {
        etiqueta_variable(i + 1): st.column_config.NumberColumn(format=f"%.{d}f")
        for i in range(len(resultado.x))
    }
    configuracion |= {
        "k": st.column_config.NumberColumn("Iteración k", format="%d"),
        "‖ΔX‖∞": st.column_config.NumberColumn(format="%.6e"),
        "Error relativo": st.column_config.NumberColumn(format="%.6e"),
        "Residuo ‖AX−b‖∞": st.column_config.NumberColumn(format="%.6e"),
    }
    st.dataframe(tabla, hide_index=True, column_config=configuracion, width="stretch")

    with st.container(horizontal=True):
        st.metric("Tolerancia", f"{resultado.tolerancia:g}", border=True)
        st.metric("Iteraciones totales", resultado.iteraciones, border=True)
        st.metric("Resultado", "Convergió" if resultado.convergio else "No convergió", border=True)

    with st.container(border=True):
        st.markdown("**Última aproximación**" + ("" if resultado.convergio else " · no convergente"))
        st.latex(rf"X^{{({resultado.iteraciones})}}={_vector_fila_latex(resultado.x, d)}")

    with st.expander("Errores por componente en cada iteración"):
        n = len(resultado.x)
        filas = []
        for it in resultado.historial_detallado:
            fila = {"k": it.k}
            for i in range(n):
                fila[f"|Δ{etiqueta_variable(i + 1)}|"] = it.errores_absolutos[i]
                fila[f"εᵣ {etiqueta_variable(i + 1)}"] = it.errores_relativos[i]
            filas.append(fila)
        st.dataframe(
            pd.DataFrame(filas),
            hide_index=True,
            column_config={c: st.column_config.NumberColumn(format="%.6e") for c in pd.DataFrame(filas).columns if c != "k"},
            width="stretch",
        )
        st.caption("εᵣ = |xᵢ⁽ᵏ⁾ − xᵢ⁽ᵏ⁻¹⁾| / |xᵢ⁽ᵏ⁾|; se deja vacío cuando xᵢ⁽ᵏ⁾ = 0 (no definido).")


def _tab_matrices(resultado: ResultadoGaussSeidel, d: int) -> None:
    n = len(resultado.x)
    if resultado.hubo_reordenacion:
        st.markdown("#### Sistema original (antes de reordenar)")
        cols = st.columns(2)
        mostrar_matriz(cols[0], resultado.A_original, "A original")
        mostrar_vector(cols[1], resultado.b_original, "b original")
        _aviso_reordenacion(resultado)
        st.markdown("#### Sistema reordenado usado por el método")

    cols = st.columns([3, 1, 1])
    mostrar_matriz(cols[0], resultado.A, "Matriz A")
    mostrar_vector(cols[1], resultado.b, "b")
    mostrar_vector(cols[2], resultado.x0, "X⁽⁰⁾")

    variables = r"\begin{bmatrix}" + r" \\ ".join(f"x_{{{i}}}" for i in range(1, n + 1)) + r"\end{bmatrix}"
    st.markdown("#### Sistema AX = b")
    st.latex(f"{_matriz_latex(resultado.A, d)}{variables}={_vector_latex(resultado.b, d)}")

    st.markdown("#### Descomposición A = L + D + U")
    st.write(
        "Se usa la convención aditiva: **D** contiene la diagonal de A, **L** la parte estrictamente "
        "inferior y **U** la parte estrictamente superior (sin cambiar signos)."
    )
    cols = st.columns(3)
    for col, nombre, matriz in zip(cols, ("D", "L", "U"), (resultado.D, resultado.L, resultado.U)):
        mostrar_matriz(col, matriz, nombre, columnas_variables=False, filas_ecuaciones=False)

    st.markdown("#### Forma matricial de la iteración")
    st.latex(r"(D+L)\,X^{(k+1)} = b - U\,X^{(k)}")
    st.latex(r"X^{(k+1)} = \underbrace{-(D+L)^{-1}U}_{T_{GS}}\,X^{(k)} + \underbrace{(D+L)^{-1}b}_{c}")
    if resultado.matriz_iteracion is not None:
        cols = st.columns([3, 1])
        mostrar_matriz(cols[0], resultado.matriz_iteracion, "Matriz de iteración T_GS", columnas_variables=False, filas_ecuaciones=False)
        mostrar_vector(cols[1], resultado.vector_constante, "c")
        st.caption(
            "La forma matricial es equivalente al cálculo componente a componente: "
            "resolver con la matriz triangular D+L es exactamente usar los valores nuevos en cuanto se obtienen."
        )
    else:
        st.info("No fue posible construir T_GS porque D+L no es invertible numéricamente.")

    st.markdown("#### Condiciones de convergencia")
    filas = [
        {
            "Fila": f["fila"],
            "|aᵢᵢ|": f["diagonal"],
            "Σ |aᵢⱼ| (j ≠ i)": f["suma_resto"],
            "|aᵢᵢ| > Σ|aᵢⱼ|": "Sí" if f["estricta"] else "No",
        }
        for f in resultado.dominancia
    ]
    st.dataframe(
        pd.DataFrame(filas),
        hide_index=True,
        column_config={
            "|aᵢᵢ|": st.column_config.NumberColumn(format=f"%.{d}g"),
            "Σ |aᵢⱼ| (j ≠ i)": st.column_config.NumberColumn(format=f"%.{d}g"),
        },
        width="stretch",
    )
    if resultado.estrictamente_dominante:
        st.success(
            "A es estrictamente diagonalmente dominante por filas: Gauss-Seidel converge para cualquier X⁽⁰⁾.",
            icon=":material/check_circle:",
        )
    else:
        st.warning(
            "A no es estrictamente diagonalmente dominante. Esto no implica divergencia: "
            "la condición decisiva es el radio espectral de T_GS.",
            icon=":material/warning:",
        )
    st.caption(
        "La dominancia diagonal estricta es una condición suficiente de convergencia, pero no necesaria: "
        "existen matrices no dominantes para las que el método converge."
    )

    if resultado.radio_espectral is not None:
        st.latex(rf"\rho(T_{{GS}})=\max_i |\lambda_i| = {resultado.radio_espectral:.{max(d, 6)}f}")
        if resultado.radio_espectral < 1:
            st.success(
                "ρ(T_GS) < 1: la iteración converge para cualquier vector inicial (condición necesaria y suficiente). "
                "Cuanto menor es ρ, más rápida es la convergencia.",
                icon=":material/check_circle:",
            )
        else:
            st.error(
                "ρ(T_GS) ≥ 1: la iteración no converge en general (solo podría hacerlo para vectores iniciales particulares).",
                icon=":material/cancel:",
            )
        with st.expander("Valores propios de T_GS"):
            st.dataframe(
                pd.DataFrame(
                    {
                        "λ": [f"{v.real:.{d}f}" + (f" {'+' if v.imag >= 0 else '−'} {abs(v.imag):.{d}f}i" if abs(v.imag) > 1e-14 else "")
                              for v in resultado.valores_propios],
                        "|λ|": np.abs(resultado.valores_propios),
                    }
                ),
                hide_index=True,
                column_config={"|λ|": st.column_config.NumberColumn(format=f"%.{d}f")},
                width="stretch",
            )


def _formula_general(paso, k: int) -> str:
    i = paso.i + 1
    restas = "".join(
        rf" - a_{{{i}{t.j + 1}}}x_{{{t.j + 1}}}^{{({k if t.nuevo else k - 1})}}" for t in paso.terminos
    )
    return rf"x_{{{i}}}^{{({k})}} = \frac{{b_{{{i}}}{restas}}}{{a_{{{i}{i}}}}}"


def _sustitucion(paso, k: int, d: int) -> str:
    i = paso.i + 1
    restas = "".join(
        rf" - {_par(t.coeficiente, d)}{_par(t.valor, d, COLOR_NUEVO if t.nuevo else None)}"
        for t in paso.terminos
    )
    return rf"x_{{{i}}}^{{({k})}} = \frac{{{_num(paso.b_i, d)}{restas}}}{{{_num(paso.a_ii, d)}}}"


def _operaciones(paso, k: int, d: int) -> str:
    i = paso.i + 1
    restas = "".join(rf" - {_par(t.producto, d)}" for t in paso.terminos)
    return (
        rf"x_{{{i}}}^{{({k})}} = \frac{{{_num(paso.b_i, d)}{restas}}}{{{_num(paso.a_ii, d)}}}"
        rf" = \frac{{{_num(paso.numerador, d)}}}{{{_num(paso.a_ii, d)}}}"
    )


def _explicar_iteracion(resultado: ResultadoGaussSeidel, it, d: int) -> None:
    k = it.k
    st.markdown("**Valor de partida**")
    st.latex(rf"X^{{({k - 1})}} = {_vector_fila_latex(it.x_anterior, d)}")

    for paso in it.pasos:
        i = paso.i + 1
        with st.container(border=True):
            st.markdown(f"**Incógnita {etiqueta_variable(i)}**")
            nuevos = [etiqueta_variable(t.j + 1) for t in paso.terminos if t.nuevo]
            if nuevos:
                st.caption(
                    f"Se usan los valores ya actualizados en esta misma iteración: {', '.join(nuevos)}⁽{k}⁾ "
                    "(resaltados en morado). Esto es lo que distingue a Gauss-Seidel de Jacobi."
                )
            else:
                st.caption("Es la primera ecuación: todas las demás incógnitas provienen de la iteración anterior.")
            st.markdown("1. Fórmula general")
            st.latex(_formula_general(paso, k))
            st.markdown("2. Sustitución numérica")
            st.latex(_sustitucion(paso, k, d))
            st.markdown("3. Operaciones efectuadas")
            st.latex(_operaciones(paso, k, d))
            st.markdown("4. Resultado")
            st.latex(rf"x_{{{i}}}^{{({k})}} = {_num(paso.valor, d)}")
            st.markdown("5. Error de la componente")
            st.latex(
                rf"\left|x_{{{i}}}^{{({k})}} - x_{{{i}}}^{{({k - 1})}}\right| = "
                rf"\left|{_num(paso.valor, d)} - {_par(paso.valor_anterior, d)}\right| = {_cientifico(paso.error_absoluto)}"
            )
            if paso.error_relativo is not None:
                st.latex(
                    rf"\varepsilon_{{r,{i}}} = \frac{{\left|x_{{{i}}}^{{({k})}} - x_{{{i}}}^{{({k - 1})}}\right|}}"
                    rf"{{\left|x_{{{i}}}^{{({k})}}\right|}} = {_cientifico(paso.error_relativo)}"
                )

    st.markdown("**Vector actualizado y cálculo del error de la iteración**")
    st.latex(rf"X^{{({k})}} = {_vector_fila_latex(it.x, d)}")
    componentes = r",\ ".join(_cientifico(v) for v in it.errores_absolutos)
    st.latex(
        rf"\left\|X^{{({k})}} - X^{{({k - 1})}}\right\|_\infty = \max\left\{{{componentes}\right\}} = {_cientifico(it.norma_cambio)}"
    )
    if it.error_relativo is not None:
        st.latex(
            rf"\frac{{\left\|X^{{({k})}} - X^{{({k - 1})}}\right\|_\infty}}{{\left\|X^{{({k})}}\right\|_\infty}} = "
            rf"\frac{{{_cientifico(it.norma_cambio)}}}{{{_num(float(np.max(np.abs(it.x))), d)}}} = {_cientifico(it.error_relativo)}"
        )
    st.latex(rf"\left\|AX^{{({k})}} - b\right\|_\infty = {_cientifico(it.residuo)}")

    simbolo = CRITERIOS_GAUSS_SEIDEL[resultado.criterio]
    if it.error is not None and it.error <= resultado.tolerancia:
        st.success(
            f"{simbolo} = {it.error:.6e} ≤ {resultado.tolerancia:g} → se cumple el criterio y el método se detiene.",
            icon=":material/check_circle:",
        )
    elif k == resultado.iteraciones and not resultado.convergio:
        st.error(f"{simbolo} = {_texto_error(it.error)} > {resultado.tolerancia:g}. {resultado.motivo}", icon=":material/cancel:")
    else:
        st.info(
            f"{simbolo} = {_texto_error(it.error)} > {resultado.tolerancia:g} → se continúa con la iteración {k + 1}.",
            icon=":material/arrow_forward:",
        )


def _tab_paso_a_paso(resultado: ResultadoGaussSeidel, d: int) -> None:
    n = len(resultado.x)
    st.markdown("#### Fórmula del método")
    st.latex(
        r"x_i^{(k+1)}=\frac{b_i-\sum_{j<i}a_{ij}\,x_j^{(k+1)}-\sum_{j>i}a_{ij}\,x_j^{(k)}}{a_{ii}},"
        rf"\qquad i=1,\ldots,{n}"
    )
    st.write(
        "En cada iteración las incógnitas se calculan en orden. Para obtener xᵢ se usan los valores "
        "**nuevos** de x₁, …, xᵢ₋₁ (ya calculados en la misma iteración) y los valores **anteriores** "
        "de xᵢ₊₁, …, xₙ. Jacobi, en cambio, usaría solo valores de la iteración anterior."
    )
    _aviso_reordenacion(resultado)
    st.markdown("**Ecuaciones despejadas**")
    for i in range(n):
        restas = "".join(
            rf" - {_par(resultado.A[i, j], d)}x_{{{j + 1}}}^{{({'k+1' if j < i else 'k'})}}"
            for j in range(n) if j != i
        )
        st.latex(rf"x_{{{i + 1}}}^{{(k+1)}} = \frac{{{_num(resultado.b[i], d)}{restas}}}{{{_num(resultado.A[i, i], d)}}}")

    st.markdown("**Vector inicial**")
    st.latex(rf"X^{{(0)}} = {_vector_fila_latex(resultado.x0, d)}")

    modo = st.radio(
        "Visualización",
        ["Todas las iteraciones", "Una iteración"],
        horizontal=True,
        key="gs_modo_pasos",
    )
    if modo == "Una iteración" and resultado.iteraciones > 1:
        k = st.select_slider(
            "Iteración", options=list(range(1, resultado.iteraciones + 1)), key="gs_iter_sel"
        )
        st.markdown(f"### Iteración {k}")
        _explicar_iteracion(resultado, resultado.historial_detallado[k - 1], d)
    else:
        for it in resultado.historial_detallado:
            ultima = it.k == resultado.iteraciones
            with st.expander(f"Iteración {it.k}" + (" · última" if ultima else ""), expanded=it.k == 1):
                _explicar_iteracion(resultado, it, d)

    st.markdown("#### Conclusión")
    if resultado.convergio:
        st.success(
            f"Después de {resultado.iteraciones} iteraciones se obtiene X ≈ {_texto_vector(resultado.x, d)} "
            "como aproximación de la solución.",
            icon=":material/check_circle:",
        )
    else:
        st.error(
            f"Tras {resultado.iteraciones} iteraciones el método no cumplió el criterio de parada; "
            f"la última aproximación {_texto_vector(resultado.x, d)} no debe interpretarse como solución.",
            icon=":material/cancel:",
        )


def _texto_vector(vector, d: int) -> str:
    return "[" + ", ".join(_num(v, d) for v in vector) + "]ᵀ"


def _tab_comprobacion(resultado: ResultadoGaussSeidel, d: int) -> None:
    st.markdown("#### Comprobación AX ≈ b")
    st.write(
        "Se sustituye la última aproximación en el sistema. El producto AX debe parecerse a b; "
        "la diferencia r = AX − b es el **residuo**."
    )
    AX = resultado.comprobacion
    r = resultado.residuo_vector
    st.latex(
        rf"{_matriz_latex(resultado.A, d)}{_vector_latex(resultado.x, d)}={_vector_latex(AX, d)}"
        rf"\approx{_vector_latex(resultado.b, d)}"
    )
    cols = st.columns(4)
    mostrar_vector(cols[0], resultado.x, "X aproximado")
    mostrar_vector(cols[1], AX, "AX")
    mostrar_vector(cols[2], resultado.b, "b")
    mostrar_vector(cols[3], r, "r = AX − b")
    residuos_latex = r"\begin{bmatrix}" + r" \\ ".join(_cientifico(v) for v in r) + r"\end{bmatrix}"
    st.latex(rf"r = AX-b = {residuos_latex}")
    st.latex(rf"\|r\|_\infty = \max_i |r_i| = {_cientifico(resultado.norma_residuo)}")

    with st.container(horizontal=True):
        st.metric("Tolerancia de parada", f"{resultado.tolerancia:g}", border=True,
                  help="Umbral aplicado al criterio elegido entre iteraciones.")
        st.metric("Último valor del criterio", _texto_error(resultado.error), border=True,
                  help=CRITERIOS_GAUSS_SEIDEL[resultado.criterio])
        st.metric("‖AX − b‖∞", f"{resultado.norma_residuo:.6e}", border=True)
    st.info(
        "La tolerancia controla cuánto cambian las aproximaciones entre iteraciones (o el criterio elegido); "
        "el residuo mide cuánto deja de cumplirse cada ecuación. Son magnitudes distintas: un cambio pequeño "
        "entre iteraciones no garantiza por sí solo un residuo igual de pequeño.",
        icon=":material/functions:",
    )

    st.markdown("#### Sustitución en cada ecuación")
    for fila in filas_comprobacion(resultado.A, resultado.b, resultado.x):
        with st.container(border=True):
            st.markdown(f"**Ecuación {fila['ecuacion']}**")
            st.latex(fila["simbolica"])
            st.latex(fila["sustitucion"].rsplit("=", 1)[0] + rf"= {_num(fila['lado_izquierdo'], d)} \approx {_num(fila['lado_derecho'], d)}")
            st.caption(f"Residuo de la ecuación: {fila['residuo']:.6e}")

    try:
        referencia = np.linalg.solve(resultado.A, resultado.b)
        if np.linalg.cond(resultado.A) < 1e12:
            st.markdown("#### Comparación con una solución de referencia")
            st.caption("Referencia obtenida independientemente por eliminación gaussiana (numpy.linalg.solve).")
            st.dataframe(
                pd.DataFrame(
                    {
                        "Incógnita": [etiqueta_variable(i + 1) for i in range(len(referencia))],
                        "Gauss-Seidel": resultado.x,
                        "Referencia": referencia,
                        "|Diferencia|": np.abs(resultado.x - referencia),
                    }
                ),
                hide_index=True,
                column_config={
                    "Gauss-Seidel": st.column_config.NumberColumn(format=f"%.{d}f"),
                    "Referencia": st.column_config.NumberColumn(format=f"%.{d}f"),
                    "|Diferencia|": st.column_config.NumberColumn(format="%.3e"),
                },
                width="stretch",
            )
    except np.linalg.LinAlgError:
        st.caption("A es singular: no existe una solución de referencia única para comparar.")

    if resultado.convergio:
        st.caption(
            "La solución de Gauss-Seidel es una aproximación: el residuo es pequeño pero no nulo, "
            "por lo que no se presenta como solución exacta."
        )
    else:
        st.warning(
            "El método no convergió; el residuo anterior corresponde a la última aproximación calculada, "
            "que no es una solución del sistema.",
            icon=":material/warning:",
        )


def _tab_graficas(resultado: ResultadoGaussSeidel) -> None:
    config = {"displaylogo": False, "scrollZoom": True, "responsive": True}
    errores = [it.error for it in resultado.historial_detallado]
    residuos = [resultado.residuo_inicial] + [it.residuo for it in resultado.historial_detallado]
    logaritmica = st.toggle(
        "Escala logarítmica para error y residuo",
        value=True,
        key="gs_log",
        disabled=not (puede_usar_log(errores) or puede_usar_log(residuos)),
        help="Se desactiva automáticamente si algún valor es cero o negativo.",
    )
    with st.container(border=True):
        st.markdown("#### Gráfica 1 · Convergencia de las incógnitas")
        st.plotly_chart(figura_convergencia_incognitas(resultado), width="stretch", key="gs_fig_incognitas", config=config)
    with st.container(border=True):
        st.markdown("#### Gráfica 2 · Evolución del error")
        st.plotly_chart(figura_evolucion_error(resultado, logaritmica=logaritmica), width="stretch", key="gs_fig_error", config=config)
        st.caption("La línea discontinua es la tolerancia: el método se detiene en la primera iteración cuyo error queda por debajo de ella.")
    with st.container(border=True):
        st.markdown("#### Gráfica 3 · Evolución del residuo ‖AX − b‖∞")
        st.plotly_chart(figura_evolucion_residuo(resultado, logaritmica=logaritmica), width="stretch", key="gs_fig_residuo", config=config)


def mostrar_resultados_gauss_seidel(resultado: ResultadoGaussSeidel, decimales: int) -> None:
    st.markdown('<div class="step-label">Paso 2 · Análisis</div>', unsafe_allow_html=True)
    st.subheader("Resultados del sistema")
    tabs = st.tabs(
        [
            "Resumen",
            "Resultados",
            "Matrices y operaciones",
            "Explicación paso a paso",
            "Comprobación",
            "Gráficas",
        ]
    )
    with tabs[0]:
        _tab_resumen(resultado, decimales)
    with tabs[1]:
        _tab_resultados(resultado, decimales)
    with tabs[2]:
        _tab_matrices(resultado, decimales)
    with tabs[3]:
        _tab_paso_a_paso(resultado, decimales)
    with tabs[4]:
        _tab_comprobacion(resultado, decimales)
    with tabs[5]:
        _tab_graficas(resultado)


def mostrar_gauss_seidel() -> None:
    """Punto de entrada: formulario + resultados de Gauss-Seidel."""

    _mostrar_formulario()
    if st.session_state.get("gs_error"):
        st.error(st.session_state.gs_error, icon=":material/error:")
    resultado = st.session_state.get("gs_resultado")
    if resultado is not None:
        mostrar_resultados_gauss_seidel(resultado, int(st.session_state.get("gs_decimales", 6)))


__all__ = [
    "EJEMPLO_GAUSS_SEIDEL",
    "limpiar_resultado_gauss_seidel",
    "mostrar_gauss_seidel",
    "mostrar_resultados_gauss_seidel",
]
