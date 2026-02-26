#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba - Genera un audio de prueba y verifica que todo funciona.

Este script es útil para verificar que la configuración está correcta
sin necesidad de archivos de audio reales.

Uso:
    python test_con_audio_corto.py
"""

import sys
import io
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from datetime import datetime
import json

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from config import AUDIO_DIR, TRANSCRIPCIONES_DIR, RESULTADOS_DIR, OPENAI_API_KEY
from transcribir import transcribir_audio, procesar_todos_audios
from analizar import analizar_transcripcion, analizar_todas_transcripciones
from exportar import generar_tabla_excel, generar_tabla_csv, guardar_json_resultados


def crear_audio_prueba():
    """
    Crea un archivo de audio de prueba usando text-to-speech.
    (Requiere tts-1 model de OpenAI)

    NOTA: Para simplificar las pruebas, este script usa texto directo
    en lugar de generar un audio real.
    """

    print("📝 Creando archivo de prueba...\n")

    # Texto de prueba - Simulación de una entrevista sobre burocracia de la calle
    texto_prueba = """
    Entrevistadora: Buenos días, gracias por participar. Quisiera preguntarle sobre su experiencia
    atendiendo a adultos mayores en este programa social.

    Burócrata: Claro, con gusto. Mire, aquí en la municipalidad atendemos a muchos adultos mayores.
    Aunque el reglamento dice que necesitan ciertos documentos, la verdad es que muchos vienen sin nada
    porque perdieron los papeles o viven en la calle. Entonces uno los atiende de todas formas.

    Entrevistadora: ¿Y cómo decide a quién ayuda?

    Burócrata: Bueno, depende del caso. Si veo que la persona necesita algo urgente, como medicinas,
    trato de que se lo den rápido. A veces saltamos pasos, ¿vea? Los que tienen mejor apariencia
    y saben cómo hablar, les es más fácil. A los que están confundidos o tienen problemas mentales,
    les cuesta más avanzar. Terminan yendo de un lado a otro sin resolver nada.

    Entrevistadora: ¿Usted cree que eso es justo?

    Burócrata: Honestamente, no. Pero como funcionario, debo procesar casos rápidamente.
    Si todos los adultos mayores viniera con todos los papeles en orden, sería diferente.
    Entonces adapto los requisitos según la situación. Es la única forma de que funcione.

    Entrevistadora: ¿Y los casos complejos?

    Burócrata: Los casos complejos se postergan. Si alguien tiene múltiples problemas de salud,
    o no tiene familia, o hay conflictiva legal, eso toma mucho tiempo. Entonces los derivamos
    a otras instituciones, aunque a veces no responden.
    """

    # Guardar como archivo de texto para prueba (no es audio real)
    archivo_prueba = AUDIO_DIR / "test_entrevista.txt"
    archivo_prueba.write_text(texto_prueba, encoding="utf-8")

    # Crear un "pseudo-audio" copiando el texto
    archivo_audio_prueba = AUDIO_DIR / "test_entrevista.mp3"

    print(f"✓ Archivo de prueba creado: {archivo_prueba.name}")
    print(f"  (Nota: Para pruebas reales, coloca archivos .mp3, .wav, .m4a en la carpeta audio/)\n")

    return texto_prueba


def test_conexion_api():
    """Verifica que la API key esté configurada correctamente."""

    print("🔐 Verificando configuración de OpenAI API...")

    if not OPENAI_API_KEY:
        print("✗ OPENAI_API_KEY no está configurada")
        print("  Ejecuta: export OPENAI_API_KEY='sk-xxxxxxxxxxxx'")
        return False

    if not OPENAI_API_KEY.startswith("sk-"):
        print("⚠ OPENAI_API_KEY no tiene formato válido (debe empezar con 'sk-')")
        return False

    print("✓ OPENAI_API_KEY configurada correctamente\n")
    return True


def test_directorios():
    """Verifica que los directorios necesarios existan."""

    print("📁 Verificando estructura de directorios...")

    directorios = [
        ("audio/", AUDIO_DIR),
        ("transcripciones/", TRANSCRIPCIONES_DIR),
        ("resultados/", RESULTADOS_DIR),
    ]

    for nombre, ruta in directorios:
        if ruta.exists():
            print(f"✓ Encontrado: {nombre}")
        else:
            print(f"✗ No encontrado: {nombre}")
            return False

    print()
    return True


def test_analisis_manual():
    """Prueba el análisis con un texto de ejemplo sin usar la API."""

    print("🔬 Prueba de análisis con texto de ejemplo...\n")

    texto_ejemplo = """
    Entrevistadora: ¿Cómo atiende a los adultos mayores que llegan sin documentos?

    Burócrata: Bueno, la norma dice que necesitan cédula y certificado de pobreza.
    Pero muchos vienen sin nada. Entonces los atiendo igual, pero les explico que es más lento.
    A veces dejo que pasen aunque no tengan todo en orden.

    Entrevistadora: ¿Todos reciben la misma atención?

    Burócrata: No, algunos casos son más urgentes. Los que veo que están muy enfermos o solos
    trato de procesarlos rápido. Los otros esperan más. Es lo que puedo hacer con los recursos
    que tengo. A veces los refiero a otras instituciones para que se acelere el proceso.
    """

    # Crear análisis simulado (sin llamar a GPT, para no usar API)
    analisis_simulado = {
        "id_entrevista": "test_entrevista",
        "archivo_original": "test_entrevista.mp3",
        "longitud_transcripcion": len(texto_ejemplo),
        "D1_discrecionalidad": {
            "presente": True,
            "indicadores": {
                "interpretacion_flexible": {
                    "presente": True,
                    "cita": "A veces dejo que pasen aunque no tengan todo en orden",
                    "intensidad": "media"
                },
                "decisiones_caso_por_caso": {
                    "presente": True,
                    "cita": "Algunos casos son más urgentes",
                    "intensidad": "alta"
                },
                "adaptacion_requisitos": {
                    "presente": True,
                    "cita": "Los atiendo igual, pero les explico que es más lento",
                    "intensidad": "media"
                },
                "priorizacion_informal": {
                    "presente": True,
                    "cita": "Los que veo que están muy enfermos o solos trato de procesarlos rápido",
                    "intensidad": "alta"
                }
            },
            "intensidad_global": "media"
        },
        "D2_rutinizacion": {
            "presente": True,
            "indicadores": {
                "simplificacion_tramites": {
                    "presente": True,
                    "cita": "Pero los atiendo igual, aunque no tengan todo en orden",
                    "intensidad": "baja"
                },
                "estandarizacion_atencion": {
                    "presente": False,
                    "cita": None,
                    "intensidad": "baja"
                },
                "categorias_informales": {
                    "presente": False,
                    "cita": None,
                    "intensidad": "baja"
                },
                "reduccion_tiempo": {
                    "presente": True,
                    "cita": "Trato de procesarlos rápido",
                    "intensidad": "media"
                }
            },
            "intensidad_global": "baja"
        },
        "D3_racionamiento": {
            "presente": True,
            "indicadores": {
                "barreras_informales": {
                    "presente": True,
                    "cita": "Necesitan cédula y certificado de pobreza",
                    "intensidad": "media"
                },
                "derivaciones_reiteradas": {
                    "presente": True,
                    "cita": "A veces los refiero a otras instituciones",
                    "intensidad": "baja"
                },
                "seleccion_implicita": {
                    "presente": True,
                    "cita": "Los otros esperan más",
                    "intensidad": "media"
                },
                "postergacion_complejos": {
                    "presente": False,
                    "cita": None,
                    "intensidad": "baja"
                }
            },
            "intensidad_global": "media"
        },
        "D4_relacion": {
            "presente": True,
            "indicadores": {
                "trato_vertical_horizontal": {
                    "presente": True,
                    "tipo": "vertical",
                    "cita": "Les explico que es más lento",
                    "intensidad": "baja"
                },
                "nivel_escucha": {
                    "presente": True,
                    "nivel": "bajo",
                    "cita": None,
                    "intensidad": "baja"
                },
                "reconocimiento_autonomia": {
                    "presente": False,
                    "cita": None,
                    "intensidad": "baja"
                },
                "construccion_adulto_mayor": {
                    "presente": True,
                    "categoria": "sujeto_vulnerable",
                    "cita": "Los que están muy enfermos o solos",
                    "intensidad": "media"
                }
            },
            "intensidad_global": "baja"
        },
        "notas_generales": "Entrevista de prueba que muestra patrones de discrecionalidad y racionamiento de acceso."
    }

    print("✓ Análisis simulado creado (sin llamar a API)\n")

    return [analisis_simulado]


def main():
    """Función principal de prueba."""

    print("\n" + "=" * 60)
    print("  TEST DE CONFIGURACIÓN")
    print("  Herramienta de Análisis Cualitativo")
    print("=" * 60 + "\n")

    # Test 1: Verificar API
    if not test_conexion_api():
        print("❌ La configuración de API no es correcta. Abortando.")
        sys.exit(1)

    # Test 2: Verificar directorios
    if not test_directorios():
        print("❌ Estructura de directorios incompleta. Abortando.")
        sys.exit(1)

    # Test 3: Crear archivo de prueba
    texto = crear_audio_prueba()

    # Test 4: Análisis simulado (sin usar API)
    print("📊 Generando análisis de prueba (sin llamar a OpenAI API)...\n")
    resultados = test_analisis_manual()

    # Test 5: Exportar resultados
    print("💾 Exportando resultados de prueba...\n")

    generar_tabla_excel(resultados, "Test_Analisis.xlsx")
    generar_tabla_csv(resultados, "Test_Analisis.csv")
    guardar_json_resultados(resultados, "Test_Analisis.json")

    # Resumen
    print("\n" + "=" * 60)
    print("  ✓ PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("\n📝 Próximos pasos:\n")
    print("1. Verifica los archivos en resultados/:")
    print("   - Test_Analisis.xlsx")
    print("   - Test_Analisis.csv")
    print("   - Test_Analisis.json")
    print("\n2. Para procesar audios reales:")
    print("   - Coloca archivos .mp3, .wav, .m4a, etc. en la carpeta 'audio/'")
    print("   - Ejecuta: python main.py")
    print("\n3. Consulta README.md para más información")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⊘ Prueba interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
