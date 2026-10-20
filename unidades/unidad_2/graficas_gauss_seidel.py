"""Gráficas Plotly del método de Gauss-Seidel.

Todas las figuras se construyen exclusivamente con el historial almacenado
por ``resolver_gauss_seidel_detallado``; no se recalcula nada aquí.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import plotly.graph_objects as go

from .graficas import COLORES, PLANTILLA
from .presentacion import etiqueta_variable


COLOR_TOLERANCIA = "#f59e0b"
COLOR_ERROR = "#8b5cf6"
COLOR_RESIDUO = "#22d3ee"


def _estilo(figura: go.Figure, titulo: str, eje_y: str, altura: int = 440) -> go.Figure:
    figura.update_layout(
        title=titulo,
        xaxis_title="Iteración k",
        yaxis_title=eje_y,
        template=PLANTILLA,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,43,0.65)",
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.12},
        height=altura,
        margin={"l": 60, "r": 25, "t": 85, "b": 50},
    )
    figura.update_xaxes(dtick=1 if _num_puntos(figura) <= 25 else None, gridcolor="#1e293b")
    figura.update_yaxes(gridcolor="#1e293b")
    return figura


def _num_puntos(figura: go.Figure) -> int:
    return max((len(traza.x) for traza in figura.data if traza.x is not None), default=0)


def figura_convergencia_incognitas(resultado: Any) -> go.Figure:
    """Valor de cada incógnita en k = 0, 1, …, K."""

    iteraciones = [0] + [it.k for it in resultado.historial_detallado]
    valores = np.vstack([resultado.x0] + [it.x for it in resultado.historial_detallado])
    figura = go.Figure()
    for i in range(valores.shape[1]):
        nombre = etiqueta_variable(i + 1)
        figura.add_trace(
            go.Scatter(
                x=iteraciones,
                y=valores[:, i],
                mode="lines+markers",
                name=nombre,
                line={"color": COLORES[i % len(COLORES)], "width": 3},
                marker={"size": 7},
                hovertemplate=f"{nombre}=%{{y:.10g}}<extra></extra>",
            )
        )
    return _estilo(figura, "Convergencia de las incógnitas", "Valor aproximado")


def _serie_error(resultado: Any) -> tuple[list[int], list[float | None]]:
    iteraciones = [it.k for it in resultado.historial_detallado]
    errores = [it.error for it in resultado.historial_detallado]
    return iteraciones, errores


def puede_usar_log(valores: list[float | None]) -> bool:
    finitos = [v for v in valores if v is not None and np.isfinite(v)]
    return bool(finitos) and all(v > 0 for v in finitos)


def figura_evolucion_error(resultado: Any, *, logaritmica: bool = True) -> go.Figure:
    """Error del criterio de parada por iteración y línea de tolerancia."""

    from .metodos.gauss_seidel import CRITERIOS_GAUSS_SEIDEL

    iteraciones, errores = _serie_error(resultado)
    y = [np.nan if v is None else v for v in errores]
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=iteraciones,
            y=y,
            mode="lines+markers",
            name=CRITERIOS_GAUSS_SEIDEL[resultado.criterio],
            line={"color": COLOR_ERROR, "width": 3},
            marker={"size": 8},
            hovertemplate="error=%{y:.6e}<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=[iteraciones[0], iteraciones[-1]] if len(iteraciones) > 1 else [iteraciones[0] - 0.5, iteraciones[0] + 0.5],
            y=[resultado.tolerancia, resultado.tolerancia],
            mode="lines",
            name=f"Tolerancia = {resultado.tolerancia:g}",
            line={"color": COLOR_TOLERANCIA, "width": 2, "dash": "dash"},
            hovertemplate="tolerancia=%{y:.6e}<extra></extra>",
        )
    )
    _estilo(figura, "Evolución del error", "Error del criterio de parada")
    if logaritmica and puede_usar_log(errores):
        figura.update_yaxes(type="log", exponentformat="power")
    return figura


def figura_evolucion_residuo(resultado: Any, *, logaritmica: bool = True) -> go.Figure:
    """‖AX⁽ᵏ⁾ − b‖∞ para k = 0, 1, …, K."""

    iteraciones = [0] + [it.k for it in resultado.historial_detallado]
    residuos = [resultado.residuo_inicial] + [it.residuo for it in resultado.historial_detallado]
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=iteraciones,
            y=residuos,
            mode="lines+markers",
            name="‖AX⁽ᵏ⁾ − b‖∞",
            line={"color": COLOR_RESIDUO, "width": 3},
            marker={"size": 8},
            fill="tozeroy" if not (logaritmica and puede_usar_log(residuos)) else None,
            hovertemplate="residuo=%{y:.6e}<extra></extra>",
        )
    )
    if resultado.criterio == "residuo":
        figura.add_trace(
            go.Scatter(
                x=[iteraciones[0], iteraciones[-1]],
                y=[resultado.tolerancia, resultado.tolerancia],
                mode="lines",
                name=f"Tolerancia = {resultado.tolerancia:g}",
                line={"color": COLOR_TOLERANCIA, "width": 2, "dash": "dash"},
            )
        )
    _estilo(figura, "Evolución del residuo", "‖AX − b‖∞")
    if logaritmica and puede_usar_log(residuos):
        figura.update_yaxes(type="log", exponentformat="power")
    return figura


__all__ = [
    "figura_convergencia_incognitas",
    "figura_evolucion_error",
    "figura_evolucion_residuo",
    "puede_usar_log",
]
