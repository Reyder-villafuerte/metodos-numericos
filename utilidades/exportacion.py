from io import BytesIO
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import math
import sympy as sp


def _convertir_valor(valor):
    """Convierte un valor a un tipo Python nativo seguro para Excel."""
    if valor is None:
        return ""
    if isinstance(valor, (int, float)):
        if math.isnan(valor) or math.isinf(valor):
            return "Error"
        return valor
    if isinstance(valor, sp.Basic):
        return str(valor)
    if isinstance(valor, complex):
        return str(valor)
    return valor


def crear_excel(titulo, funcion, metodo, parametros, error_permitido, raiz, error_final, iteraciones):
    """Crea un archivo Excel con resultados de métodos numéricos."""
    salida = BytesIO()
    
    try:
        # Preparar datos del resumen
        raiz_conv = float(raiz) if raiz is not None else 0.0
        error_final_conv = float(error_final) if error_final is not None else 0.0
        error_permitido_conv = float(error_permitido) if error_permitido is not None else 0.0
        
        # Crear DataFrame del resumen
        resumen_data = [
            {"Descripción": "Título", "Valor": titulo},
            {"Descripción": "Función original", "Valor": str(funcion)},
            {"Descripción": "Método", "Valor": metodo},
            {"Descripción": "Error permitido (%)", "Valor": error_permitido_conv},
            {"Descripción": "Raíz aproximada", "Valor": raiz_conv},
            {"Descripción": "Error final (%)", "Valor": error_final_conv},
            {"Descripción": "Número de iteraciones", "Valor": len(iteraciones) if iteraciones else 0},
        ]
        
        # Preparar datos de iteraciones
        iteraciones_conv = []
        if iteraciones:
            for fila in iteraciones:
                fila_conv = {}
                for clave, valor in fila.items():
                    fila_conv[str(clave)] = _convertir_valor(valor)
                iteraciones_conv.append(fila_conv)
        
        # Crear archivo Excel
        with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
            # Hoja de resumen
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(escritor, sheet_name="Resumen", index=False)
            
            # Hoja de iteraciones
            if iteraciones_conv:
                df_iteraciones = pd.DataFrame(iteraciones_conv)
                df_iteraciones.to_excel(escritor, sheet_name="Iteraciones", index=False)
            
            # Hoja de descripción
            descripcion_data = [
                {"Sección": "Método", "Detalle": metodo},
                {"Sección": "Función", "Detalle": str(funcion)},
                {"Sección": "Criterio de parada", "Detalle": f"Error permitido: {error_permitido_conv}%"},
                {"Sección": "Raíz encontrada", "Detalle": f"{raiz_conv:.10f}"},
                {"Sección": "Error final", "Detalle": f"{error_final_conv}%"},
                {"Sección": "Interpretación", "Detalle": "La raíz es el valor de x donde f(x) = 0 o está cercano a él."},
            ]
            df_descripcion = pd.DataFrame(descripcion_data)
            df_descripcion.to_excel(escritor, sheet_name="Descripción", index=False)
            
            # Formatear hojas
            for sheet_name in escritor.sheets:
                ws = escritor.sheets[sheet_name]
                for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
                    for cell in row:
                        if cell.row == 1:
                            cell.font = Font(bold=True, color="FFFFFF")
                            cell.fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
                        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                
                # Ajustar ancho de columnas
                for col in ws.columns:
                    max_length = 0
                    col_letter = col[0].column_letter
                    for cell in col:
                        if len(str(cell.value or "")) > max_length:
                            max_length = len(str(cell.value or ""))
                    ws.column_dimensions[col_letter].width = min(max_length + 2, 50)
        
        return salida.getvalue()
    
    except Exception as exc:
        # Log del error para debugging
        print(f"Error al crear Excel: {exc}", flush=True)
        raise ValueError(f"Error al preparar el archivo Excel: {str(exc)}") from exc
