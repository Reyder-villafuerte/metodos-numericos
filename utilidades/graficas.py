import numpy as np
import plotly.graph_objects as go
import sympy as sp


def crear_grafica(expresion, raiz, limites, puntos=None):
    """Crea una gráfica interactiva con estilo GNU Octave."""
    inicio, fin = limites
    if inicio >= fin:
        raise ValueError("El rango de la gráfica debe ser creciente.")
    
    # Generar puntos con mayor densidad
    xs = np.linspace(inicio, fin, 1000)
    ys = []
    y_vals_validos = []
    
    for valor in xs:
        try:
            resultado = float(expresion.subs({"x": valor}).evalf())
            
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
        raiz_y = float(expresion.subs({"x": raiz}).evalf())
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
