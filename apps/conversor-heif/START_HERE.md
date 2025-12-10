# 🚀 Cómo Iniciar el Conversor HEIC + PDF a JPG

## ⚡ **INICIO RÁPIDO (Recomendado)**

### Opción 1: Script Automatizado (macOS/Linux)
```bash
# En Terminal:
cd "/Users/ivantintore/Conversor de PDF a JPG"
./start.sh
```

### Opción 2: Doble-Click (Solo macOS)
- Hacer doble-click en: `start_mac.command`
- Se abrirá Terminal automáticamente

### Opción 3: Manual (Si necesitas más control)
```bash
cd "/Users/ivantintore/Conversor de PDF a JPG"
source .venv/bin/activate
python -m app.main
```

---

## ✅ **¿CÓMO SÉ QUE FUNCIONA?**

Después del inicio verás:

```
🚀 Starting Conversor HEIC + PDF a JPG...
🧹 Cleaning up previous server instances...
✅ Port 8000 is available
📱 Server will start on: http://localhost:8000
🌍 Also accessible on: http://0.0.0.0:8000
🔧 Debug mode: False
==================================================
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Luego abre:** http://localhost:8000

---

## 🔧 **SOLUCIÓN DE PROBLEMAS**

### ❌ "Address already in use"
**YA NO DEBERÍA PASAR** - El script nuevo lo maneja automáticamente, pero si ocurre:
```bash
lsof -i :8000
kill -9 [PID]
./start.sh
```

### ❌ "Python not found"
```bash
# Instalar Python 3.8+
brew install python3
# O descargar de: https://python.org
```

### ❌ "Permission denied"
```bash
chmod +x start.sh
chmod +x start_mac.command
```

### ❌ "Module not found"
```bash
# El script instala automáticamente, pero si falla:
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 **FUNCIONALIDADES PROBADAS**

✅ **Conversión HEIC → JPG** con calidad configurable  
✅ **Extracción PDF → JPG** con nomenclatura inteligente  
✅ **Procesamiento en lote** de múltiples archivos  
✅ **Descarga en ZIP** automática  
✅ **Interfaz web responsive**  
✅ **Manejo robusto de errores**  
✅ **Detección automática de puertos**  
✅ **Limpieza automática de procesos**  

---

## 📞 **¿NECESITAS AYUDA?**

1. **Verificar que funciona:**
   ```bash
   curl http://localhost:8000/health
   # Debería mostrar: {"status":"healthy","version":"1.0.0"}
   ```

2. **Ver logs detallados:**
   - Los logs aparecen en Terminal durante la ejecución

3. **Reiniciar completamente:**
   ```bash
   pkill -f uvicorn
   ./start.sh
   ```

**¡Tu aplicación está lista para usar de forma CONFIABLE!** 🎉
