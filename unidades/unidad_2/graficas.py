"""Figuras Plotly reutilizables para los resultados de la Unidad 2."""

from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go

from .presentacion import etiquetas_ecuaciones, etiquetas_variables


COLORES = ["#8b5cf6", "#22d3ee", "#f59e0b", "#ec4899", "#10b981", "#60a5fa"]
COLOR_SOLUCION = "#fb7185"
PLANTILLA = "plotly_dark"


def _extension_visual(solucion: np.ndarray) -> float:
    return max(4.0, float(np.max(np.abs(solucion))) * 0.6 + 2.0)


def crear_grafica_sistema_2d(
    A: Any,
    b: Any,
    x: Any,
    *,
    tolerancia: float = 1e-12,
) -> go.Figure:
    """Representa dos ecuaciones como rectas, incluidas rectas verticales."""

    matriz = np.asarray(A, dtype=float)
    vector = np.asarray(b, dtype=float).reshape(-1)
    solucion = np.asarray(x, dtype=float).reshape(-1)
    if matriz.shape != (2, 2) or vector.shape != (2,) or solucion.shape != (2,):
        raise ValueError("La gráfica 2D requiere un sistema 2×2 y una solución de dos componentes.")

    amplitud = _extension_visual(solucion)
    valores_x = np.linspace(solucion[0] - amplitud, solucion[0] + amplitud, 240)
    valores_y = np.linspace(solucion[1] - amplitud, solucion[1] + amplitud, 240)
    figura = go.Figure()
    for indice, ((a, c), termino) in enumerate(zip(matriz, vector), start=1):
        color = COLORES[(indice - 1) % len(COLORES)]
        if abs(c) > tolerancia:
            xs = valores_x
            ys = (termino - a * xs) / c
        elif abs(a) > tolerancia:
            xs = np.full_like(valores_y, termino / a)
            ys = valores_y
        else:
            continue
        figura.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                name=f"Ecuación {indice}",
                line={"color": color, "width": 3},
                hovertemplate="x₁=%{x:.6g}<br>x₂=%{y:.6g}<extra>"
                f"Ecuación {indice}</extra>",
            )
        )
    figura.add_trace(
        go.Scatter(
            x=[solucion[0]],
            y=[solucion[1]],
            mode="markers",
            name="Solución",
            marker={"size": 13, "color": COLOR_SOLUCION, "symbol": "diamond"},
            hovertemplate="x₁=%{x:.10g}<br>x₂=%{y:.10g}<extra>Solución</extra>",
        )
    )
    figura.update_layout(
        title="Intersección de las ecuaciones",
        xaxis_title="x₁",
        yaxis_title="x₂",
        template=PLANTILLA,
        hovermode="closest",
        legend={"orientation": "h", "y": 1.08},
        height=560,
        margin={"l": 40, "r": 30, "t": 80, "b": 45},
    )
    figura.update_xaxes(zeroline=True, zerolinecolor="#64748b")
    figura.update_yaxes(zeroline=True, zerolinecolor="#64748b", scaleanchor="x", scaleratio=1)
    return figura


def _superficie_plano(
    coeficientes: np.ndarray,
    termino: float,
    solucion: np.ndarray,
    amplitud: float,
    puntos: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    dependiente = int(np.argmax(np.abs(coeficientes)))
    independientes = [indice for indice in range(3) if indice != dependiente]
    rejilla_1 = np.linspace(
        solucion[independientes[0]] - amplitud,
        solucion[independientes[0]] + amplitud,
        puntos,
    )
    rejilla_2 = np.linspace(
        solucion[independientes[1]] - amplitud,
        solucion[independientes[1]] + amplitud,
        puntos,
    )
    valor_1, valor_2 = np.meshgrid(rejilla_1, rejilla_2)
    dependiente_valor = (
        termino
        - coeficientes[independientes[0]] * valor_1
        - coeficientes[independientes[1]] * valor_2
    ) / coeficientes[dependiente]
    coordenadas: list[np.ndarray | None] = [None, None, None]
    coordenadas[independientes[0]] = valor_1
    coordenadas[independientes[1]] = valor_2
    coordenadas[dependiente] = dependiente_valor
    nombres = ["x₁", "x₂", "x₃"]
    return (
        np.asarray(coordenadas[0]),
        np.asarray(coordenadas[1]),
        np.asarray(coordenadas[2]),
        nombres[dependiente],
    )


def crear_grafica_sistema_3d(
    A: Any,
    b: Any,
    x: Any,
    *,
    tolerancia: float = 1e-12,
) -> go.Figure:
    """Representa tres planos eligiendo para cada uno la variable más estable."""

    matriz = np.asarray(A, dtype=float)
    vector = np.asarray(b, dtype=float).reshape(-1)
    solucion = np.asarray(x, dtype=float).reshape(-1)
    if matriz.shape != (3, 3) or vector.shape != (3,) or solucion.shape != (3,):
        raise ValueError("La gráfica 3D requiere un sistema 3×3 y una solución de tres componentes.")
    if np.any(np.max(np.abs(matriz), axis=1) <= tolerancia):
        raise ValueError("No puede representarse un plano con todos sus coeficientes nulos.")

    amplitud = _extension_visual(solucion)
    figura = go.Figure()
    for indice, (coeficientes, termino) in enumerate(zip(matriz, vector), start=1):
        xs, ys, zs, dependiente = _superficie_plano(
            coeficientes, float(termino), solucion, amplitud, 35
        )
        color = COLORES[(indice - 1) % len(COLORES)]
        figura.add_trace(
            go.Surface(
                x=xs,
                y=ys,
                z=zs,
                name=f"Plano {indice}",
                legendgroup=f"plano-{indice}",
                showlegend=True,
                showscale=False,
                opacity=0.58,
                colorscale=[[0, color], [1, color]],
                hovertemplate=(
                    "x₁=%{x:.5g}<br>x₂=%{y:.5g}<br>x₃=%{z:.5g}"
                    f"<extra>Plano {indice} · despejado en {dependiente}</extra>"
                ),
            )
        )
    figura.add_trace(
        go.Scatter3d(
            x=[solucion[0]],
            y=[solucion[1]],
            z=[solucion[2]],
            mode="markers",
            name="Solución",
            marker={"size": 7, "color": COLOR_SOLUCION, "symbol": "diamond"},
            hovertemplate=(
                "x₁=%{x:.10g}<br>x₂=%{y:.10g}<br>x₃=%{z:.10g}"
                "<extra>Solución</extra>"
            ),
        )
    )
    figura.update_layout(
        title="Intersección de los tres planos",
        template=PLANTILLA,
        height=680,
        scene={
            "xaxis_title": "x₁",
            "yaxis_title": "x₂",
            "zaxis_title": "x₃",
            "aspectmode": "cube",
        },
        legend={"orientation": "h", "y": 1.05},
        margin={"l": 10, "r": 10, "t": 80, "b": 10},
    )
    return figura


def crear_mapa_calor(
    matriz: Any,
    titulo: str,
    *,
    columnas: list[str] | None = None,
    filas: list[str] | None = None,
) -> go.Figure:
    datos = np.asarray(matriz, dtype=float)
    if datos.ndim != 2:
        raise ValueError("El mapa de calor requiere una matriz bidimensional.")
    etiquetas_x = columnas or etiquetas_variables(datos.shape[1])
    etiquetas_y = filas or etiquetas_ecuaciones(datos.shape[0])
    figura = go.Figure(
        go.Heatmap(
            z=datos,
            x=etiquetas_x,
            y=etiquetas_y,
            colorscale="Purples",
            zmid=0,
            text=np.vectorize(lambda valor: f"{valor:.5g}")(datos),
            texttemplate="%{text}",
            hovertemplate="%{y}, %{x}: %{z:.10g}<extra></extra>",
            colorbar={"title": "Valor"},
        )
    )
    figura.update_layout(
        title=titulo,
        template=PLANTILLA,
        height=max(390, 52 * datos.shape[0] + 180),
        margin={"l": 80, "r": 30, "t": 70, "b": 50},
        yaxis={"autorange": "reversed"},
    )
    return figura


def crear_grafica_componentes(vector: Any, titulo: str, nombre_eje: str) -> go.Figure:
    datos = np.asarray(vector, dtype=float).reshape(-1)
    figura = go.Figure(
        go.Bar(
            x=etiquetas_variables(len(datos)),
            y=datos,
            marker_color="#8b5cf6",
            text=[f"{valor:.6g}" for valor in datos],
            textposition="outside",
            hovertemplate="%{x}=%{y:.10g}<extra></extra>",
        )
    )
    figura.update_layout(
        title=titulo,
        xaxis_title="Componente",
        yaxis_title=nombre_eje,
        template=PLANTILLA,
        height=430,
        margin={"l": 50, "r": 25, "t": 70, "b": 45},
    )
    return figura


def crear_grafica_residuos(residuo: Any) -> go.Figure:
    datos = np.asarray(residuo, dtype=float).reshape(-1)
    figura = go.Figure(
        go.Bar(
            x=etiquetas_ecuaciones(len(datos)),
            y=datos,
            marker_color="#22d3ee",
            text=[f"{valor:.3e}" for valor in datos],
            textposition="outside",
            hovertemplate="%{x}<br>residuo=%{y:.12e}<extra></extra>",
        )
    )
    figura.update_layout(
        title="Residuo por ecuación",
        xaxis_title="Ecuación",
        yaxis_title="(Ax − b)ᵢ",
        template=PLANTILLA,
        height=430,
        margin={"l": 55, "r": 25, "t": 70, "b": 45},
    )
    return figura


def construir_figuras(resultado: Any) -> list[tuple[str, str, go.Figure]]:
    """Devuelve figuras basadas exclusivamente en el resultado seleccionado."""

    n = len(resultado.x)
    figuras: list[tuple[str, str, go.Figure]] = []
    if n == 2:
        figuras.append(
            ("sistema-2d", "Sistema 2×2", crear_grafica_sistema_2d(resultado.A, resultado.b, resultado.x, tolerancia=resultado.tolerancia))
        )
    elif n == 3:
        figuras.append(
            ("sistema-3d", "Sistema 3×3", crear_grafica_sistema_3d(resultado.A, resultado.b, resultado.x, tolerancia=resultado.tolerancia))
        )
    else:
        figuras.extend(
            [
                ("matriz-a", "Mapa de calor de A", crear_mapa_calor(resultado.A, "Coeficientes de la matriz A")),
                ("solucion", "Componentes de x", crear_grafica_componentes(resultado.x, "Componentes del vector solución", "Valor")),
                ("residuos", "Residuos", crear_grafica_residuos(resultado.residuo)),
            ]
        )

    if resultado.inversa is not None:
        figuras.append(
            ("inversa", "Mapa de calor de A⁻¹", crear_mapa_calor(resultado.inversa, "Matriz inversa A⁻¹"))
        )
    elif resultado.matrices_cramer:
        if n <= 4:
            figuras.append(("cramer-a", "Matriz A", crear_mapa_calor(resultado.A, "Matriz original A")))
            for indice, matriz in enumerate(resultado.matrices_cramer, start=1):
                figuras.append(
                    (f"cramer-a-{indice}", f"Matriz A{subindice_texto(indice)}", crear_mapa_calor(matriz, f"Matriz A{subindice_texto(indice)}"))
                )
    elif resultado.L is not None and resultado.U is not None:
        etiquetas = [f"Columna {i}" for i in range(1, n + 1)]
        filas = [f"Fila {i}" for i in range(1, n + 1)]
        figuras.extend(
            [
                ("lu-l", "Mapa de calor de L", crear_mapa_calor(resultado.L, "Matriz triangular inferior L", columnas=etiquetas, filas=filas)),
                ("lu-u", "Mapa de calor de U", crear_mapa_calor(resultado.U, "Matriz triangular superior U", columnas=etiquetas, filas=filas)),
            ]
        )
        if resultado.hubo_pivoteo and resultado.P is not None:
            figuras.append(
                ("lu-p", "Mapa de calor de P", crear_mapa_calor(resultado.P, "Matriz de permutación P", columnas=etiquetas, filas=filas))
            )
    return figuras


def subindice_texto(numero: int) -> str:
    traduccion = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return str(numero).translate(traduccion)


__all__ = [
    "construir_figuras",
    "crear_grafica_componentes",
    "crear_grafica_residuos",
    "crear_grafica_sistema_2d",
    "crear_grafica_sistema_3d",
    "crear_mapa_calor",
]
