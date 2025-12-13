"""
Deuda-Rentabilidad: API y Dashboard
====================================

Aplicación web para analizar estrategias de apalancamiento
con préstamos lombardos.
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json

from .calculators import (
    CalculadoraLombardo,
    CalculadoraHipoteca,
    AnalizadorActivo,
    AnalizadorInversion
)
from .calculators.activo import (
    comparar_bancos_españoles, 
    ranking_por_rentabilidad_dividendo,
    comparar_ibex35,
    comparar_por_sector,
    obtener_sectores,
    IBEX35_DATOS,
    stress_test_lombardo,
    calcular_ltv_maximo_por_drawdown,
    calcular_drawdown_tolerable
)
from .calculators.inversion import calcular_rentabilidad_total_estrategia, analisis_escenarios
from .calculators.hipoteca import comparar_hipoteca_vs_lombardo

# Crear app (sin root_path - Caddy maneja el subpath con strip_prefix)
app = FastAPI(
    title="Deuda-Rentabilidad",
    description="Análisis de estrategias de apalancamiento con préstamos lombardos",
    version="1.0.0"
)

# Configurar templates y static files
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Montar archivos estáticos
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================================================================
# PÁGINAS WEB
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal interactivo"""
    return templates.TemplateResponse("index.html", {"request": request})


# ============================================================================
# API: ESTUDIO 1 - CRÉDITO LOMBARDO
# ============================================================================

@app.get("/api/lombardo/calcular")
async def calcular_lombardo(
    valor_garantia: float = 100_000,
    ltv: float = 0.70,
    euribor: float = 0.025,
    spread: float = 0.015
):
    """
    Calcula los costes de un préstamo lombardo.
    
    - valor_garantia: Valor de los activos en garantía (€)
    - ltv: Loan-to-Value (0.50-0.80)
    - euribor: Euribor 12M actual
    - spread: Diferencial sobre Euribor
    """
    calc = CalculadoraLombardo(
        valor_garantia=valor_garantia,
        ltv=ltv,
        euribor=euribor,
        spread=spread
    )
    
    return calc.resumen()


@app.get("/api/lombardo/tabla-amortizacion")
async def tabla_amortizacion_lombardo(
    valor_garantia: float = 100_000,
    ltv: float = 0.70,
    euribor: float = 0.025,
    spread: float = 0.015,
    años: int = 5
):
    """Tabla de costes anuales del préstamo lombardo"""
    calc = CalculadoraLombardo(
        valor_garantia=valor_garantia,
        ltv=ltv,
        euribor=euribor,
        spread=spread
    )
    
    return {
        "resumen": calc.resumen(),
        "tabla": calc.tabla_amortizacion(años)
    }


@app.get("/api/lombardo/margin-call")
async def analizar_margin_call(
    valor_garantia: float = 100_000,
    ltv: float = 0.70,
    ltv_margin_call: float = 0.85,
    ltv_liquidacion: float = 0.95
):
    """Analiza el riesgo de margin call"""
    calc = CalculadoraLombardo(valor_garantia=valor_garantia, ltv=ltv)
    margin = calc.analizar_margin_call(ltv_margin_call, ltv_liquidacion)
    
    return {
        "valor_garantia_inicial": margin.valor_garantia_inicial,
        "ltv_inicial": f"{margin.ltv_inicial*100:.0f}%",
        "ltv_margin_call": f"{margin.ltv_margin_call*100:.0f}%",
        "ltv_liquidacion": f"{margin.ltv_liquidacion*100:.0f}%",
        "caida_hasta_margin_call": f"{margin.caida_hasta_margin_call*100:.1f}%",
        "caida_hasta_liquidacion": f"{margin.caida_hasta_liquidacion*100:.1f}%",
        "valor_margin_call": margin.valor_margin_call,
        "valor_liquidacion": margin.valor_liquidacion,
        "interpretacion": (
            f"Si las acciones caen un {margin.caida_hasta_margin_call*100:.1f}%, "
            f"recibirás un margin call. Si caen un {margin.caida_hasta_liquidacion*100:.1f}%, "
            f"el banco venderá tus acciones."
        )
    }


# ============================================================================
# API: COMPARATIVA HIPOTECA vs LOMBARDO
# ============================================================================

@app.get("/api/comparar/hipoteca-lombardo")
async def comparar_hipoteca_lombardo(
    capital: float = 70_000,
    hipoteca_plazo: int = 25,
    hipoteca_spread: float = 0.01,
    lombardo_ltv: float = 0.70,
    lombardo_spread: float = 0.015,
    euribor: float = 0.025
):
    """Compara los costes de hipoteca vs lombardo"""
    return comparar_hipoteca_vs_lombardo(
        capital=capital,
        hipoteca_params={
            "plazo_años": hipoteca_plazo,
            "spread": hipoteca_spread,
            "euribor": euribor
        },
        lombardo_params={
            "ltv": lombardo_ltv,
            "spread": lombardo_spread,
            "euribor": euribor
        }
    )


# ============================================================================
# API: ESTUDIO 2 - ANÁLISIS DE ACTIVOS
# ============================================================================

@app.get("/api/activos/ibex35")
async def listar_ibex35(inversion: float = 100_000, sector: str = None):
    """
    Lista todos los valores del IBEX 35 con análisis de dividendos (5 años).
    Opcionalmente filtra por sector.
    """
    if sector:
        return comparar_por_sector(sector, inversion)
    return comparar_ibex35(inversion)


@app.get("/api/activos/sectores")
async def listar_sectores():
    """Lista los sectores disponibles del IBEX 35"""
    return {
        "sectores": obtener_sectores(),
        "total_valores": len(IBEX35_DATOS)
    }


@app.get("/api/activos/sector/{sector}")
async def activos_por_sector(sector: str, inversion: float = 100_000):
    """Lista valores de un sector específico del IBEX 35"""
    return comparar_por_sector(sector, inversion)


@app.get("/api/activos/bancos-españoles")
async def listar_bancos(inversion: float = 100_000):
    """Compara los principales bancos españoles como inversión"""
    return comparar_bancos_españoles(inversion)


@app.get("/api/activos/ranking-dividendos")
async def ranking_dividendos(top: int = None):
    """Ranking de valores IBEX 35 por rentabilidad por dividendo (últimos 5 años)"""
    return ranking_por_rentabilidad_dividendo(top_n=top)


@app.get("/api/activos/analizar/{ticker}")
async def analizar_activo(ticker: str, inversion: float = 100_000):
    """
    Analiza un activo específico.
    
    Tickers disponibles: SAN.MC, BBVA.MC, CABK.MC, BKT.MC, SAB.MC
    """
    analizador = AnalizadorActivo(ticker, usar_api=False)
    return analizador.resumen_completo(inversion)


# ============================================================================
# API: ESTUDIO 3 - ANÁLISIS DE INVERSIÓN
# ============================================================================

@app.get("/api/inversion/opciones")
async def opciones_inversion(
    capital_prestamo: float = 70_000,
    coste_prestamo: float = 0.04,
    perfil: str = "conservador"
):
    """
    Lista opciones de inversión para el préstamo.
    
    - capital_prestamo: Capital del préstamo lombardo
    - coste_prestamo: TAE del préstamo (ej: 0.04 = 4%)
    - perfil: conservador, moderado, agresivo
    """
    analizador = AnalizadorInversion(
        capital_prestamo=capital_prestamo,
        coste_prestamo=coste_prestamo,
        perfil_riesgo=perfil
    )
    
    return {
        "todas_las_opciones": analizador.analizar_todas_opciones(),
        "filtradas_por_perfil": analizador.filtrar_por_perfil(),
        "mejor_opcion": analizador.mejor_opcion(),
        "resumen": analizador.resumen_estrategia()
    }


@app.get("/api/inversion/escenarios")
async def escenarios_inversion(capital: float = 70_000):
    """
    Analiza escenarios con diferentes costes de préstamo.
    
    Útil para ver qué pasa si sube/baja el Euribor.
    """
    escenarios = [0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06]
    return analisis_escenarios(capital, escenarios)


# ============================================================================
# API: ESTRATEGIA COMPLETA
# ============================================================================

@app.get("/api/estrategia/completa")
async def estrategia_completa(
    capital_inicial: float = 100_000,
    ticker_activo: str = "BBVA.MC",
    ltv: float = 0.70,
    euribor: float = 0.025,
    spread_lombardo: float = 0.015,
    rentabilidad_inversion: float = 0.035
):
    """
    Calcula la rentabilidad total de la estrategia completa:
    
    1. Comprar acciones con capital_inicial
    2. Pedir préstamo lombardo sobre las acciones
    3. Invertir el préstamo en activo con rentabilidad_inversion
    """
    # Obtener yield del activo
    analizador = AnalizadorActivo(ticker_activo)
    dividendos = analizador.analizar_dividendos(capital_inicial)
    yield_activo = dividendos["rentabilidad_dividendo"]
    
    # Coste total del préstamo
    coste_prestamo = euribor + spread_lombardo
    
    # Calcular rentabilidad total
    resultado = calcular_rentabilidad_total_estrategia(
        capital_inicial=capital_inicial,
        dividendo_activo=yield_activo,
        ltv=ltv,
        coste_prestamo=coste_prestamo,
        rentabilidad_inversion=rentabilidad_inversion
    )
    
    # Añadir info del activo
    resultado["activo"] = {
        "ticker": ticker_activo,
        "nombre": dividendos["nombre"],
        "yield": dividendos["rentabilidad_dividendo_pct"]
    }
    
    return resultado


@app.get("/api/estrategia/simulador")
async def simulador_estrategia(
    capital_inicial: float = 100_000,
    yield_activo: float = 0.07,
    ltv: float = 0.70,
    coste_prestamo: float = 0.04,
    rentabilidad_inversion: float = 0.035,
    años: int = 5
):
    """
    Simula la estrategia a lo largo del tiempo.
    
    Muestra evolución del patrimonio asumiendo reinversión de dividendos.
    """
    resultados_anuales = []
    capital_acumulado = capital_inicial
    beneficio_acumulado = 0
    
    for año in range(1, años + 1):
        # Calcular resultado del año
        prestamo = capital_acumulado * ltv
        dividendos = capital_acumulado * yield_activo
        coste = prestamo * coste_prestamo
        rentabilidad_inv = prestamo * rentabilidad_inversion
        
        beneficio_año = dividendos + rentabilidad_inv - coste
        beneficio_acumulado += beneficio_año
        
        # Reinvertir beneficios (opcional)
        # capital_acumulado += beneficio_año
        
        resultados_anuales.append({
            "año": año,
            "capital": capital_acumulado,
            "prestamo": prestamo,
            "dividendos": dividendos,
            "rentabilidad_inversion": rentabilidad_inv,
            "coste_prestamo": coste,
            "beneficio_año": beneficio_año,
            "beneficio_acumulado": beneficio_acumulado,
            "roi_año": beneficio_año / capital_inicial,
            "roi_acumulado": beneficio_acumulado / capital_inicial
        })
    
    return {
        "parametros": {
            "capital_inicial": capital_inicial,
            "yield_activo": f"{yield_activo*100:.2f}%",
            "ltv": f"{ltv*100:.0f}%",
            "coste_prestamo": f"{coste_prestamo*100:.2f}%",
            "rentabilidad_inversion": f"{rentabilidad_inversion*100:.2f}%"
        },
        "proyeccion": resultados_anuales,
        "resumen": {
            "beneficio_total": beneficio_acumulado,
            "roi_total": f"{(beneficio_acumulado/capital_inicial)*100:.2f}%",
            "roi_anualizado": f"{(beneficio_acumulado/capital_inicial/años)*100:.2f}%"
        }
    }


# ============================================================================
# API: STRESS TEST - Análisis de resistencia a drawdowns
# ============================================================================

@app.get("/api/stress-test/analizar")
async def analizar_stress_test(
    valor_colateral: float = 100_000,
    ltv_actual: float = 0.70,
    drawdown_tolerado: float = 0.30
):
    """
    Realiza un stress test del préstamo lombardo.
    
    Simula diferentes escenarios de crisis (2008, 2020, etc.) y muestra
    si tu configuración sobreviviría cada uno.
    
    - valor_colateral: Valor de las acciones en garantía
    - ltv_actual: LTV actual del préstamo (0.50-0.80)
    - drawdown_tolerado: Caída máxima que quieres poder tolerar (-20% a -50%)
    """
    return stress_test_lombardo(
        valor_colateral=valor_colateral,
        ltv_actual=ltv_actual,
        drawdown_tolerado=drawdown_tolerado
    )


@app.get("/api/stress-test/ltv-seguro")
async def calcular_ltv_seguro(drawdown_tolerado: float = 0.30):
    """
    Calcula el LTV máximo seguro para tolerar un drawdown dado.
    
    Ejemplo: Si quieres tolerar una caída del 30%, el LTV máximo seguro es ~60%
    
    - drawdown_tolerado: Caída que quieres poder soportar (0.20, 0.30, 0.40, 0.50)
    """
    ltv_maximo = calcular_ltv_maximo_por_drawdown(drawdown_tolerado)
    
    return {
        "drawdown_tolerado": f"-{drawdown_tolerado*100:.0f}%",
        "ltv_maximo_seguro": ltv_maximo,
        "ltv_maximo_seguro_pct": f"{ltv_maximo*100:.0f}%",
        "prestamo_sobre_100k": ltv_maximo * 100_000,
        "explicacion": f"Para tolerar una caída del {drawdown_tolerado*100:.0f}%, "
                       f"tu LTV no debería superar el {ltv_maximo*100:.0f}%"
    }


@app.get("/api/stress-test/drawdown-tolerable")
async def calcular_drawdown_max(ltv_actual: float = 0.70):
    """
    Dado un LTV actual, calcula el drawdown máximo que puedes tolerar
    antes de recibir un margin call.
    
    - ltv_actual: LTV actual del préstamo
    """
    drawdown_max = calcular_drawdown_tolerable(ltv_actual)
    
    # Evaluar el riesgo
    if drawdown_max >= 0.30:
        nivel_riesgo = "Bajo"
        color = "verde"
    elif drawdown_max >= 0.20:
        nivel_riesgo = "Moderado"
        color = "amarillo"
    elif drawdown_max >= 0.10:
        nivel_riesgo = "Alto"
        color = "naranja"
    else:
        nivel_riesgo = "Muy Alto"
        color = "rojo"
    
    return {
        "ltv_actual": f"{ltv_actual*100:.0f}%",
        "drawdown_tolerable": drawdown_max,
        "drawdown_tolerable_pct": f"-{drawdown_max*100:.1f}%",
        "nivel_riesgo": nivel_riesgo,
        "color": color,
        "explicacion": f"Con un LTV del {ltv_actual*100:.0f}%, puedes tolerar "
                       f"una caída máxima del {drawdown_max*100:.1f}% antes del margin call"
    }


@app.get("/api/stress-test/tabla-referencia")
async def tabla_referencia_stress():
    """
    Devuelve la tabla de referencia: qué LTV usar según el drawdown que quieras tolerar.
    
    Basado en datos históricos del S&P 500 (1950-2024).
    """
    return {
        "titulo": "Guía de LTV según tolerancia al drawdown",
        "fuente": "Datos históricos S&P 500 (1950-2024)",
        "estadisticas_historicas": {
            "años_analizados": 75,
            "años_positivos": "80%",
            "media_drawdown_anual": "-13.8%",
            "peor_año": {"año": 1974, "drawdown": "-48%"},
            "segundo_peor": {"año": 2008, "drawdown": "-50%"}
        },
        "recomendaciones": [
            {
                "perfil": "Muy Conservador",
                "drawdown_tolerable": "-50%",
                "ltv_maximo": "43%",
                "prestamo_sobre_100k": 43000,
                "descripcion": "Sobrevives cualquier crisis histórica incluyendo 2008"
            },
            {
                "perfil": "Conservador",
                "drawdown_tolerable": "-40%",
                "ltv_maximo": "51%",
                "prestamo_sobre_100k": 51000,
                "descripcion": "Sobrevives crisis severas como 2022 y COVID"
            },
            {
                "perfil": "Moderado",
                "drawdown_tolerable": "-30%",
                "ltv_maximo": "60%",
                "prestamo_sobre_100k": 60000,
                "descripcion": "Sobrevives correcciones fuertes y crisis moderadas"
            },
            {
                "perfil": "Agresivo",
                "drawdown_tolerable": "-20%",
                "ltv_maximo": "68%",
                "prestamo_sobre_100k": 68000,
                "descripcion": "Solo sobrevives correcciones normales"
            }
        ],
        "advertencia": "⚠️ Un LTV superior al 70% es muy arriesgado. "
                       "Históricamente, casi el 50% de los años tienen drawdowns > 10%"
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "deuda-rentabilidad"}

