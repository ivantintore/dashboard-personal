# 🖼️ Conversor HEIC + PDF a JPG

**Conversor profesional de imágenes HEIC y extractor de imágenes de PDFs con compresión configurable**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Características

- 🖼️ **Conversión HEIC/HEIF a JPG** con calidad configurable
- 📄 **Extracción de imágenes de PDFs** con nomenclatura inteligente
- 🎛️ **Compresión configurable** con barras deslizantes intuitivas
- 📁 **Procesamiento en lote** de múltiples archivos
- 🚀 **Interfaz web moderna** con drag & drop
- 📱 **Diseño responsive** para móvil y desktop
- 🔒 **Validación de archivos** y seguridad integrada
- 📦 **Descarga en ZIP** de todas las imágenes convertidas

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/ivantintore/conversor-heif-jpg.git
   cd conversor-heif-jpg
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python -m app.main
   ```

5. **Abrir en el navegador**
   ```
   http://localhost:8000
   ```

### Instalación con Docker

1. **Construir la imagen**
   ```bash
   docker build -t conversor-heic-jpg .
   ```

2. **Ejecutar el contenedor**
   ```bash
   docker run -p 8000:8000 conversor-heic-jpg
   ```

3. **Con Docker Compose**
   ```bash
   docker-compose up --build
   ```

## 🎯 Uso

### Interfaz Web

1. **Abrir la aplicación** en tu navegador
2. **Arrastrar y soltar archivos** HEIC, HEIF o PDF en el área de upload
3. **Configurar calidad y compresión** usando las barras deslizantes
4. **Hacer clic en "Convertir Archivos"**
5. **Descargar el ZIP** con todas las imágenes convertidas

### API REST

#### Convertir Archivos

```bash
POST /api/convert
Content-Type: multipart/form-data

files: [archivo1.heic, archivo2.pdf]
quality: 85
compression: 85
```

**Respuesta:**
```json
{
  "success": true,
  "task_id": "uuid-12345",
  "total_files": 2,
  "heic_files": 1,
  "pdf_files": 1,
  "processed_files": 2,
  "download_url": "/api/download/uuid-12345"
}
```

#### Descargar Resultados

```bash
GET /api/download/{task_id}
```

### Línea de Comandos

```bash
# Convertir archivo HEIC individual
python -c "
from app.core.converters.heic_converter import HEICConverter
import asyncio

async def convert():
    converter = HEICConverter()
    result = await converter.convert_file(
        'imagen.heic', 
        'imagen.jpg', 
        quality=90
    )
    print(result)

asyncio.run(convert())
"
```

## 🏗️ Arquitectura

```
conversor-heif-jpg/
├── 📁 app/
│   ├── 📁 core/           # Lógica de negocio
│   │   ├── converters/    # Conversores HEIC/PDF
│   │   ├── validators/    # Validación de archivos
│   │   └── processors/    # Procesamiento en lote
│   ├── 📁 api/            # Endpoints REST
│   ├── 📁 web/            # Interfaz de usuario
│   └── 📁 utils/          # Utilidades comunes
├── 📁 tests/              # Tests unitarios
├── 📁 docs/               # Documentación
├── 📁 config/             # Configuraciones
├── requirements.txt        # Dependencias
├── Dockerfile             # Containerización
└── docker-compose.yml     # Desarrollo local
```

### Componentes Principales

- **HEICConverter**: Conversión de imágenes HEIC/HEIF a JPG
- **PDFConverter**: Extracción de imágenes de PDFs
- **BatchProcessor**: Procesamiento en lote de archivos
- **FileValidator**: Validación y seguridad de archivos
- **FastAPI**: API REST moderna y rápida

## ⚙️ Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Configuración de la aplicación
ENVIRONMENT=development
DEBUG=true
MAX_FILE_SIZE=100MB
UPLOAD_DIR=uploads

# Configuración de conversión
DEFAULT_QUALITY=85
MAX_QUALITY=100
MIN_QUALITY=1

# Configuración de PDF
MAX_PDF_PAGES=100
MAX_IMAGES_PER_PAGE=10

# Configuración de seguridad
ENABLE_RATE_LIMITING=true
MAX_REQUESTS_PER_MINUTE=60
```

### Configuración de Calidad

- **Calidad de Imagen**: Controla la calidad del JPG de salida (1-100)
- **Compresión**: Controla el nivel de compresión (1-100)
- **Optimización**: Habilita optimización automática de archivos

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=app

# Tests específicos
pytest tests/test_heic_converter.py

# Tests en paralelo
pytest -n auto
```

### Cobertura de Tests

```bash
# Generar reporte de cobertura
pytest --cov=app --cov-report=html

# Abrir reporte en navegador
open htmlcov/index.html
```

## 🚀 Deploy en Railway

### 1. Preparar el Proyecto

```bash
# Asegurar que todos los archivos estén committeados
git add .
git commit -m "Preparar para deploy en Railway"
git push origin main
```

### 2. Conectar con Railway

1. **Crear cuenta** en [Railway.app](https://railway.app)
2. **Conectar repositorio** de GitHub
3. **Seleccionar rama** (main)
4. **Configurar variables** de entorno

### 3. Variables de Entorno en Railway

```env
ENVIRONMENT=production
DEBUG=false
MAX_FILE_SIZE=100MB
UPLOAD_DIR=uploads
DEFAULT_QUALITY=85
MAX_PDF_PAGES=100
```

### 4. Deploy Automático

Railway detectará automáticamente el `Dockerfile` y desplegará la aplicación.

## 🔧 Desarrollo

### Estructura del Código

- **Clean Architecture**: Separación clara de responsabilidades
- **Type Hints**: Anotaciones de tipo para mejor documentación
- **Async/Await**: Procesamiento asíncrono para mejor rendimiento
- **Error Handling**: Manejo robusto de errores con mensajes claros

### Estándares de Código

```bash
# Formatear código
black app/ tests/

# Ordenar imports
isort app/ tests/

# Linting
flake8 app/ tests/
```

### Agregar Nuevas Funcionalidades

1. **Crear módulo** en `app/core/`
2. **Implementar tests** en `tests/`
3. **Actualizar API** en `app/main.py`
4. **Documentar cambios** en README

## 📊 Rendimiento

### Optimizaciones Implementadas

- **Procesamiento asíncrono** de archivos
- **Compresión inteligente** de imágenes
- **Limpieza automática** de archivos temporales
- **Validación temprana** de archivos

### Límites de Rendimiento

- **Archivos máximos**: 100MB por archivo
- **PDFs máximos**: 100 páginas
- **Imágenes por página**: 10 imágenes
- **Tiempo de procesamiento**: ~2-5 segundos por imagen

## 🔒 Seguridad

### Medidas Implementadas

- **Validación de tipos** de archivo
- **Sanitización** de nombres de archivo
- **Límites de tamaño** configurables
- **Rate limiting** para prevenir abuso
- **Limpieza automática** de archivos temporales

### Validaciones de Archivo

- ✅ **HEIC/HEIF**: Verificación de formato real
- ✅ **PDF**: Validación de estructura PDF
- ✅ **Tamaño**: Límites configurables
- ✅ **Nombres**: Prevención de path traversal

## 🤝 Contribuir

### Cómo Contribuir

1. **Fork** el repositorio
2. **Crear rama** para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crear Pull Request**

### Guías de Contribución

- **Código limpio** y bien documentado
- **Tests** para nuevas funcionalidades
- **Type hints** en todas las funciones
- **Mensajes de commit** descriptivos

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **Pillow**: Procesamiento de imágenes
- **PyMuPDF**: Extracción de PDFs
- **FastAPI**: Framework web moderno
- **Railway**: Plataforma de hosting

## 📞 Soporte

### Problemas Comunes

**Error: "No module named 'pillow_heif'"**
```bash
pip install pillow-heif
```

**Error: "PDF too large"**
- Reducir el número de páginas en configuración
- Dividir PDFs grandes en archivos más pequeños

**Error: "File validation failed"**
- Verificar que el archivo sea HEIC, HEIF o PDF válido
- Comprobar que el archivo no esté corrupto

### Contacto

- **Issues**: [GitHub Issues](https://github.com/ivantintore/conversor-heif-jpg/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ivantintore/conversor-heif-jpg/discussions)

---

**Desarrollado con ❤️ para familias que necesitan convertir sus fotos fácilmente**

