"""Utilidades para sugerir despejes de g(x) en método de punto fijo."""

import sympy as sp
from .parser_funciones import X


def sugerir_despejes(expresion_str):
    """
    Sugiere posibles despejes g(x) para un f(x) dado.
    
    Para f(x) = 0, intentamos encontrar f(x) = x => g(x) = despeje.
    
    Retorna una lista de tuplas (descripción, expresión_g(x)).
    """
    sugerencias = []
    
    try:
        # Normalizar entrada
        f_original = expresion_str.strip()
        
        # Intentar sugerencias básicas
        
        # 1. Si es f(x) = x^3 + ax^2 + bx + c, sugerir x = (d - ax^2 - bx) / c, etc.
        if "x^3" in f_original or "x**3" in f_original:
            # f(x) = x^3 + 2x^2 + 10x - 20 => x = (20 - x^3 - 2x^2) / 10
            sugerencias.append((
                "Despejar término independiente",
                "Estructura: x = (constante - otros términos) / coeficiente"
            ))
        
        # 2. Si contiene exp, logaritmo
        if "exp" in f_original.lower() or "ln" in f_original.lower() or "log" in f_original.lower():
            sugerencias.append((
                "Función exponencial/logarítmica",
                "Considere usar propiedades: ln(x) = y => x = e^y, e^x = y => x = ln(y)"
            ))
        
        # 3. Si contiene sin, cos
        if "sin" in f_original.lower() or "cos" in f_original.lower():
            sugerencias.append((
                "Función trigonométrica",
                "Considere aislar la función: sin(x) = y => x = arcsin(y)"
            ))
        
        # 4. Sugerencia genérica
        sugerencias.append((
            "Método general",
            "Si f(x) = 0, despeje para obtener x = g(x). Por ejemplo: f(x) = x^2 - 4 => x = ±√(4) = ±2"
        ))
        
    except Exception:
        pass
    
    return sugerencias if sugerencias else [(
        "Despeje manual",
        "Escriba manualmente g(x) tal que x = g(x) sea equivalente a f(x) = 0"
    )]


def evaluar_convergencia_local(g_expr, x0):
    """
    Evalúa si el método de punto fijo probablemente convergerá localmente.
    
    Retorna (converge, criterio_valor, mensaje).
    """
    try:
        derivada_g = sp.diff(g_expr, X)
        criterio = abs(float(derivada_g.subs(X, x0).evalf()))
        
        converge = criterio < 1.0
        
        if criterio < 0.5:
            mensaje = f"✓ Criterio cumplido (|g'({x0})| = {criterio:.6f} < 0.5): Convergencia probable rápida"
        elif criterio < 1.0:
            mensaje = f"✓ Criterio cumplido (|g'({x0})| = {criterio:.6f} < 1.0): Convergencia probable, pero puede ser lenta"
        else:
            mensaje = f"✗ Criterio no cumplido (|g'({x0})| = {criterio:.6f} ≥ 1.0): Divergencia probable"
        
        return converge, criterio, mensaje
    
    except Exception as exc:
        return None, None, f"No se pudo evaluar el criterio: {str(exc)}"
