# Análisis Cualitativo de Entrevistas - Burocracia de la Calle

Herramienta de análisis cualitativo para investigación en ciencia política. Convierte entrevistas en audio a texto y extrae variables de investigación sobre los mecanismos de acción de los burócratas de la calle en la implementación de políticas sociales dirigidas al adulto mayor.

## 📋 Funcionalidades

✅ **Transcripción automática** de audios con Whisper (OpenAI API)
✅ **Análisis cualitativo** con GPT-4o usando esquema de codificación específico
✅ **4 dimensiones analíticas** con indicadores e intensidades
✅ **Exportación a Excel, CSV y JSON** con estructura tabular
✅ **Reintentos automáticos** con backoff exponencial
✅ **Interfaz CLI** flexible y fácil de usar

## 🛠️ Instalación

### Requisitos previos
- Python 3.10+
- Cuenta en OpenAI con API key
- 2 GB de espacio en disco

### 1. Clonar o descargar el repositorio

```bash
cd ~/Desktop
# O navega a tu directorio GitHub
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar API key de OpenAI

#### Opción A: Variable de entorno (RECOMENDADO - MÁS SEGURO)

```bash
# En Windows (PowerShell):
$env:OPENAI_API_KEY="sk-xxxxxxxxxxxx"

# En Windows (CMD):
set OPENAI_API_KEY=sk-xxxxxxxxxxxx

# En macOS/Linux:
export OPENAI_API_KEY="sk-xxxxxxxxxxxx"
```

#### Opción B: Archivo `.env` (alternativo)

Crea un archivo `.env` en la raíz del proyecto:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

Luego, en `config.py`, descomenta la línea:
```python
from dotenv import load_dotenv
load_dotenv()
```

## 📖 Uso

### Flujo completo: Transcribir + Analizar + Exportar

```bash
python main.py
```

Procesará todos los archivos de audio en la carpeta `audio/`:
1. Transcribe cada audio
2. Analiza cada transcripción con GPT-4o
3. Genera tablas Excel, CSV y JSON

### Procesar un archivo específico

```bash
python main.py --audio entrevista_01.mp3
```

### Solo transcribir (sin análisis)

Útil para procesar audios largos sin costos de análisis:

```bash
python main.py --solo-transcribir
```

Las transcripciones se guardan en `transcripciones/` para analizar después.

### Re-analizar transcripciones existentes

Sin re-transcribir (más económico):

```bash
python main.py --reanalizar
```

Útil si quieres cambiar criterios de análisis sin volver a pagar transcripciones.

### Forzar re-procesamiento

```bash
python main.py --forzar              # Re-transcribe y re-analiza todo
python main.py --forzar --audio file.mp3  # Re-procesa un archivo
```

### Ver ayuda

```bash
python main.py --help
```

## 📁 Estructura del proyecto

```
Analisis_Proteccion_Social/
├── audio/                  # 📁 Coloca aquí tus archivos de audio
│   ├── entrevista_01.mp3
│   ├── entrevista_02.m4a
│   └── ...
│
├── transcripciones/        # 📁 Transcripciones generadas automáticamente
│   ├── entrevista_01.txt
│   ├── entrevista_02.txt
│   └── ...
│
├── resultados/             # 📁 Análisis y tablas generadas
│   ├── Analisis_Entrevistas_20260226_124530.xlsx
│   ├── Analisis_Entrevistas_20260226_124530.csv
│   ├── Analisis_Entrevistas_20260226_124530.json
│   └── ...
│
├── main.py                 # Script principal
├── config.py               # Configuración centralizada
├── transcribir.py          # Módulo de transcripción (Whisper)
├── analizar.py             # Módulo de análisis (GPT-4o)
├── exportar.py             # Módulo de exportación
├── requirements.txt        # Dependencias Python
├── README.md               # Este archivo
└── .gitignore              # Archivos a ignorar en git
```

## 🎯 Esquema de análisis

El sistema identifica 4 dimensiones analíticas:

### Dimensión 1: Uso de la discrecionalidad
Conjunto de prácticas mediante las cuales los burócratas interpretan y aplican normas de forma flexible.

**Indicadores:**
- Interpretación flexible de normas
- Decisiones caso por caso
- Adaptación de requisitos formales
- Priorización informal de beneficiarios

### Dimensión 2: Estrategias de rutinización
Mecanismos de estandarización que simplifican la atención.

**Indicadores:**
- Simplificación de trámites
- Estandarización de la atención
- Uso de categorías informales para clasificar adultos mayores
- Reducción del tiempo de atención

### Dimensión 3: Racionamiento del acceso
Prácticas que limitan o controlan el acceso a la política.

**Indicadores:**
- Barreras informales de acceso
- Derivaciones reiteradas
- Selección implícita de beneficiarios
- Postergación de casos complejos

### Dimensión 4: Relación burócrata–adulto mayor
Dinámicas de la interacción entre funcionario y beneficiario.

**Indicadores:**
- Trato vertical vs. trato horizontal
- Nivel de escucha activa
- Reconocimiento de autonomía del adulto mayor
- Construcción del adulto mayor como "cliente", "beneficiario" o "sujeto vulnerable"

## 📊 Tabla de resultados

Cada fila corresponde a una entrevista con columnas para:

| Tipo | Ejemplo |
|------|---------|
| Metadatos | id_entrevista, archivo_original, fecha_procesamiento |
| Dimensión 1 | D1_discrecionalidad_presente, D1_interpretacion_flexible, ... D1_intensidad |
| Dimensión 2 | D2_rutinizacion_presente, D2_simplificacion_tramites, ... D2_intensidad |
| Dimensión 3 | D3_racionamiento_presente, D3_barreras_informales, ... D3_intensidad |
| Dimensión 4 | D4_relacion_presente, D4_trato, ... D4_intensidad |
| Análisis | notas_generales |

Cada indicador incluye:
- **Presente**: Sí/No
- **Cita**: Fragmento textual de la entrevista como evidencia
- **Intensidad**: Baja, Media, Alta

## 💰 Costos estimados (OpenAI API)

- **Whisper**: ~$0.006 por minuto de audio
  - Entrevista de 1 hora: ~$0.36

- **GPT-4o**: ~$0.01-0.03 por entrevista de 1 hora
  - Depende de la longitud de la transcripción

**Total estimado por entrevista:** $0.40-0.40

**Recomendación:** Una vez transcrita, puedes re-analizar sin costo de transcripción.

## 🔧 Configuración avanzada

Edita `config.py` para personalizar:

```python
# Modelo a usar
GPT_MODEL = "gpt-4o"  # o "gpt-4-turbo", "gpt-3.5-turbo"

# Temperatura (0-1): Más alto = más creativo, más bajo = más consistente
TEMPERATURA_GPT = 0.1  # Para análisis, mantener bajo

# Reintentos si la API falla
MAX_REINTENTOS = 3
```

## 🚀 Próximas mejoras

- [ ] Interfaz gráfica (Streamlit)
- [ ] Base de datos para historial de análisis
- [ ] Validación automática de calidad
- [ ] Análisis comparativo entre entrevistas
- [ ] Exportación a ATLAS.ti o NVivo

## 📝 Ejemplo de uso completo

```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Configurar API key
export OPENAI_API_KEY="sk-xxxxxxxxxxxx"

# 3. Colocar audios en audio/
# (copiar archivos manualmente a la carpeta audio/)

# 4. Ejecutar análisis completo
python main.py

# 5. Revisar resultados en resultados/
# - Analisis_Entrevistas_*.xlsx
# - Analisis_Entrevistas_*.csv
# - Analisis_Entrevistas_*.json
```

## 🐛 Solución de problemas

### Error: "OPENAI_API_KEY no está configurada"

```bash
# Verifica que la variable de entorno esté establecida
echo $OPENAI_API_KEY

# Si está vacía, configúrala:
export OPENAI_API_KEY="sk-xxxxxxxxxxxx"
```

### Error: "Módulo no encontrado"

```bash
# Verifica que estés en el entorno virtual correcto
pip install -r requirements.txt
```

### Audios no se encuentran

Coloca los archivos en la carpeta `audio/` (no en subcarpetas).

Formatos soportados: `.mp3`, `.wav`, `.m4a`, `.webm`, `.mp4`, `.mpeg`, `.mpga`

### Timeout con audios largos

OpenAI API tiene límite de 25 MB por archivo. Para audios más largos, divídelos en partes menores a 25 MB.

## 📧 Contacto y soporte

Para problemas o sugerencias, consulta:
- Documentación de OpenAI: https://platform.openai.com/docs
- GitHub Issues: (tu repositorio)

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles

---

**Última actualización:** Febrero 2026
**Versión:** 1.0.0
