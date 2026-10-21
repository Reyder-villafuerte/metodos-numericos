"""Componentes Streamlit reutilizables para presentar la Unidad 2."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from .explicaciones import latex_matriz, latex_numero
from .graficas import construir_figuras
from .presentacion import (
    clasificar_sistema,
    conclusion_resultado,
    dataframe_matriz,
    dataframe_vector,
    ecuacion_latex,
    etiqueta_variable,
    filas_comprobacion,
    latex_fraccion,
    solucion_racional_verificada,
    texto_fraccion,
)


def mostrar_matriz(
    destino: Any,
    matriz: Any,
    nombre: str,
    *,
    columnas_variables: bool = True,
    filas_ecuaciones: bool = True,
) -> None:
    destino.caption(nombre)
    destino.dataframe(
        dataframe_matriz(
            matriz,
            columnas_variables=columnas_variables,
            filas_ecuaciones=filas_ecuaciones,
        ),
        width="stretch",
    )


def mostrar_vector(destino: Any, vector: Any, nombre: str) -> None:
    destino.caption(nombre)
    destino.dataframe(dataframe_vector(vector, nombre), width="stretch")


def mostrar_resumen(resultado: Any, decimales: int) -> None:
    with st.container(horizontal=True):
        st.metric("Incógnitas", len(resultado.x), border=True)
        st.metric("det(A)", f"{resultado.determinante:.{decimales}g}", border=True)
        st.metric("Residuo máximo", f"{resultado.norma_residuo:.{decimales}g}", border=True)
        st.metric("Pivoteo", "Sí" if resultado.hubo_pivoteo else "No", border=True)
    st.success("El sistema se resolvió y se comprobó numéricamente con Ax=b.")
    st.latex(f"x={latex_matriz(resultado.x, decimales)}")
    solucion = pd.DataFrame(
        {
            "Incógnita": [etiqueta_variable(i) for i in range(1, len(resultado.x) + 1)],
            "Valor aproximado": resultado.x,
        }
    )
    st.dataframe(
        solucion,
        hide_index=True,
        column_config={
            "Valor aproximado": st.column_config.NumberColumn(format=f"%.{decimales}g")
        },
    )


def _mostrar_tarjetas_solucion(resultado: Any, decimales: int) -> None:
    exacta = solucion_racional_verificada(resultado.A, resultado.b, resultado.x)
    for inicio in range(0, len(resultado.x), 4):
        bloque = resultado.x[inicio : inicio + 4]
        columnas = st.columns(len(bloque), border=True)
        for desplazamiento, (columna, valor) in enumerate(zip(columnas, bloque)):
            indice = inicio + desplazamiento
            columna.metric(
                etiqueta_variable(indice + 1),
                f"{float(valor):.{decimales}g}",
            )
            if exacta is not None:
                columna.caption(f"Exacto: {texto_fraccion(exacta[indice])}")
            else:
                columna.caption("Aproximación decimal")

    if exacta is not None:
        vector_exacto = r"\begin{bmatrix}" + r" \\ ".join(
            latex_fraccion(valor) for valor in exacta
        ) + r"\end{bmatrix}"
        st.markdown("**Forma racional exacta verificada**")
        st.latex(rf"x={vector_exacto}")
        st.caption(
            "Esta forma racional satisface exactamente los coeficientes decimales ingresados."
        )
    else:
        st.caption(
            "No se identificó una forma racional exacta verificable; se muestran únicamente aproximaciones."
        )


def _mostrar_datos_especificos(resultado: Any) -> None:
    if resultado.inversa is not None:
        st.markdown("#### Matriz inversa")
        mostrar_matriz(st, resultado.inversa, "A⁻¹")
    elif resultado.matrices_cramer:
        st.markdown("#### Determinantes de Cramer")
        determinantes = pd.DataFrame(
            {
                "Determinante": ["det(A)"]
                + [f"det(A{str(i).translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))})" for i in range(1, len(resultado.x) + 1)],
                "Valor": [resultado.determinante] + resultado.determinantes_cramer,
            }
        )
        st.dataframe(
            determinantes,
            hide_index=True,
            column_config={"Valor": st.column_config.NumberColumn(format="%.12g")},
        )
    elif resultado.L is not None and resultado.U is not None:
        st.markdown("#### Factores LU")
        columnas = st.columns(3 if resultado.hubo_pivoteo else 2)
        desplazamiento = 0
        if resultado.hubo_pivoteo and resultado.P is not None:
            mostrar_matriz(
                columnas[0], resultado.P, "P", columnas_variables=False, filas_ecuaciones=False
            )
            desplazamiento = 1
        mostrar_matriz(
            columnas[desplazamiento],
            resultado.L,
            "L",
            columnas_variables=False,
            filas_ecuaciones=False,
        )
        mostrar_matriz(
            columnas[desplazamiento + 1],
            resultado.U,
            "U",
            columnas_variables=False,
            filas_ecuaciones=False,
        )


def mostrar_resultados_completos(resultado: Any, decimales: int) -> None:
    st.markdown(f"### {resultado.metodo}")
    estado = clasificar_sistema(resultado.A, resultado.b, resultado.tolerancia)
    st.success(f"Estado del sistema: {estado}", icon=":material/check_circle:")

    st.markdown("#### Sistema original")
    st.latex(
        f"{latex_matriz(resultado.A, decimales)}"
        + r"\begin{bmatrix}"
        + r" \\ ".join(f"x_{{{i}}}" for i in range(1, len(resultado.x) + 1))
        + r"\end{bmatrix}="
        + latex_matriz(resultado.b, decimales)
    )
    with st.expander("Ver ecuaciones individualmente"):
        for indice, (fila, termino) in enumerate(zip(resultado.A, resultado.b), start=1):
            st.latex(rf"({indice})\quad {ecuacion_latex(fila, termino)}")

    columnas = st.columns(2)
    mostrar_matriz(columnas[0], resultado.A, "Matriz A")
    mostrar_vector(columnas[1], resultado.b, "b")

    st.markdown("#### Solución")
    _mostrar_tarjetas_solucion(resultado, decimales)
    st.latex(rf"x_{{\mathrm{{decimal}}}}={latex_matriz(resultado.x, decimales)}")

    with st.container(horizontal=True):
        st.metric("Determinante de A", f"{resultado.determinante:.12g}", border=True)
        st.metric("Norma ‖Ax − b‖∞", f"{resultado.norma_residuo:.12e}", border=True)

    _mostrar_datos_especificos(resultado)

    st.markdown("#### Comprobación compacta")
    st.latex(f"Ax={latex_matriz(resultado.comprobacion, 12)}")
    st.latex(f"Ax-b={latex_matriz(resultado.residuo, 12)}")
    st.info(conclusion_resultado(resultado), icon=":material/functions:")


def mostrar_comprobacion_detallada(resultado: Any, decimales: int) -> None:
    if resultado.P is not None and resultado.L is not None and resultado.U is not None:
        relacion = "PA − LU" if resultado.hubo_pivoteo else "A − LU"
        st.markdown(f"**Verificación de la factorización ({relacion})**")
        st.metric(
            "Norma del error de factorización",
            f"{resultado.norma_factorizacion:.12e}",
            border=True,
        )

    st.markdown("#### Sustitución en cada ecuación")
    filas = filas_comprobacion(resultado.A, resultado.b, resultado.x)
    for fila in filas:
        with st.container(border=True):
            st.markdown(f"**Ecuación {fila['ecuacion']}**")
            st.latex(fila["simbolica"])
            st.latex(fila["sustitucion"])
            st.caption(
                f"Lado izquierdo = {fila['lado_izquierdo']:.12g} · "
                f"Lado derecho = {fila['lado_derecho']:.12g} · "
                f"Residuo = {fila['residuo']:.12e}"
            )

    st.markdown("#### Vectores de comprobación")
    columnas = st.columns(3)
    mostrar_vector(columnas[0], resultado.comprobacion, "Ax")
    mostrar_vector(columnas[1], resultado.b, "b")
    mostrar_vector(columnas[2], resultado.residuo, "Ax − b")
    st.metric("‖Ax − b‖∞", f"{resultado.norma_residuo:.12e}", border=True)
    st.caption(
        "Los residuos se presentan con doce cifras significativas. Un valor pequeño "
        "indica concordancia numérica, no necesariamente igualdad algebraica exacta."
    )


def mostrar_graficas(resultado: Any) -> None:
    n = len(resultado.x)
    if n == 2:
        st.caption(
            "Cada ecuación se representa como una recta; la solución calculada se marca en su intersección."
        )
    elif n == 3:
        st.caption(
            "Cada ecuación se parametriza como un plano usando la variable con coeficiente más estable."
        )
    else:
        st.caption(
            "Una intersección completa en más de tres dimensiones no es representable. "
            "Se muestran coeficientes, componentes de la solución y residuos."
        )

    for clave, titulo, figura in construir_figuras(resultado):
        with st.container(border=True):
            st.markdown(f"#### {titulo}")
            st.plotly_chart(
                figura,
                width="stretch",
                key=f"u2_grafica_{resultado.metodo}_{len(resultado.x)}_{clave}",
                config={
                    "displaylogo": False,
                    "scrollZoom": True,
                    "responsive": True,
                },
            )

    if resultado.matrices_cramer and n > 4:
        st.caption(
            "Para mantener la legibilidad, las matrices Aᵢ de Cramer se conservan en "
            "“Matrices y operaciones”; en esta pestaña no se generan ocho mapas adicionales."
        )


def mostrar_graficas_newton_sistema(funciones: Any, resultado: Any) -> None:
    """Muestra geometría, trayectoria y convergencia de Newton para dos variables."""
    from .graficas import crear_graficas_newton_sistema

    figuras = crear_graficas_newton_sistema(
        funciones,
        resultado.historial,
        resultado.x,
    )
    st.info(
        "Las curvas de nivel F₁=0 y F₂=0 se cortan en la solución. "
        "La línea punteada muestra cómo Newton se desplaza desde x⁽⁰⁾ hasta la raíz.",
        icon=":material/insights:",
    )
    st.plotly_chart(
        figuras[0],
        width="stretch",
        key="u2_newton_grafica_curvas",
        config={"displaylogo": False, "scrollZoom": True, "responsive": True},
    )
    columnas = st.columns(2)
    with columnas[0]:
        st.plotly_chart(
            figuras[1],
            width="stretch",
            key="u2_newton_grafica_convergencia",
            config={"displaylogo": False, "scrollZoom": True, "responsive": True},
        )
    with columnas[1]:
        st.plotly_chart(
            figuras[2],
            width="stretch",
            key="u2_newton_grafica_componentes",
            config={"displaylogo": False, "scrollZoom": True, "responsive": True},
        )


__all__ = [
    "mostrar_comprobacion_detallada",
    "mostrar_graficas",
    "mostrar_graficas_newton_sistema",
    "mostrar_matriz",
    "mostrar_resultados_completos",
    "mostrar_resumen",
    "mostrar_vector",
]
