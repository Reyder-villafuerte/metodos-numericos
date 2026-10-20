#!/usr/bin/env python
"""Prueba rápida de la aplicación sin interfaz gráfica."""

import sys
from utilidades.parser_funciones import analizar_funcion, funcion_numerica, X
from unidades.unidad_1.metodos import biseccion
from unidades.unidad_1.metodos import newton_raphson
from unidades.unidad_1.metodos import punto_fijo
from unidades.unidad_1.metodos import secante
from unidades.unidad_1.metodos import regla_falsa
import sympy as sp


def prueba_completa():
    """Prueba cada método con ejercicios estándar."""
    
    print("="*60)
    print("PRUEBA COMPLETA DE MÉTODOS NUMÉRICOS")
    print("="*60)
    
    # Bisección: exp(-x)-x, a=0, b=1
    print("\n1. BISECCION: exp(-x)-x en [0, 1]")
    f = funcion_numerica(analizar_funcion("exp(-x)-x"))
    r = biseccion(f, 0, 1, 0.01, 100)
    print(f"   Raiz: {r.raiz:.6f}")
    print(f"   Error: {r.error_final:.6f}%")
    print(f"   Iteraciones: {len(r.iteraciones)}")
    print(f"   Convergio: {r.convergio}")
    
    # Regla Falsa: x*sin(x)-1 en [2, 3]
    print("\n2. REGLA FALSA: x*sin(x)-1 en [2, 3]")
    f = funcion_numerica(analizar_funcion("x*sin(x)-1"))
    r = regla_falsa(f, 2, 3, 0.01, 100)
    print(f"   Raiz: {r.raiz:.6f}")
    print(f"   Error: {r.error_final:.6f}%")
    print(f"   Iteraciones: {len(r.iteraciones)}")
    print(f"   Convergio: {r.convergio}")
    
    # Newton-Raphson: exp(-x)-x, x0=0.5
    print("\n3. NEWTON-RAPHSON: exp(-x)-x, x0=0.5")
    expr = analizar_funcion("exp(-x)-x")
    f = funcion_numerica(expr)
    df = sp.diff(expr, X)
    df_num = funcion_numerica(df)
    r = newton_raphson(f, df_num, 0.5, 0.01, 100)
    print(f"   Raiz: {r.raiz:.6f}")
    print(f"   Error: {r.error_final:.6f}%")
    print(f"   Iteraciones: {len(r.iteraciones)}")
    print(f"   Convergio: {r.convergio}")
    
    # Secante: exp(-x)-x, x0=0, x1=1
    print("\n4. SECANTE: exp(-x)-x, x0=0, x1=1")
    f = funcion_numerica(analizar_funcion("exp(-x)-x"))
    r = secante(f, 0, 1, 0.01, 100)
    print(f"   Raiz: {r.raiz:.6f}")
    print(f"   Error: {r.error_final:.6f}%")
    print(f"   Iteraciones: {len(r.iteraciones)}")
    print(f"   Convergio: {r.convergio}")
    
    # Punto Fijo: x^3+2x^2+10x-20, g(x)=20/(x^2+2x+10), x0=1.5
    print("\n5. PUNTO FIJO: x^3+2x^2+10x-20, g(x)=20/(x^2+2x+10), x0=1.5")
    f = funcion_numerica(analizar_funcion("x^3+2*x^2+10*x-20"))
    g = funcion_numerica(analizar_funcion("20/(x^2+2*x+10)"))
    r = punto_fijo(f, g, 1.5, 0.01, 100)
    print(f"   Raiz: {r.raiz:.6f}")
    print(f"   Error: {r.error_final:.6f}%")
    print(f"   Iteraciones: {len(r.iteraciones)}")
    print(f"   Convergio: {r.convergio}")
    
    # Nueva función: Newton-Raphson con arctan
    print("\n6. NEWTON-RAPHSON: 1-x^2-arctan(x), x0=0.2 (NUEVA FUNCION)")
    expr = analizar_funcion("1-x^2-arctan(x)")
    f = funcion_numerica(expr)
    df = sp.diff(expr, X)
    df_num = funcion_numerica(df)
    r = newton_raphson(f, df_num, 0.2, 0.01, 100)
    print(f"   Raiz: {r.raiz:.6f}")
    print(f"   Error: {r.error_final:.6f}%")
    print(f"   Iteraciones: {len(r.iteraciones)}")
    print(f"   Convergio: {r.convergio}")
    
    # Nueva función: Secante con arcsin
    print("\n7. SECANTE: arcsin(x)-exp(-2*x), x0=0.1, x1=0.5 (NUEVA FUNCION)")
    f = funcion_numerica(analizar_funcion("arcsin(x)-exp(-2*x)"))
    r = secante(f, 0.1, 0.5, 0.01, 100)
    print(f"   Raiz: {r.raiz:.6f}")
    print(f"   Error: {r.error_final:.6f}%")
    print(f"   Iteraciones: {len(r.iteraciones)}")
    print(f"   Convergio: {r.convergio}")
    
    print("\n" + "="*60)
    print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("="*60)


if __name__ == "__main__":
    try:
        prueba_completa()
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
