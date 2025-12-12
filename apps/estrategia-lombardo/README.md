# 📊 Deuda-Rentabilidad: Análisis de Estrategia Lombardo

Herramienta de análisis financiero para evaluar estrategias de apalancamiento usando préstamos lombardos.

## 🎯 Objetivo

Analizar la viabilidad de la siguiente estrategia:

1. **Comprar un activo** (ej: acciones de un banco) con capital propio
2. **Solicitar préstamo lombardo** usando las acciones como garantía
3. **Invertir el préstamo** en activos que rindan más que el coste del crédito

## 📚 Los 3 Estudios

### Estudio 1: Crédito Lombardo
- Costes totales del préstamo (TIN, TAE, comisiones)
- Ratio LTV (Loan-to-Value)
- Análisis de margin call
- Comparativa con hipoteca tradicional

### Estudio 2: El Activo Inicial
- Análisis de acciones bancarias (Santander, BBVA, CaixaBank, etc.)
- Historial de dividendos
- Rentabilidad por dividendo
- Volatilidad y riesgo

### Estudio 3: La Inversión
- Opciones de inversión para el préstamo
- Spread de rentabilidad (yield - coste)
- Análisis de escenarios
- Rentabilidad total de la estrategia

## 🚀 Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Mac/Linux

# Instalar dependencias
pip install -r requirements.txt
```

## 💻 Uso

```bash
# Iniciar el servidor
python -m uvicorn app.main:app --reload --port 8000

# Abrir en navegador
open http://localhost:8000
```

## 📁 Estructura

```
├── app/
│   ├── main.py              # FastAPI app
│   ├── calculators/
│   │   ├── lombardo.py      # Calculadora crédito lombardo
│   │   ├── activo.py        # Análisis de activos
│   │   └── inversion.py     # Análisis de inversión
│   ├── templates/
│   │   └── index.html       # Dashboard interactivo
│   └── static/
│       └── styles.css       # Estilos
├── tests/
│   └── test_calculators.py
├── requirements.txt
└── README.md
```

## 📈 Ejemplo de Uso

```
Capital inicial: 100.000€
Activo: Acciones BBVA
Dividendo esperado: 7%
Préstamo Lombardo: 70.000€ (LTV 70%)
Coste préstamo: 5% TAE
Inversión: Letras del Tesoro 3.5%

Resultado:
- Dividendos: 7.000€/año
- Coste préstamo: 3.500€/año
- Rentabilidad inversión: 2.450€/año
- Beneficio neto: 5.950€/año
- Rentabilidad sobre capital: 5.95%
```

## ⚠️ Riesgos

- **Margin Call**: Si las acciones caen, pueden pedir más garantías
- **Riesgo de tipos**: Si sube el Euribor, sube el coste del préstamo
- **Riesgo de dividendos**: Los dividendos no están garantizados
- **Riesgo de liquidez**: Dificultad para vender en momentos de stress

