#!/usr/bin/env python3
"""
Script de validación manual de la integración OCR en app.py

Este script documenta la secuencia de pruebas que debe ejecutarse manualmente
en la interfaz de Streamlit para validar el comportamiento correcto del ingreso
mediante imágenes.

SECUENCIA DE PRUEBAS:
====================

A. INICIO (sin imagen):
   - Selector: "Escribir función manualmente" ✓
   - Campo f(x): VACÍO ✓
   - Mensaje: Ninguno
   - Resultado esperado: La app funciona normalmente con el campo vacío

B. CAMBIO A MODO IMAGEN:
   - Selector: cambiar a "Subir una imagen" ✓
   - Campo f(x): DEBE QUEDAR VACÍO (limpieza de modo manual)
   - Mensaje: "Suba una imagen para detectar la función."
   - Resultado esperado: No hay restos de la función manual

C. CARGAR IMAGEN 1 (f(x)=1-x^2-arctan(x)):
   - Archivo: imagen_prueba_1.png
   - OCR se ejecuta automáticamente
   - Campo f(x): SE LLENA CON "1-x^2-arctan(x)" ✓
   - Mensaje: "Función detectada automáticamente. Revísela y confirme." ✓
   - Checkbox: "Confirmo que la función..." (desmarcado)
   - Resultado esperado: El usuario ve la función detectada y puede confirmar

D. CONFIRMAR FUNCIÓN:
   - Checkbox: marcar confirmación ✓
   - Mensaje persiste
   - Resultado esperado: Ahora se puede hacer clic en "Resolver"

E. ELIMINAR IMAGEN (hacer clic en X):
   - Archivo: Se elimina del uploader
   - Campo f(x): DEBE QUEDAR VACÍO ✓
   - Hash: Se borra de session_state
   - Confirmación: Se desmarca
   - Mensaje: "Suba una imagen para detectar la función."
   - Resultado esperado: Limpieza completa del estado OCR

F. CARGAR IMAGEN 2 (f(x)=exp(-x)-x):
   - Archivo: imagen_prueba_2.png
   - OCR se ejecuta automáticamente (diferente hash)
   - Campo f(x): SE LLENA CON "exp(-x)-x" (reemplaza anterior) ✓
   - Mensaje: "Función detectada automáticamente. Revísela y confirme." ✓
   - Confirmación: Desmarcada (reiniciada)
   - Resultado esperado: Nueva función detectada, estado anterior limpiado

G. CAMBIAR A MODO MANUAL:
   - Selector: cambiar a "Escribir función manualmente" ✓
   - Campo f(x): DEBE QUEDAR VACÍO ✓
   - Hash y OCR state: Se limpian
   - Mensaje OCR: Desaparece
   - Resultado esperado: Regresa al modo manual limpio

H. VOLVER A MODO IMAGEN (sin cargar archivo):
   - Selector: cambiar a "Subir una imagen" ✓
   - Campo f(x): VACÍO ✓
   - Mensaje: "Suba una imagen para detectar la función."
   - Resultado esperado: No muestra funciones anteriores

VALIDACIONES CLAVE:
===================

✓ 1. Hash SHA-256 diferencia imágenes correctamente
✓ 2. OCR no se re-ejecuta si la imagen no cambió
✓ 3. Cambio de imagen limpia estado anterior
✓ 4. Eliminación de imagen limpia todo
✓ 5. Cambio de modo limpia OCR
✓ 6. Campo f(x) siempre disponible para edición
✓ 7. Confirmación solo aparece en modo imagen
✓ 8. Botón Limpiar vacía todo correctamente

NOTAS TÉCNICAS:
===============

- session_state["funcion_input"] se asigna ANTES de crear st.text_input
- Callback on_change maneja transiciones entre modos
- limpiar_estado_ocr() y limpiar() mantienen estados separados
- El campo text_input nunca asigna a session_state después de instanciarse
- Cada rerun regenera todo con valores correctos del session_state
"""

print(__doc__)

# Validar que las imágenes de prueba existen
import os
from pathlib import Path

directorio = Path(__file__).parent
imagenes_esperadas = [
    "imagen_prueba_1.png",
    "imagen_prueba_2.png",
    "imagen_prueba_3.png"
]

print("\n" + "="*70)
print("VALIDACIÓN DE IMÁGENES DE PRUEBA")
print("="*70)

for imagen in imagenes_esperadas:
    ruta = directorio / imagen
    if ruta.exists():
        tamaño = ruta.stat().st_size
        print(f"✓ {imagen:30} ({tamaño:,} bytes)")
    else:
        print(f"✗ {imagen:30} NO ENCONTRADA")

print("\n" + "="*70)
print("INSTRUCCIONES PARA EJECUTAR PRUEBAS MANUALES")
print("="*70)

print("""
1. En una terminal, ejecutar:
   streamlit run app.py

2. En el navegador (localhost:8502):
   - Seguir la SECUENCIA DE PRUEBAS listada arriba
   - En cada paso, verificar que los resultados coincidan

3. Capturar evidencia:
   - Capturas de pantalla en cada punto clave
   - Logs de la terminal para errores

4. Reportar resultados:
   - Si todo funciona: ✓ PRUEBA EXITOSA
   - Si hay problemas: ✗ Incluir paso, acción y comportamiento actual vs esperado
""")

print("\n" + "="*70)
print("CAMBIOS IMPLEMENTADOS")
print("="*70)

cambios = """
1. Importación de hashlib para cálculo SHA-256
2. Función calcular_hash_imagen() para identificar imágenes únicamente
3. Función limpiar_estado_ocr() para limpiar OCR sin tocar resultado
4. Función callback_cambiar_origen() para manejar transiciones entre modos
5. Función limpiar() mejorada para incluir todos los estados OCR
6. Sección MODO IMAGEN con lógica robusta:
   - Detección de cambio de imagen por hash
   - Ejecución condicional de OCR
   - Asignación a session_state ANTES de text_input
   - Manejo de errores OCR
   - Mensajes informativos
7. Sección MODO MANUAL con limpieza de OCR
8. Ambas secciones usan key="funcion_input" correctamente
9. Checkbox de confirmación solo en modo imagen con imagen cargada
"""

print(cambios)

print("✓ Script de validación completado")
