#!/usr/bin/env python3
"""Script para crear imágenes de prueba con funciones matemáticas."""

from PIL import Image, ImageDraw, ImageFont
import os

def crear_imagen_funcion(texto_funcion, nombre_archivo, ancho=800, alto=200):
    """
    Crea una imagen con el texto de una función matemática.
    
    Args:
        texto_funcion: La función a escribir en la imagen
        nombre_archivo: Nombre del archivo de salida
        ancho: Ancho de la imagen en píxeles
        alto: Alto de la imagen en píxeles
    """
    # Crear imagen con fondo blanco
    imagen = Image.new('RGB', (ancho, alto), color='white')
    draw = ImageDraw.Draw(imagen)
    
    # Intentar usar una fuente monoespaciada (si está disponible)
    try:
        # Fuente de Windows
        fuente = ImageFont.truetype("arial.ttf", 40)
    except:
        try:
            # Fuente alternativa
            fuente = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 40)
        except:
            # Fuente por defecto
            fuente = ImageFont.load_default()
    
    # Calcular posición centrada
    bbox = draw.textbbox((0, 0), texto_funcion, font=fuente)
    ancho_texto = bbox[2] - bbox[0]
    alto_texto = bbox[3] - bbox[1]
    
    x = (ancho - ancho_texto) // 2
    y = (alto - alto_texto) // 2
    
    # Dibujar texto negro sobre fondo blanco
    draw.text((x, y), texto_funcion, fill='black', font=fuente)
    
    # Guardar imagen
    ruta_completa = os.path.join(os.path.dirname(__file__), nombre_archivo)
    imagen.save(ruta_completa)
    print(f"✓ Imagen creada: {ruta_completa}")
    return ruta_completa


if __name__ == "__main__":
    # Crear imágenes de prueba
    crear_imagen_funcion("f(x) = 1 - x^2 - arctan(x)", "imagen_prueba_1.png")
    crear_imagen_funcion("f(x) = exp(-x) - x", "imagen_prueba_2.png")
    crear_imagen_funcion("f(x) = sin(x) - x/2", "imagen_prueba_3.png")
    
    print("\n✓ Imágenes de prueba creadas en la carpeta del proyecto.")
    print("Puede usar estas imágenes para probar la función OCR en la aplicación.")
