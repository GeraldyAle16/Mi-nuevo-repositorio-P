#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para dividir archivos WAV usando la librería estándar.
"""

import sys
import io
import wave
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def dividir_wav(archivo_entrada, duracion_segundos=10*60):
    """
    Divide un archivo WAV en partes.

    Args:
        archivo_entrada: Ruta al archivo WAV
        duracion_segundos: Duración de cada parte en segundos (default: 10 minutos)
    """

    archivo = Path(archivo_entrada)

    if not archivo.exists():
        print(f"✗ Archivo no encontrado: {archivo}")
        return

    print(f"📁 Cargando archivo: {archivo.name}")

    try:
        # Abrir archivo de audio
        with wave.open(str(archivo), 'rb') as audio_entrada:
            # Obtener parámetros
            n_canales = audio_entrada.getnchannels()
            ancho_muestra = audio_entrada.getsampwidth()
            framerate = audio_entrada.getframerate()
            n_frames = audio_entrada.getnframes()

            # Calcular duración
            duracion_total = n_frames / framerate
            tamaño_mb = archivo.stat().st_size / (1024**2)

            print(f"✓ Duración total: {duracion_total / 60:.1f} minutos")
            print(f"✓ Tamaño original: {tamaño_mb:.1f} MB")
            print(f"✓ Framerate: {framerate} Hz")

            # Calcular frames por parte
            frames_por_parte = int(framerate * duracion_segundos)
            num_partes = (n_frames + frames_por_parte - 1) // frames_por_parte

            if num_partes == 1:
                print("✓ El archivo es pequeño, no necesita división")
                return

            print(f"📊 Se crearán {num_partes} partes de ~{duracion_segundos//60} minutos cada una\n")

            # Dividir
            for i in range(num_partes):
                inicio = i * frames_por_parte
                fin = min((i + 1) * frames_por_parte, n_frames)

                # Leer frames
                audio_entrada.setpos(inicio)
                frames = audio_entrada.readframes(fin - inicio)

                # Crear archivo de salida
                nombre_salida = f"{archivo.stem}_parte_{i+1:02d}.wav"
                ruta_salida = archivo.parent / nombre_salida

                print(f"↻ Exportando parte {i+1}/{num_partes}: {nombre_salida}...", end=" ")

                # Escribir archivo
                with wave.open(str(ruta_salida), 'wb') as audio_salida:
                    audio_salida.setnchannels(n_canales)
                    audio_salida.setsampwidth(ancho_muestra)
                    audio_salida.setframerate(framerate)
                    audio_salida.writeframes(frames)

                tamaño_parte = ruta_salida.stat().st_size / (1024**2)
                print(f"✓ ({tamaño_parte:.1f} MB)")

            print(f"\n✓ División completada. Los archivos están en: {archivo.parent}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    archivo = Path("~/Desktop/Analisis_Proteccion_Social/audio/Promotor Jhonatan_Pensión 65.wav").expanduser()

    if archivo.exists():
        dividir_wav(archivo)
    else:
        print(f"✗ No se encontró el archivo: {archivo}")
