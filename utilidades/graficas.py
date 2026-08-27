import numpy as np
import plotly.graph_objects as go


def crear_grafica(expresion, raiz, limites, puntos=None):
    inicio, fin = limites
    if inicio >= fin:
        raise ValueError("El rango de la gráfica debe ser creciente.")
    xs = np.linspace(inicio, fin, 600)
    ys = []
    for valor in xs:
        try:
            resultado = float(expresion.subs({"x": valor}).evalf())
            ys.append(resultado if np.isfinite(resultado) and abs(resultado) < 1e6 else np.nan)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            ys.append(np.nan)
    figura = go.Figure()
    figura.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)", line={"color": "#1d4ed8", "width": 3}, connectgaps=False))
    figura.add_hline(y=0, line_dash="dash", line_color="#64748b", name="y = 0")
    figura.add_trace(go.Scatter(x=[raiz], y=[0], mode="markers", name="Raíz aproximada", marker={"size": 12, "color": "#dc2626"}))
    if puntos:
        figura.add_trace(go.Scatter(x=puntos, y=[0] * len(puntos), mode="markers", name="Valores iniciales", marker={"size": 9, "color": "#f59e0b"}))
    figura.update_layout(title="Comportamiento de la función", xaxis_title="x", yaxis_title="f(x)", template="plotly_white", hovermode="x unified")
    return figura
