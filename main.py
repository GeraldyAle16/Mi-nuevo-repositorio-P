"""
Script principal - Herramienta de análisis cualitativo de entrevistas.

Uso:
    python main.py                              # Procesa todos los audios
    python main.py --audio archivo.mp3         # Procesa un audio específico
    python main.py --solo-transcribir           # Solo transcribe sin analizar
    python main.py --reanalizar                 # Re-analiza sin re-transcribir
    python main.py --help                       # Muestra esta ayuda
"""

import argparse
import sys
from pathlib import Path

from config import AUDIO_DIR, VERBOSE
from transcribir import procesar_todos_audios, transcribir_audio, cargar_transcripcion
from analizar import analizar_transcripcion, analizar_todas_transcripciones
from exportar import generar_tabla_excel, generar_tabla_csv, guardar_json_resultados


def main():
    """Función principal con interfaz CLI."""

    parser = argparse.ArgumentParser(
        description="Herramienta de análisis cualitativo para investigación en ciencia política.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
    python main.py                          # Procesa todos los audios
    python main.py --audio miarchivo.mp3   # Procesa un archivo específico
    python main.py --solo-transcribir       # Solo transcribe
    python main.py --reanalizar             # Re-analiza transcripciones existentes
    python main.py --forzar --audio file.mp3  # Fuerza re-transcripción
        """
    )

    parser.add_argument(
        "--audio",
        type=str,
        help="Procesa un archivo de audio específico"
    )

    parser.add_argument(
        "--solo-transcribir",
        action="store_true",
        help="Solo transcribe sin analizar"
    )

    parser.add_argument(
        "--reanalizar",
        action="store_true",
        help="Re-analiza transcripciones existentes sin re-transcribir"
    )

    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Fuerza re-transcripción/re-análisis de archivos existentes"
    )

    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="No genera archivo Excel (solo CSV y JSON)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Muestra información detallada de depuración"
    )

    args = parser.parse_args()

    # Banner
    print("\n" + "=" * 60)
    print("  ANÁLISIS CUALITATIVO DE ENTREVISTAS")
    print("  Burocracia de la Calle - Políticas Sociales Adulto Mayor")
    print("=" * 60 + "\n")

    try:
        # MODO 1: Procesar archivo específico
        if args.audio:
            archivo = Path(args.audio)

            if not archivo.is_file():
                # Buscar en directorio AUDIO_DIR
                archivo = AUDIO_DIR / args.audio

            if not archivo.is_file():
                print(f"✗ Archivo no encontrado: {args.audio}")
                sys.exit(1)

            print(f"📁 Procesando archivo: {archivo.name}\n")

            # Transcribir
            transcripcion = transcribir_audio(archivo, forzar=args.forzar)

            if not transcripcion:
                print("✗ Error en transcripción. Abortando.")
                sys.exit(1)

            if args.solo_transcribir:
                print("\n✓ Transcripción completada (análisis omitido)")
                sys.exit(0)

            # Analizar
            analisis = analizar_transcripcion(archivo, transcripcion)

            if not analisis:
                print("✗ Error en análisis. Abortando.")
                sys.exit(1)

            # Exportar
            print("\n📊 Exportando resultados...")
            if not args.no_excel:
                generar_tabla_excel([analisis])
            generar_tabla_csv([analisis])
            guardar_json_resultados([analisis])

            print("\n✓ Procesamiento completado")

        # MODO 2: Solo re-analizar
        elif args.reanalizar:
            print("🔄 Re-analizando todas las transcripciones...\n")

            resultados = analizar_todas_transcripciones(forzar=args.forzar)

            if not resultados:
                print("✗ No se pudieron completar los análisis.")
                sys.exit(1)

            # Exportar
            print("\n📊 Exportando resultados...")
            if not args.no_excel:
                generar_tabla_excel(resultados)
            generar_tabla_csv(resultados)
            guardar_json_resultados(resultados)

            print("\n✓ Procesamiento completado")

        # MODO 3: Solo transcribir
        elif args.solo_transcribir:
            print("🎙️  Transcribiendo todos los audios...\n")

            resultados = procesar_todos_audios(forzar=args.forzar)

            if resultados["exitosos"] == 0:
                print("✗ No se pudieron transcribir audios.")
                sys.exit(1)

            print("\n✓ Transcripción completada")

        # MODO 4: Procesar todo (default)
        else:
            print("🎙️  Transcribiendo audios...\n")
            resultados_trans = procesar_todos_audios(forzar=args.forzar)

            if resultados_trans["exitosos"] == 0:
                print("✗ No se pudieron transcribir audios.")
                sys.exit(1)

            print("\n🔍 Analizando transcripciones...\n")
            resultados_analisis = analizar_todas_transcripciones(forzar=args.forzar)

            if not resultados_analisis:
                print("✗ No se pudieron completar los análisis.")
                sys.exit(1)

            # Exportar
            print("\n📊 Exportando resultados...")
            if not args.no_excel:
                generar_tabla_excel(resultados_analisis)
            generar_tabla_csv(resultados_analisis)
            guardar_json_resultados(resultados_analisis)

            print("\n✓ Procesamiento completado")

    except KeyboardInterrupt:
        print("\n⊘ Proceso interrumpido por el usuario")
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
