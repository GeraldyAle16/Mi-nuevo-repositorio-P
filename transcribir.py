"""
Módulo de transcripción de audio usando la API de Whisper de OpenAI.
Convierte archivos de audio a texto con reintentos automáticos.
"""

import time
from pathlib import Path
from typing import Optional, Tuple
import logging

from openai import OpenAI, APIError, RateLimitError, APIConnectionError

from config import (
    OPENAI_API_KEY,
    WHISPER_MODEL,
    IDIOMA_AUDIO,
    TRANSCRIPCIONES_DIR,
    MAX_REINTENTOS,
    ESPERA_INICIAL,
    FACTOR_BACKOFF,
    VERBOSE,
    LOG_FILE,
)

# Configurar logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Inicializar cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Formatos de audio soportados por Whisper
AUDIO_FORMATS = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"}


def obtener_archivos_audio(directorio: Path) -> list[Path]:
    """
    Obtiene lista de archivos de audio en el directorio especificado.

    Args:
        directorio: Ruta del directorio a escanear

    Returns:
        Lista de rutas a archivos de audio
    """
    if not directorio.exists():
        logger.warning(f"Directorio no existe: {directorio}")
        return []

    archivos = [
        f for f in directorio.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_FORMATS
    ]

    if VERBOSE:
        print(f"✓ Encontrados {len(archivos)} archivo(s) de audio")

    return sorted(archivos)


def ya_transcrito(archivo_audio: Path) -> bool:
    """
    Verifica si un archivo de audio ya ha sido transcrito.

    Args:
        archivo_audio: Ruta al archivo de audio

    Returns:
        True si el archivo de transcripción ya existe
    """
    archivo_transcripcion = TRANSCRIPCIONES_DIR / f"{archivo_audio.stem}.txt"
    return archivo_transcripcion.exists()


def transcribir_audio(
    archivo_audio: Path,
    forzar: bool = False
) -> Optional[str]:
    """
    Transcribe un archivo de audio usando la API de Whisper.
    Implementa reintentos con backoff exponencial.

    Args:
        archivo_audio: Ruta al archivo de audio
        forzar: Si True, ignora transcripciones previas

    Returns:
        Texto de la transcripción, o None si falla
    """

    # Verificar si ya existe transcripción
    if ya_transcrito(archivo_audio) and not forzar:
        if VERBOSE:
            print(f"⊘ {archivo_audio.name} ya estaba transcrito (saltando)")
        logger.info(f"Archivo ya transcrito: {archivo_audio.name}")
        return cargar_transcripcion(archivo_audio)

    if VERBOSE:
        print(f"↻ Transcribiendo: {archivo_audio.name}")

    # Reintentos con backoff exponencial
    espera = ESPERA_INICIAL

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            with open(archivo_audio, "rb") as audio_file:
                transcripcion = client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=audio_file,
                    language=IDIOMA_AUDIO,
                    response_format="text"
                )

            # Guardar transcripción
            archivo_transcripcion = TRANSCRIPCIONES_DIR / f"{archivo_audio.stem}.txt"
            archivo_transcripcion.write_text(transcripcion, encoding="utf-8")

            if VERBOSE:
                print(f"✓ Transcripción guardada: {archivo_transcripcion.name}")

            logger.info(f"Transcripción exitosa: {archivo_audio.name}")
            return transcripcion

        except (RateLimitError, APIConnectionError) as e:
            if intento < MAX_REINTENTOS:
                if VERBOSE:
                    print(f"  ⚠ Reintento {intento}/{MAX_REINTENTOS} en {espera}s...")
                time.sleep(espera)
                espera *= FACTOR_BACKOFF
                continue
            else:
                error_msg = f"Error de API después de {MAX_REINTENTOS} intentos: {e}"
                print(f"✗ {error_msg}")
                logger.error(f"{archivo_audio.name}: {error_msg}")
                return None

        except APIError as e:
            error_msg = f"Error de OpenAI API: {e}"
            print(f"✗ {error_msg}")
            logger.error(f"{archivo_audio.name}: {error_msg}")
            return None

        except FileNotFoundError:
            error_msg = f"Archivo no encontrado: {archivo_audio}"
            print(f"✗ {error_msg}")
            logger.error(error_msg)
            return None

        except Exception as e:
            error_msg = f"Error inesperado: {e}"
            print(f"✗ {error_msg}")
            logger.error(f"{archivo_audio.name}: {error_msg}")
            return None

    return None


def cargar_transcripcion(archivo_audio: Path) -> str:
    """
    Carga una transcripción guardada previamente.

    Args:
        archivo_audio: Ruta al archivo de audio original

    Returns:
        Texto de la transcripción
    """
    archivo_transcripcion = TRANSCRIPCIONES_DIR / f"{archivo_audio.stem}.txt"

    if archivo_transcripcion.exists():
        return archivo_transcripcion.read_text(encoding="utf-8")

    return ""


def procesar_todos_audios(
    directorio: Path = None,
    forzar: bool = False
) -> dict:
    """
    Procesa todos los archivos de audio en el directorio especificado.

    Args:
        directorio: Directorio con audios (default: AUDIO_DIR)
        forzar: Si True, re-transcribe todos los audios

    Returns:
        Diccionario con resultados del procesamiento
    """
    if directorio is None:
        from config import AUDIO_DIR
        directorio = AUDIO_DIR

    archivos = obtener_archivos_audio(directorio)

    if not archivos:
        print("No se encontraron archivos de audio para procesar.")
        return {"total": 0, "exitosos": 0, "fallidos": 0}

    resultados = {"total": len(archivos), "exitosos": 0, "fallidos": 0, "detalles": {}}

    for archivo in archivos:
        transcripcion = transcribir_audio(archivo, forzar=forzar)

        if transcripcion:
            resultados["exitosos"] += 1
            resultados["detalles"][archivo.name] = "exitoso"
        else:
            resultados["fallidos"] += 1
            resultados["detalles"][archivo.name] = "fallido"

    print(f"\n📊 Resumen: {resultados['exitosos']}/{resultados['total']} transcripciones completadas")

    return resultados
