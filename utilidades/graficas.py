import numpy as np
import plotly.graph_objects as go
import sympy as sp


_X_REAL = sp.Symbol("x", real=True)


def _simbolo_de(expresion):
    for simbolo in getattr(expresion, "free_symbols", []):
        if getattr(simbolo, "name", None) == "x":
            return simbolo
    return _X_REAL


def crear_grafica(expresion, raiz, limites, puntos=None):
    """Crea una gráfica interactiva con estilo GNU Octave."""
    inicio, fin = limites
    if inicio >= fin:
        raise ValueError("El rango de la gráfica debe ser creciente.")

    simbolo = _simbolo_de(expresion)

    # Generar puntos con mayor densidad
    xs = np.linspace(inicio, fin, 1000)
    ys = []
    y_vals_validos = []

    for valor in xs:
        try:
            resultado = float(expresion.subs(simbolo, valor).evalf())
            
            # Filtrar valores no finitos y extremadamente grandes
            if np.isnan(resultado) or np.isinf(resultado):
                ys.append(np.nan)
            else:
                # Limitar valores extremos para evitar que compriman la gráfica
                # pero registrar valores válidos para escala
                ys.append(resultado)
                y_vals_validos.append(resultado)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            ys.append(np.nan)
    
    # Determinar escala Y automática basada en valores válidos
    if y_vals_validos:
        y_min_data = np.percentile(y_vals_validos, 1)
        y_max_data = np.percentile(y_vals_validos, 99)
        
        # Si el rango es muy pequeño, expandir
        if abs(y_max_data - y_min_data) < 0.1:
            y_center = (y_max_data + y_min_data) / 2
            y_min_data = y_center - 0.5
            y_max_data = y_center + 0.5
        
        # Agregar margen
        margen_y = (y_max_data - y_min_data) * 0.1
        y_axis_min = y_min_data - margen_y
        y_axis_max = y_max_data + margen_y
    else:
        y_axis_min = -10
        y_axis_max = 10
    
    # Crear figura
    figura = go.Figure()
    
    # Agregar línea de la función
    figura.add_trace(go.Scatter(
        x=xs,
        y=ys,
        mode="lines",
        name="f(x)",
        line={"color": "#1f77b4", "width": 2},
        connectgaps=False,
        hovertemplate="x: %{x:.6f}<br>f(x): %{y:.6f}<extra></extra>"
    ))
    
    # Agregar eje y=0 visible
    figura.add_hline(
        y=0,
        line_dash="solid",
        line_color="#000000",
        line_width=1.5,
        annotation_text="y = 0",
        annotation_position="right"
    )
    
    # Agregar eje x=0 visible si está en rango
    if inicio < 0 < fin:
        figura.add_vline(
            x=0,
            line_dash="solid",
            line_color="#000000",
            line_width=1.5,
            annotation_text="x = 0",
            annotation_position="top"
        )
    
    # Marcar raíz aproximada
    try:
        raiz_y = float(expresion.subs(simbolo, raiz).evalf())
        if np.isfinite(raiz_y) and abs(raiz_y) < 1e6:
            figura.add_trace(go.Scatter(
                x=[raiz],
                y=[raiz_y],
                mode="markers",
                name="Raíz aproximada",
                marker={"size": 12, "color": "#dc2626"},
                hovertemplate="Raíz: x = %{x:.6f}<br>f(x) ≈ %{y:.6e}<extra></extra>"
            ))
        else:
            # Si el valor de f en la raíz no es válido, mostrar en y=0
            figura.add_trace(go.Scatter(
                x=[raiz],
                y=[0],
                mode="markers",
                name="Raíz aproximada",
                marker={"size": 12, "color": "#dc2626"},
                hovertemplate="Raíz: x = %{x:.6f}<extra></extra>"
            ))
    except (TypeError, ValueError, OverflowError, ZeroDivisionError):
        figura.add_trace(go.Scatter(
            x=[raiz],
            y=[0],
            mode="markers",
            name="Raíz aproximada",
            marker={"size": 12, "color": "#dc2626"}
        ))
    
    # Marcar valores iniciales
    if puntos:
        figura.add_trace(go.Scatter(
            x=puntos,
            y=[0] * len(puntos),
            mode="markers",
            name="Valores iniciales",
            marker={"size": 9, "color": "#f59e0b"},
            hovertemplate="Valor inicial: x = %{x:.6f}<extra></extra>"
        ))
    
    # Configurar layout estilo GNU Octave
    figura.update_layout(
        title={"text": f"f(x) = {sp.latex(expresion)}", "x": 0.5, "xanchor": "center"},
        xaxis_title="x",
        yaxis_title="f(x)",
        template="plotly_white",
        hovermode="x unified",
        height=550,
        width=None,
        xaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=1.5,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=1.5,
            range=[y_axis_min, y_axis_max],
        ),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
    )
    
    return figura


def crear_grafica_con_tangente(expresion, fila_iteracion, limites, puntos=None):
    """Crea la gráfica de Newton-Raphson para una iteración.

    Muestra la curva f(x), el punto (xn, f(xn)) con su etiqueta, la recta
    tangente y = f(xn) + f'(xn)*(x - xn), y el cruce con el eje x que
    corresponde a la nueva aproximación xn+1 (con etiqueta).

    Los valores se toman de la fila real de la iteración ({xi, f(xi),
    f'(xi), xi+1}), por lo que funciona para cualquier función válida.
    Controla dominios, valores no reales, infinitos y derivada cercana a cero.
    """
    import math

    inicio, fin = limites
    if inicio >= fin:
        raise ValueError("El rango de la gráfica debe ser creciente.")

    def _es_finito(valor):
        if isinstance(valor, complex):
            return math.isfinite(valor.real) and math.isfinite(valor.imag) and abs(valor.imag) < 1e-14
        return isinstance(valor, (int, float)) and math.isfinite(float(valor))

    xn = fila_iteracion["xi"]
    fxn = fila_iteracion["f(xi)"]
    dfxn = fila_iteracion["f'(xi)"]
    xn1 = fila_iteracion["xi+1"]
    numero = fila_iteracion["i"]

    if not (_es_finito(xn) and _es_finito(fxn) and _es_finito(dfxn) and _es_finito(xn1)):
        raise ValueError("La iteración seleccionada contiene valores no reales o infinitos; no se puede graficar.")

    dfxn = float(dfxn)
    fxn = float(fxn)
    xn = float(xn)
    xn1 = float(xn1)

    derivada_cercana_cero = abs(dfxn) < 1e-14
    tangente_valida = abs(dfxn) > 1e-14 and math.isfinite(fxn) and abs(fxn / max(abs(dfxn), 1e-300)) < 1e308

    simbolo = _simbolo_de(expresion)

    xs = np.linspace(inicio, fin, 1000)
    ys = []
    y_vals_validos = []

    for valor in xs:
        try:
            resultado = float(expresion.subs(simbolo, valor).evalf())
            if np.isnan(resultado) or np.isinf(resultado):
                ys.append(np.nan)
            else:
                ys.append(resultado)
                y_vals_validos.append(resultado)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            ys.append(np.nan)

    if y_vals_validos:
        y_min_data = np.percentile(y_vals_validos, 1)
        y_max_data = np.percentile(y_vals_validos, 99)
        if abs(y_max_data - y_min_data) < 0.1:
            y_center = (y_max_data + y_min_data) / 2
            y_min_data = y_center - 0.5
            y_max_data = y_center + 0.5
        margen_y = (y_max_data - y_min_data) * 0.1
        y_axis_min = y_min_data - margen_y
        y_axis_max = y_max_data + margen_y
    else:
        y_axis_min = -10
        y_axis_max = 10

    figura = go.Figure()

    figura.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines", name="f(x)",
        line={"color": "#1f77b4", "width": 2}, connectgaps=False,
        hovertemplate="x: %{x:.6f}<br>f(x): %{y:.6f}<extra></extra>",
    ))

    figura.add_hline(y=0, line_dash="solid", line_color="#000000", line_width=1.5,
                     annotation_text="y = 0", annotation_position="right")

    if inicio < 0 < fin:
        figura.add_vline(x=0, line_dash="solid", line_color="#000000", line_width=1.5,
                         annotation_text="x = 0", annotation_position="top")

    if tangente_valida:
        ancho = (fin - inicio) * 0.4
        tangente_xs = np.linspace(xn - ancho, xn + ancho, 200)
        tangente_ys = [fxn + dfxn * (t - xn) for t in tangente_xs]
        figura.add_trace(go.Scatter(
            x=tangente_xs, y=tangente_ys, mode="lines", name=f"Recta tangente (iter. {numero})",
            line={"color": "#10b981", "width": 2, "dash": "dash"},
            hovertemplate="x: %{x:.6f}<br>y: %{y:.6f}<extra>Tangente</extra>",
        ))
    else:
        figura.add_annotation(
            text="Derivada cercana a cero: la recta tangente no es útil en este punto.",
            x=0.5, y=0.02, xref="paper", yref="paper", showarrow=False,
            font={"size": 12, "color": "#b45309"},
        )

    # Punto (xn, f(xn)) con etiqueta visible
    if math.isfinite(fxn) and abs(fxn) < 1e6:
        figura.add_trace(go.Scatter(
            x=[xn], y=[fxn], mode="markers",
            name=f"x_{numero-1} (punto actual)",
            marker={"size": 12, "color": "#dc2626"},
            hovertemplate=f"(x_{numero-1}, f(x_{numero-1})) = (%{{x:.6f}}, %{{y:.6f}})<extra></extra>",
        ))
        figura.add_annotation(
            x=xn, y=fxn, text=f"x_{numero-1}", showarrow=True, arrowhead=2,
            ax=0, ay=-38, arrowcolor="#dc2626", font={"size": 13, "color": "#dc2626"},
        )
    else:
        figura.add_trace(go.Scatter(
            x=[xn], y=[0], mode="markers",
            name=f"x_{numero-1} (punto actual)",
            marker={"size": 12, "color": "#dc2626"},
        ))
        figura.add_annotation(
            x=xn, y=0, text=f"x_{numero-1}", showarrow=True, arrowhead=2,
            ax=0, ay=-38, arrowcolor="#dc2626", font={"size": 13, "color": "#dc2626"},
        )

    # Cruce de la tangente con el eje x: xn+1
    if tangente_valida and math.isfinite(xn1):
        figura.add_trace(go.Scatter(
            x=[xn1], y=[0], mode="markers",
            name=f"x_{numero} (cruce con eje x)",
            marker={"size": 11, "color": "#f59e0b", "symbol": "diamond"},
            hovertemplate=f"x_{numero} = %{{x:.6f}}<br>y = 0<extra></extra>",
        ))
        figura.add_annotation(
            x=xn1, y=0, text=f"x_{numero}", showarrow=True, arrowhead=2,
            ax=0, ay=42, arrowcolor="#f59e0b", font={"size": 13, "color": "#b45309"},
        )

    if puntos:
        figura.add_trace(go.Scatter(
            x=puntos, y=[0] * len(puntos), mode="markers",
            name="Valores iniciales",
            marker={"size": 9, "color": "#f59e0b"},
            hovertemplate="Valor inicial: x = %{x:.6f}<extra></extra>",
        ))

    figura.update_layout(
        title={"text": f"Iteración {numero} — Tangente de f(x) = {sp.latex(expresion)}", "x": 0.5, "xanchor": "center"},
        xaxis_title="x", yaxis_title="f(x)",
        template="plotly_white", hovermode="x unified", height=550, width=None,
        xaxis=dict(showgrid=True, gridcolor="lightgray", zeroline=True, zerolinecolor="black", zerolinewidth=1.5),
        yaxis=dict(showgrid=True, gridcolor="lightgray", zeroline=True, zerolinecolor="black", zerolinewidth=1.5,
                   range=[y_axis_min, y_axis_max]),
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255, 255, 255, 0.8)"),
    )

    return figura


def crear_grafica_compleja(iteraciones, raiz):
    """Grafica el recorrido de Müller en el plano complejo."""
    aproximaciones = [complex(fila["x3"]) for fila in iteraciones]
    raiz_compleja = complex(raiz)
    figura = go.Figure()
    if aproximaciones:
        figura.add_trace(go.Scatter(
            x=[valor.real for valor in aproximaciones],
            y=[valor.imag for valor in aproximaciones],
            mode="lines+markers",
            name="Aproximaciones",
            hovertemplate="Re: %{x:.6f}<br>Im: %{y:.6f}<extra></extra>",
        ))
    figura.add_trace(go.Scatter(
        x=[raiz_compleja.real], y=[raiz_compleja.imag], mode="markers",
        name="Raíz final", marker={"size": 13, "color": "#dc2626"},
        hovertemplate="Raíz: %{x:.6f} + %{y:.6f}i<extra></extra>",
    ))
    figura.add_hline(y=0, line_color="black", line_width=1)
    figura.add_vline(x=0, line_color="black", line_width=1)
    figura.update_layout(
        title="Recorrido de Müller en el plano complejo",
        xaxis_title="Parte real", yaxis_title="Parte imaginaria",
        template="plotly_white", height=550,
        xaxis={"showgrid": True, "gridcolor": "lightgray"},
        yaxis={"showgrid": True, "gridcolor": "lightgray", "scaleanchor": "x", "scaleratio": 1},
    )
    return figura
