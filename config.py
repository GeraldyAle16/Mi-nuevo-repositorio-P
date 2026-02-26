"""
Configuración central para el sistema de análisis de entrevistas.
Define API keys, modelos, parámetros y rutas.
"""

import os
from pathlib import Path

# ==================== CONFIGURACIÓN DE API ====================
# Cargar API key desde variable de entorno (MÁS SEGURO)
# Si no está definida, intentar usar valor directo (NO RECOMENDADO en producción)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not OPENAI_API_KEY:
    raise ValueError(
        "⚠️  OPENAI_API_KEY no está configurada.\n"
        "Por favor, ejecuta: export OPENAI_API_KEY='tu-api-key-aqui'\n"
        "O establece la variable de entorno en tu sistema."
    )

# ==================== MODELOS DE OpenAI ====================
WHISPER_MODEL = "whisper-1"  # Modelo de transcripción
GPT_MODEL = "gpt-4o"  # Modelo de análisis
IDIOMA_AUDIO = "es"  # Español

# ==================== PARÁMETROS DE GPT ====================
TEMPERATURA_GPT = 0.1  # Baja temperatura para análisis más consistente
MAX_TOKENS = 4000  # Máximo de tokens en respuesta

# ==================== RUTAS DE PROYECTO ====================
PROJECT_ROOT = Path(__file__).parent.absolute()
AUDIO_DIR = PROJECT_ROOT / "audio"
TRANSCRIPCIONES_DIR = PROJECT_ROOT / "transcripciones"
RESULTADOS_DIR = PROJECT_ROOT / "resultados"

# Crear directorios si no existen
for directory in [AUDIO_DIR, TRANSCRIPCIONES_DIR, RESULTADOS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==================== PARÁMETROS DE REINTENTOS ====================
MAX_REINTENTOS = 3
ESPERA_INICIAL = 1  # segundos
FACTOR_BACKOFF = 2  # multiplicador exponencial

# ==================== ESQUEMA DE CODIFICACIÓN ====================
# Dimensiones y sus indicadores (para referencia y validación)
DIMENSIONES = {
    "D1_discrecionalidad": {
        "nombre": "Uso de la discrecionalidad",
        "indicadores": [
            "interpretacion_flexible",
            "decisiones_caso_por_caso",
            "adaptacion_requisitos",
            "priorizacion_informal",
        ]
    },
    "D2_rutinizacion": {
        "nombre": "Estrategias de rutinización",
        "indicadores": [
            "simplificacion_tramites",
            "estandarizacion_atencion",
            "categorias_informales",
            "reduccion_tiempo",
        ]
    },
    "D3_racionamiento": {
        "nombre": "Racionamiento del acceso",
        "indicadores": [
            "barreras_informales",
            "derivaciones_reiteradas",
            "seleccion_implicita",
            "postergacion_complejos",
        ]
    },
    "D4_relacion": {
        "nombre": "Relación burócrata–adulto mayor",
        "indicadores": [
            "trato_vertical_horizontal",
            "nivel_escucha",
            "reconocimiento_autonomia",
            "construccion_adulto_mayor",
        ]
    },
}

# ==================== AJUSTES DE LOGGING ====================
VERBOSE = True  # Mostrar más detalles en consola
LOG_FILE = PROJECT_ROOT / "analisis.log"
