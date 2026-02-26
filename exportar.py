"""
Módulo de exportación de resultados a Excel y CSV.
Convierte los análisis JSON a tablas tabulares.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json
import logging

import pandas as pd

from config import (
    RESULTADOS_DIR,
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


def aplanar_analisis(analisis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte el análisis JSON anidado a un diccionario plano para la tabla.

    Args:
        analisis: Diccionario de análisis con estructura anidada

    Returns:
        Diccionario plano con columnas de la tabla
    """

    fila = {
        "id_entrevista": analisis.get("id_entrevista", ""),
        "archivo_original": analisis.get("archivo_original", ""),
        "fecha_procesamiento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "longitud_transcripcion": analisis.get("longitud_transcripcion", 0),
    }

    # Dimensión 1: Discrecionalidad
    d1 = analisis.get("D1_discrecionalidad", {})
    fila["D1_discrecionalidad_presente"] = "Sí" if d1.get("presente") else "No"

    if d1.get("indicadores"):
        ind = d1["indicadores"]
        fila["D1_interpretacion_flexible"] = "Sí" if ind.get("interpretacion_flexible", {}).get("presente") else "No"
        fila["D1_interpretacion_flexible_cita"] = ind.get("interpretacion_flexible", {}).get("cita") or ""

        fila["D1_decisiones_caso_por_caso"] = "Sí" if ind.get("decisiones_caso_por_caso", {}).get("presente") else "No"
        fila["D1_decisiones_caso_por_caso_cita"] = ind.get("decisiones_caso_por_caso", {}).get("cita") or ""

        fila["D1_adaptacion_requisitos"] = "Sí" if ind.get("adaptacion_requisitos", {}).get("presente") else "No"
        fila["D1_adaptacion_requisitos_cita"] = ind.get("adaptacion_requisitos", {}).get("cita") or ""

        fila["D1_priorizacion_informal"] = "Sí" if ind.get("priorizacion_informal", {}).get("presente") else "No"
        fila["D1_priorizacion_informal_cita"] = ind.get("priorizacion_informal", {}).get("cita") or ""

    fila["D1_intensidad"] = d1.get("intensidad_global", "").capitalize()

    # Dimensión 2: Rutinización
    d2 = analisis.get("D2_rutinizacion", {})
    fila["D2_rutinizacion_presente"] = "Sí" if d2.get("presente") else "No"

    if d2.get("indicadores"):
        ind = d2["indicadores"]
        fila["D2_simplificacion_tramites"] = "Sí" if ind.get("simplificacion_tramites", {}).get("presente") else "No"
        fila["D2_simplificacion_tramites_cita"] = ind.get("simplificacion_tramites", {}).get("cita") or ""

        fila["D2_estandarizacion_atencion"] = "Sí" if ind.get("estandarizacion_atencion", {}).get("presente") else "No"
        fila["D2_estandarizacion_atencion_cita"] = ind.get("estandarizacion_atencion", {}).get("cita") or ""

        fila["D2_categorias_informales"] = "Sí" if ind.get("categorias_informales", {}).get("presente") else "No"
        fila["D2_categorias_informales_cita"] = ind.get("categorias_informales", {}).get("cita") or ""

        fila["D2_reduccion_tiempo"] = "Sí" if ind.get("reduccion_tiempo", {}).get("presente") else "No"
        fila["D2_reduccion_tiempo_cita"] = ind.get("reduccion_tiempo", {}).get("cita") or ""

    fila["D2_intensidad"] = d2.get("intensidad_global", "").capitalize()

    # Dimensión 3: Racionamiento
    d3 = analisis.get("D3_racionamiento", {})
    fila["D3_racionamiento_presente"] = "Sí" if d3.get("presente") else "No"

    if d3.get("indicadores"):
        ind = d3["indicadores"]
        fila["D3_barreras_informales"] = "Sí" if ind.get("barreras_informales", {}).get("presente") else "No"
        fila["D3_barreras_informales_cita"] = ind.get("barreras_informales", {}).get("cita") or ""

        fila["D3_derivaciones_reiteradas"] = "Sí" if ind.get("derivaciones_reiteradas", {}).get("presente") else "No"
        fila["D3_derivaciones_reiteradas_cita"] = ind.get("derivaciones_reiteradas", {}).get("cita") or ""

        fila["D3_seleccion_implicita"] = "Sí" if ind.get("seleccion_implicita", {}).get("presente") else "No"
        fila["D3_seleccion_implicita_cita"] = ind.get("seleccion_implicita", {}).get("cita") or ""

        fila["D3_postergacion_complejos"] = "Sí" if ind.get("postergacion_complejos", {}).get("presente") else "No"
        fila["D3_postergacion_complejos_cita"] = ind.get("postergacion_complejos", {}).get("cita") or ""

    fila["D3_intensidad"] = d3.get("intensidad_global", "").capitalize()

    # Dimensión 4: Relación
    d4 = analisis.get("D4_relacion", {})
    fila["D4_relacion_presente"] = "Sí" if d4.get("presente") else "No"

    if d4.get("indicadores"):
        ind = d4["indicadores"]

        trato = ind.get("trato_vertical_horizontal", {})
        fila["D4_trato"] = trato.get("tipo", "Mixto").capitalize()
        fila["D4_trato_cita"] = trato.get("cita") or ""

        escucha = ind.get("nivel_escucha", {})
        fila["D4_nivel_escucha"] = escucha.get("nivel", "Medio").capitalize()
        fila["D4_nivel_escucha_cita"] = escucha.get("cita") or ""

        fila["D4_reconocimiento_autonomia"] = "Sí" if ind.get("reconocimiento_autonomia", {}).get("presente") else "No"
        fila["D4_reconocimiento_autonomia_cita"] = ind.get("reconocimiento_autonomia", {}).get("cita") or ""

        construccion = ind.get("construccion_adulto_mayor", {})
        fila["D4_construccion_adulto_mayor"] = construccion.get("categoria", "Mixto").replace("_", " ").capitalize()
        fila["D4_construccion_adulto_mayor_cita"] = construccion.get("cita") or ""

    fila["D4_intensidad"] = d4.get("intensidad_global", "").capitalize()

    # Notas
    fila["notas_generales"] = analisis.get("notas_generales", "")

    return fila


def generar_tabla_excel(
    resultados_analisis: List[Dict],
    nombre_archivo: str = None
) -> Path:
    """
    Genera una tabla Excel con los resultados del análisis.

    Args:
        resultados_analisis: Lista de diccionarios con análisis
        nombre_archivo: Nombre del archivo Excel (default: genera automáticamente)

    Returns:
        Ruta al archivo Excel generado
    """

    if not resultados_analisis:
        print("⚠ No hay resultados para exportar.")
        return None

    # Aplanar todos los análisis
    filas = [aplanar_analisis(analisis) for analisis in resultados_analisis]

    # Crear DataFrame
    df = pd.DataFrame(filas)

    # Generar nombre de archivo si no se proporciona
    if nombre_archivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"Analisis_Entrevistas_{timestamp}.xlsx"

    ruta_archivo = RESULTADOS_DIR / nombre_archivo

    # Escribir a Excel
    try:
        with pd.ExcelWriter(ruta_archivo, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Análisis", index=False)

            # Ajustar ancho de columnas
            worksheet = writer.sheets["Análisis"]
            for column in worksheet.columns:
                max_length = max(
                    len(str(cell.value)) for cell in column if cell.value
                )
                adjusted_width = min(max_length + 2, 50)  # Máximo 50
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

        if VERBOSE:
            print(f"✓ Archivo Excel generado: {ruta_archivo.name}")

        logger.info(f"Excel generado: {ruta_archivo}")
        return ruta_archivo

    except Exception as e:
        print(f"✗ Error al generar Excel: {e}")
        logger.error(f"Error al generar Excel: {e}")
        return None


def generar_tabla_csv(
    resultados_analisis: List[Dict],
    nombre_archivo: str = None
) -> Path:
    """
    Genera un CSV con los resultados del análisis.

    Args:
        resultados_analisis: Lista de diccionarios con análisis
        nombre_archivo: Nombre del archivo CSV (default: genera automáticamente)

    Returns:
        Ruta al archivo CSV generado
    """

    if not resultados_analisis:
        print("⚠ No hay resultados para exportar.")
        return None

    # Aplanar todos los análisis
    filas = [aplanar_analisis(analisis) for analisis in resultados_analisis]

    # Crear DataFrame
    df = pd.DataFrame(filas)

    # Generar nombre de archivo si no se proporciona
    if nombre_archivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"Analisis_Entrevistas_{timestamp}.csv"

    ruta_archivo = RESULTADOS_DIR / nombre_archivo

    # Escribir a CSV
    try:
        df.to_csv(ruta_archivo, index=False, encoding="utf-8")

        if VERBOSE:
            print(f"✓ Archivo CSV generado: {ruta_archivo.name}")

        logger.info(f"CSV generado: {ruta_archivo}")
        return ruta_archivo

    except Exception as e:
        print(f"✗ Error al generar CSV: {e}")
        logger.error(f"Error al generar CSV: {e}")
        return None


def guardar_json_resultados(
    resultados_analisis: List[Dict],
    nombre_archivo: str = None
) -> Path:
    """
    Guarda los resultados en formato JSON para posterior procesamiento.

    Args:
        resultados_analisis: Lista de diccionarios con análisis
        nombre_archivo: Nombre del archivo JSON

    Returns:
        Ruta al archivo JSON generado
    """

    if not resultados_analisis:
        print("⚠ No hay resultados para guardar.")
        return None

    if nombre_archivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"Analisis_Entrevistas_{timestamp}.json"

    ruta_archivo = RESULTADOS_DIR / nombre_archivo

    try:
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(resultados_analisis, f, indent=2, ensure_ascii=False)

        if VERBOSE:
            print(f"✓ Archivo JSON generado: {ruta_archivo.name}")

        logger.info(f"JSON generado: {ruta_archivo}")
        return ruta_archivo

    except Exception as e:
        print(f"✗ Error al generar JSON: {e}")
        logger.error(f"Error al generar JSON: {e}")
        return None
