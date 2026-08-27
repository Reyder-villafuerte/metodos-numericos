from io import BytesIO
import pandas as pd


def crear_excel(titulo, funcion, metodo, parametros, error_permitido, raiz, error_final, iteraciones):
    salida = BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        resumen = pd.DataFrame([[titulo], ["Función", funcion], ["Método", metodo], ["Parámetros iniciales", parametros], ["Error permitido (%)", error_permitido], ["Raíz aproximada", raiz], ["Error final (%)", error_final]], columns=["Resultado"])
        resumen.to_excel(escritor, sheet_name="Resumen", index=False, header=False)
        pd.DataFrame(iteraciones).to_excel(escritor, sheet_name="Iteraciones", index=False)
    return salida.getvalue()
