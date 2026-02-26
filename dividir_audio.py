#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para dividir archivos de audio grandes en partes más pequeñas.
Necesario cuando el archivo excede el límite de 25 MB de la API Whisper.
"""

import sys
import io
from pathlib import Path
from pydub import AudioSegment

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def dividir_audio(archivo_entrada, duracion_parte_ms=10*60*1000):
    """
    Divide un archivo de audio en partes más pequeñas.

    Args:
        archivo_entrada: Ruta al archivo de audio
        duracion_parte_ms: Duración de cada parte en milisegundos (default: 10 minutos)
    """

    archivo = Path(archivo_entrada)

    if not archivo.exists():
        print(f"✗ Archivo no encontrado: {archivo}")
        return

    print(f"📁 Cargando archivo: {archivo.name}")

    # Detectar formato
    formato = archivo.suffix.lower().lstrip(".")

    try:
        # Cargar audio
        audio = AudioSegment.from_file(str(archivo), format=formato)
        duracion_total = len(audio)

        print(f"✓ Duración total: {duracion_total / 1000 / 60:.1f} minutos")
        print(f"✓ Tamaño original: {archivo.stat().st_size / (1024**2):.1f} MB")

        # Calcular número de partes
        num_partes = (duracion_total + duracion_parte_ms - 1) // duracion_parte_ms

        if num_partes == 1:
            print("✓ El archivo es pequeño, no necesita división")
            return

        print(f"📊 Se crearán {num_partes} partes de ~10 minutos cada una\n")

        # Dividir y exportar
        for i in range(num_partes):
            inicio = i * duracion_parte_ms
            fin = min((i + 1) * duracion_parte_ms, duracion_total)

            parte = audio[inicio:fin]

            # Nombre de archivo
            nombre_salida = f"{archivo.stem}_parte_{i+1:02d}.mp3"
            ruta_salida = archivo.parent / nombre_salida

            # Exportar
            print(f"↻ Exportando parte {i+1}/{num_partes}: {nombre_salida}...", end=" ")
            parte.export(str(ruta_salida), format="mp3", bitrate="192k")

            tamaño_mb = ruta_salida.stat().st_size / (1024**2)
            print(f"✓ ({tamaño_mb:.1f} MB)")

        print(f"\n✓ División completada. Los archivos están en: {archivo.parent}")

    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    # Dividir el archivo de audio grande
    archivo = Path("~/Desktop/Analisis_Proteccion_Social/audio/Promotor Jhonatan_Pensión 65.wav").expanduser()

    if archivo.exists():
        dividir_audio(archivo)
    else:
        print(f"✗ No se encontró el archivo: {archivo}")
