"""
Módulo de análisis cualitativo usando GPT-4o.
Extrae variables de investigación sobre burocracia de la calle de transcripciones.
"""

import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from openai import OpenAI, APIError, RateLimitError, APIConnectionError

from config import (
    OPENAI_API_KEY,
    GPT_MODEL,
    TEMPERATURA_GPT,
    MAX_TOKENS,
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

# System prompt para el análisis
SYSTEM_PROMPT = """Eres un asistente especializado en análisis cualitativo de ciencia política.
Tu tarea es analizar transcripciones de entrevistas a burócratas de primera línea
(trabajadores sociales, funcionarios municipales, operadores de programas sociales)
que implementan políticas dirigidas al adulto mayor.

Debes identificar evidencia de las siguientes dimensiones analíticas y responder
SIEMPRE en formato JSON válido con la estructura exacta que se te solicite.

Para cada indicador:
- "presente": true/false
- "cita": fragmento textual exacto de la entrevista que evidencia el indicador (o null si no aplica)
- "intensidad": "baja", "media" o "alta" según qué tan explícita y recurrente es la evidencia

Sé riguroso: solo marca como presente lo que esté explícitamente respaldado por el texto."""


def generar_prompt_analisis(transcripcion: str) -> str:
    """
    Genera el prompt específico para analizar una transcripción.

    Args:
        transcripcion: Texto de la transcripción

    Returns:
        Prompt formateado para GPT-4o
    """

    prompt = f"""Analiza la siguiente transcripción de entrevista con un burócrata de primera línea que implementa políticas sociales para adultos mayores.

TRANSCRIPCIÓN:
---
{transcripcion[:8000]}  # Limitar a 8000 caracteres para no exceder contexto
---

Responde en JSON válido con esta estructura EXACTA:

{{
    "D1_discrecionalidad": {{
        "presente": boolean,
        "indicadores": {{
            "interpretacion_flexible": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "decisiones_caso_por_caso": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "adaptacion_requisitos": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "priorizacion_informal": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}}
        }},
        "intensidad_global": "baja"|"media"|"alta"
    }},
    "D2_rutinizacion": {{
        "presente": boolean,
        "indicadores": {{
            "simplificacion_tramites": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "estandarizacion_atencion": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "categorias_informales": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "reduccion_tiempo": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}}
        }},
        "intensidad_global": "baja"|"media"|"alta"
    }},
    "D3_racionamiento": {{
        "presente": boolean,
        "indicadores": {{
            "barreras_informales": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "derivaciones_reiteradas": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "seleccion_implicita": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "postergacion_complejos": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}}
        }},
        "intensidad_global": "baja"|"media"|"alta"
    }},
    "D4_relacion": {{
        "presente": boolean,
        "indicadores": {{
            "trato_vertical_horizontal": {{"presente": boolean, "tipo": "vertical"|"horizontal"|"mixto", "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "nivel_escucha": {{"presente": boolean, "nivel": "bajo"|"medio"|"alto", "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "reconocimiento_autonomia": {{"presente": boolean, "cita": string|null, "intensidad": "baja"|"media"|"alta"}},
            "construccion_adulto_mayor": {{"presente": boolean, "categoria": "cliente"|"beneficiario"|"sujeto_vulnerable"|"mixto", "cita": string|null, "intensidad": "baja"|"media"|"alta"}}
        }},
        "intensidad_global": "baja"|"media"|"alta"
    }},
    "notas_generales": "Observaciones adicionales sobre el análisis"
}}

Importante: Responde SOLO con el JSON válido, sin explicaciones adicionales."""

    return prompt


def analizar_transcripcion(
    archivo_audio: Path,
    transcripcion: str = None,
    forzar: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Analiza una transcripción usando GPT-4o.
    Implementa reintentos con backoff exponencial.

    Args:
        archivo_audio: Ruta del archivo de audio original
        transcripcion: Texto de la transcripción (si None, se carga del archivo)
        forzar: Si True, ignora análisis previos

    Returns:
        Diccionario con resultados del análisis, o None si falla
    """

    # Cargar transcripción si no se proporciona
    if transcripcion is None:
        archivo_transcripcion = TRANSCRIPCIONES_DIR / f"{archivo_audio.stem}.txt"
        if not archivo_transcripcion.exists():
            logger.error(f"Transcripción no encontrada: {archivo_transcripcion}")
            return None
        transcripcion = archivo_transcripcion.read_text(encoding="utf-8")

    if VERBOSE:
        print(f"🔍 Analizando: {archivo_audio.name}")

    # Generar prompt
    prompt = generar_prompt_analisis(transcripcion)

    # Reintentos con backoff exponencial
    espera = ESPERA_INICIAL

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            respuesta = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURA_GPT,
                max_tokens=MAX_TOKENS,
            )

            # Extraer JSON de la respuesta
            contenido = respuesta.choices[0].message.content.strip()

            # Parsear JSON
            resultado = json.loads(contenido)

            # Agregar metadatos
            resultado["id_entrevista"] = archivo_audio.stem
            resultado["archivo_original"] = archivo_audio.name
            resultado["longitud_transcripcion"] = len(transcripcion)

            if VERBOSE:
                print(f"✓ Análisis completado: {archivo_audio.name}")

            logger.info(f"Análisis exitoso: {archivo_audio.name}")
            return resultado

        except json.JSONDecodeError as e:
            error_msg = f"Error al parsear JSON: {e}"
            print(f"✗ {error_msg}")
            logger.error(f"{archivo_audio.name}: {error_msg}")
            # Intentar nuevamente
            if intento < MAX_REINTENTOS:
                time.sleep(espera)
                espera *= FACTOR_BACKOFF
                continue
            return None

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

        except Exception as e:
            error_msg = f"Error inesperado: {e}"
            print(f"✗ {error_msg}")
            logger.error(f"{archivo_audio.name}: {error_msg}")
            return None

    return None


def analizar_todas_transcripciones(forzar: bool = False) -> list[Dict]:
    """
    Analiza todas las transcripciones en el directorio.

    Args:
        forzar: Si True, re-analiza todos los archivos

    Returns:
        Lista de resultados de análisis
    """

    archivos_transcripciones = sorted(TRANSCRIPCIONES_DIR.glob("*.txt"))

    if not archivos_transcripciones:
        print("No se encontraron transcripciones para analizar.")
        return []

    resultados = []

    for archivo_transcripcion in archivos_transcripciones:
        # Reconstruir ruta del archivo de audio original
        # (Aquí simplemente usamos el nombre del archivo de transcripción)
        archivo_audio = Path(archivo_transcripcion.stem)

        analisis = analizar_transcripcion(archivo_audio)

        if analisis:
            resultados.append(analisis)
        else:
            print(f"⚠ Análisis fallido: {archivo_transcripcion.name}")

    print(f"\n📊 Resumen: {len(resultados)}/{len(archivos_transcripciones)} análisis completados")

    return resultados
