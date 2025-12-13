"""
Estudio 2: Análisis del Activo (Acciones IBEX 35)
=================================================

Análisis de los activos que usarás como garantía del préstamo lombardo.
Incluye todos los valores del IBEX 35 con datos históricos de 5 años.

Consideraciones para el Lombardo:
- Mayor volatilidad = menor LTV concedido
- Historial de dividendos importa
- Liquidez del valor
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class InfoAccion:
    """Información básica de una acción"""
    ticker: str
    nombre: str
    precio_actual: float
    moneda: str
    sector: str
    mercado: str


@dataclass
class AnalisisDividendos:
    """Análisis de dividendos de una acción"""
    ticker: str
    dividendo_anual: float
    rentabilidad_dividendo: float
    dividendos_ultimos_5_años: list[float]
    media_dividendos_5_años: float
    crecimiento_dividendo: float
    consistencia: str


@dataclass
class AnalisisRiesgo:
    """Análisis de riesgo de la acción"""
    ticker: str
    volatilidad_anual: float
    beta: float
    max_drawdown_5_años: float
    ltv_recomendado: float


# =============================================================================
# DATOS IBEX 35 - Últimos 5 años (2019-2023)
# Dividendos en € por acción, precios de referencia diciembre 2024
# =============================================================================

IBEX35_DATOS = {
    # === SECTOR FINANCIERO ===
    "SAN.MC": {
        "nombre": "Banco Santander",
        "sector": "Banca",
        "precio_referencia": 4.85,
        "dividendos_5_años": [0.20, 0.10, 0.14, 0.17, 0.19],  # 2019-2023
        "volatilidad": 0.35,
        "beta": 1.30,
        "max_drawdown_5y": 0.55
    },
    "BBVA.MC": {
        "nombre": "BBVA",
        "sector": "Banca",
        "precio_referencia": 10.25,
        "dividendos_5_años": [0.26, 0.16, 0.31, 0.43, 0.66],
        "volatilidad": 0.32,
        "beta": 1.20,
        "max_drawdown_5y": 0.50
    },
    "CABK.MC": {
        "nombre": "CaixaBank",
        "sector": "Banca",
        "precio_referencia": 5.45,
        "dividendos_5_años": [0.17, 0.03, 0.15, 0.31, 0.39],
        "volatilidad": 0.30,
        "beta": 1.10,
        "max_drawdown_5y": 0.52
    },
    "SAB.MC": {
        "nombre": "Banco Sabadell",
        "sector": "Banca",
        "precio_referencia": 1.95,
        "dividendos_5_años": [0.04, 0.00, 0.02, 0.05, 0.08],
        "volatilidad": 0.40,
        "beta": 1.40,
        "max_drawdown_5y": 0.65
    },
    "BKT.MC": {
        "nombre": "Bankinter",
        "sector": "Banca",
        "precio_referencia": 8.20,
        "dividendos_5_años": [0.26, 0.13, 0.21, 0.33, 0.45],
        "volatilidad": 0.28,
        "beta": 0.95,
        "max_drawdown_5y": 0.45
    },
    "UNI.MC": {
        "nombre": "Unicaja Banco",
        "sector": "Banca",
        "precio_referencia": 1.35,
        "dividendos_5_años": [0.04, 0.00, 0.03, 0.06, 0.09],
        "volatilidad": 0.35,
        "beta": 1.15,
        "max_drawdown_5y": 0.55
    },
    "MAP.MC": {
        "nombre": "MAPFRE",
        "sector": "Seguros",
        "precio_referencia": 2.35,
        "dividendos_5_años": [0.14, 0.12, 0.13, 0.14, 0.16],
        "volatilidad": 0.25,
        "beta": 0.85,
        "max_drawdown_5y": 0.40
    },
    
    # === ENERGÍA Y UTILITIES ===
    "IBE.MC": {
        "nombre": "Iberdrola",
        "sector": "Utilities",
        "precio_referencia": 12.50,
        "dividendos_5_años": [0.35, 0.42, 0.44, 0.50, 0.54],
        "volatilidad": 0.22,
        "beta": 0.70,
        "max_drawdown_5y": 0.30
    },
    "ENG.MC": {
        "nombre": "Enagás",
        "sector": "Utilities",
        "precio_referencia": 13.80,
        "dividendos_5_años": [1.53, 1.59, 1.68, 1.72, 1.74],
        "volatilidad": 0.20,
        "beta": 0.55,
        "max_drawdown_5y": 0.28
    },
    "REE.MC": {
        "nombre": "Red Eléctrica",
        "sector": "Utilities",
        "precio_referencia": 16.20,
        "dividendos_5_años": [0.94, 0.99, 1.00, 1.05, 1.08],
        "volatilidad": 0.18,
        "beta": 0.45,
        "max_drawdown_5y": 0.25
    },
    "NTGY.MC": {
        "nombre": "Naturgy",
        "sector": "Utilities",
        "precio_referencia": 23.50,
        "dividendos_5_años": [1.30, 1.00, 1.10, 1.20, 1.40],
        "volatilidad": 0.24,
        "beta": 0.65,
        "max_drawdown_5y": 0.35
    },
    "ELE.MC": {
        "nombre": "Endesa",
        "sector": "Utilities",
        "precio_referencia": 18.90,
        "dividendos_5_años": [1.43, 1.48, 1.00, 1.00, 1.00],
        "volatilidad": 0.23,
        "beta": 0.60,
        "max_drawdown_5y": 0.38
    },
    "REP.MC": {
        "nombre": "Repsol",
        "sector": "Petróleo y Gas",
        "precio_referencia": 12.80,
        "dividendos_5_años": [0.90, 0.60, 0.60, 0.70, 0.80],
        "volatilidad": 0.30,
        "beta": 1.00,
        "max_drawdown_5y": 0.55
    },
    "SLR.MC": {
        "nombre": "Solaria",
        "sector": "Energías Renovables",
        "precio_referencia": 9.50,
        "dividendos_5_años": [0.00, 0.00, 0.00, 0.00, 0.00],
        "volatilidad": 0.55,
        "beta": 1.60,
        "max_drawdown_5y": 0.75
    },
    "ACX.MC": {
        "nombre": "Acciona",
        "sector": "Energías Renovables",
        "precio_referencia": 115.00,
        "dividendos_5_años": [3.50, 3.00, 3.50, 4.00, 4.50],
        "volatilidad": 0.35,
        "beta": 1.10,
        "max_drawdown_5y": 0.50
    },
    "ANE.MC": {
        "nombre": "Acciona Energía",
        "sector": "Energías Renovables",
        "precio_referencia": 19.50,
        "dividendos_5_años": [0.00, 0.00, 0.93, 1.00, 1.12],
        "volatilidad": 0.40,
        "beta": 1.20,
        "max_drawdown_5y": 0.60
    },
    
    # === TELECOMUNICACIONES ===
    "TEF.MC": {
        "nombre": "Telefónica",
        "sector": "Telecomunicaciones",
        "precio_referencia": 4.25,
        "dividendos_5_años": [0.40, 0.30, 0.30, 0.30, 0.30],
        "volatilidad": 0.28,
        "beta": 0.90,
        "max_drawdown_5y": 0.45
    },
    "CLNX.MC": {
        "nombre": "Cellnex Telecom",
        "sector": "Telecomunicaciones",
        "precio_referencia": 32.00,
        "dividendos_5_años": [0.02, 0.02, 0.04, 0.06, 0.08],
        "volatilidad": 0.35,
        "beta": 0.80,
        "max_drawdown_5y": 0.55
    },
    
    # === CONSTRUCCIÓN E INFRAESTRUCTURAS ===
    "FER.MC": {
        "nombre": "Ferrovial",
        "sector": "Infraestructuras",
        "precio_referencia": 38.50,
        "dividendos_5_años": [0.70, 0.48, 0.72, 0.80, 0.88],
        "volatilidad": 0.25,
        "beta": 0.85,
        "max_drawdown_5y": 0.35
    },
    "ACS.MC": {
        "nombre": "ACS",
        "sector": "Construcción",
        "precio_referencia": 44.00,
        "dividendos_5_años": [1.89, 1.00, 1.54, 1.78, 2.13],
        "volatilidad": 0.28,
        "beta": 0.95,
        "max_drawdown_5y": 0.40
    },
    "AENA.MC": {
        "nombre": "Aena",
        "sector": "Infraestructuras",
        "precio_referencia": 195.00,
        "dividendos_5_años": [7.58, 0.00, 0.00, 5.75, 9.75],
        "volatilidad": 0.30,
        "beta": 1.00,
        "max_drawdown_5y": 0.60
    },
    "SGRE.MC": {
        "nombre": "Siemens Gamesa",
        "sector": "Industriales",
        "precio_referencia": 18.05,
        "dividendos_5_años": [0.00, 0.00, 0.00, 0.00, 0.00],
        "volatilidad": 0.50,
        "beta": 1.30,
        "max_drawdown_5y": 0.70
    },
    
    # === INMOBILIARIO ===
    "MRL.MC": {
        "nombre": "Merlin Properties",
        "sector": "Inmobiliario",
        "precio_referencia": 10.80,
        "dividendos_5_años": [0.46, 0.25, 0.40, 0.50, 0.56],
        "volatilidad": 0.32,
        "beta": 0.95,
        "max_drawdown_5y": 0.55
    },
    "COL.MC": {
        "nombre": "Inmobiliaria Colonial",
        "sector": "Inmobiliario",
        "precio_referencia": 5.80,
        "dividendos_5_años": [0.24, 0.24, 0.23, 0.27, 0.27],
        "volatilidad": 0.30,
        "beta": 0.90,
        "max_drawdown_5y": 0.50
    },
    
    # === CONSUMO ===
    "ITX.MC": {
        "nombre": "Inditex",
        "sector": "Retail",
        "precio_referencia": 50.00,
        "dividendos_5_años": [0.88, 0.35, 0.93, 1.12, 1.30],
        "volatilidad": 0.28,
        "beta": 0.85,
        "max_drawdown_5y": 0.40
    },
    "GRF.MC": {
        "nombre": "Grifols",
        "sector": "Farmacéutico",
        "precio_referencia": 9.50,
        "dividendos_5_años": [0.40, 0.20, 0.28, 0.00, 0.00],
        "volatilidad": 0.45,
        "beta": 0.75,
        "max_drawdown_5y": 0.70
    },
    "PHM.MC": {
        "nombre": "Pharma Mar",
        "sector": "Farmacéutico",
        "precio_referencia": 38.00,
        "dividendos_5_años": [0.00, 0.60, 0.00, 0.00, 0.00],
        "volatilidad": 0.60,
        "beta": 0.65,
        "max_drawdown_5y": 0.75
    },
    "ROVI.MC": {
        "nombre": "Laboratorios Rovi",
        "sector": "Farmacéutico",
        "precio_referencia": 55.00,
        "dividendos_5_años": [0.19, 0.25, 0.45, 1.21, 1.00],
        "volatilidad": 0.40,
        "beta": 0.70,
        "max_drawdown_5y": 0.55
    },
    
    # === INDUSTRIA Y MATERIALES ===
    "ACE.MC": {
        "nombre": "Acerinox",
        "sector": "Materiales",
        "precio_referencia": 9.80,
        "dividendos_5_años": [0.50, 0.50, 0.50, 0.60, 0.60],
        "volatilidad": 0.35,
        "beta": 1.25,
        "max_drawdown_5y": 0.50
    },
    "MTS.MC": {
        "nombre": "ArcelorMittal",
        "sector": "Materiales",
        "precio_referencia": 22.50,
        "dividendos_5_años": [0.10, 0.30, 0.38, 0.44, 0.44],
        "volatilidad": 0.45,
        "beta": 1.50,
        "max_drawdown_5y": 0.60
    },
    "CIE.MC": {
        "nombre": "CIE Automotive",
        "sector": "Automoción",
        "precio_referencia": 24.50,
        "dividendos_5_años": [0.56, 0.00, 0.35, 0.60, 0.75],
        "volatilidad": 0.38,
        "beta": 1.35,
        "max_drawdown_5y": 0.55
    },
    "FCC.MC": {
        "nombre": "FCC",
        "sector": "Servicios",
        "precio_referencia": 15.50,
        "dividendos_5_años": [0.40, 0.40, 0.40, 0.40, 0.40],
        "volatilidad": 0.28,
        "beta": 0.80,
        "max_drawdown_5y": 0.40
    },
    "SCYR.MC": {
        "nombre": "Sacyr",
        "sector": "Construcción",
        "precio_referencia": 3.20,
        "dividendos_5_años": [0.06, 0.05, 0.08, 0.10, 0.12],
        "volatilidad": 0.40,
        "beta": 1.20,
        "max_drawdown_5y": 0.55
    },
    
    # === OTROS ===
    "IAG.MC": {
        "nombre": "IAG (Iberia/British Airways)",
        "sector": "Aerolíneas",
        "precio_referencia": 2.45,
        "dividendos_5_años": [0.17, 0.00, 0.00, 0.00, 0.03],
        "volatilidad": 0.50,
        "beta": 1.45,
        "max_drawdown_5y": 0.80
    },
    "MEL.MC": {
        "nombre": "Meliá Hotels",
        "sector": "Hoteles",
        "precio_referencia": 7.20,
        "dividendos_5_años": [0.20, 0.00, 0.00, 0.00, 0.15],
        "volatilidad": 0.45,
        "beta": 1.30,
        "max_drawdown_5y": 0.75
    },
    "LOG.MC": {
        "nombre": "Logista",
        "sector": "Distribución",
        "precio_referencia": 27.50,
        "dividendos_5_años": [1.03, 1.06, 1.18, 1.43, 1.68],
        "volatilidad": 0.22,
        "beta": 0.55,
        "max_drawdown_5y": 0.30
    },
    "VIS.MC": {
        "nombre": "Viscofan",
        "sector": "Alimentación",
        "precio_referencia": 60.00,
        "dividendos_5_años": [1.48, 1.65, 1.80, 2.00, 2.30],
        "volatilidad": 0.20,
        "beta": 0.50,
        "max_drawdown_5y": 0.28
    },
    "FLUI.MC": {
        "nombre": "Fluidra",
        "sector": "Industriales",
        "precio_referencia": 20.00,
        "dividendos_5_años": [0.35, 0.25, 0.55, 0.70, 0.50],
        "volatilidad": 0.45,
        "beta": 1.25,
        "max_drawdown_5y": 0.65
    },
}


class AnalizadorActivo:
    """
    Analizador de activos del IBEX 35 para usar como garantía.
    """
    
    def __init__(self, ticker: str, usar_api: bool = False):
        self.ticker = ticker.upper()
        self.usar_api = usar_api
        self._datos_referencia = IBEX35_DATOS.get(self.ticker, {})
        self._datos_yfinance = None
        
        if usar_api:
            self._cargar_datos_yfinance()
    
    def _cargar_datos_yfinance(self):
        """Carga datos reales desde yfinance"""
        try:
            import yfinance as yf
            self._datos_yfinance = yf.Ticker(self.ticker)
        except ImportError:
            logger.warning("yfinance no instalado, usando datos de referencia")
        except Exception as e:
            logger.warning(f"Error cargando datos de yfinance: {e}")
    
    def obtener_info(self) -> InfoAccion:
        """Obtiene información básica del activo"""
        if self._datos_yfinance:
            try:
                info = self._datos_yfinance.info
                return InfoAccion(
                    ticker=self.ticker,
                    nombre=info.get("longName", self._datos_referencia.get("nombre", self.ticker)),
                    precio_actual=info.get("currentPrice", info.get("regularMarketPrice", 0)),
                    moneda=info.get("currency", "EUR"),
                    sector=info.get("sector", self._datos_referencia.get("sector", "")),
                    mercado=info.get("exchange", "MC")
                )
            except Exception:
                pass
        
        return InfoAccion(
            ticker=self.ticker,
            nombre=self._datos_referencia.get("nombre", self.ticker),
            precio_actual=self._datos_referencia.get("precio_referencia", 0),
            moneda="EUR",
            sector=self._datos_referencia.get("sector", ""),
            mercado="BME"
        )
    
    def analizar_dividendos(self, inversion: float = 100_000) -> dict:
        """Analiza los dividendos del activo con histórico de 5 años"""
        info = self.obtener_info()
        dividendos_5y = self._datos_referencia.get("dividendos_5_años", [0, 0, 0, 0, 0])
        
        # Calcular métricas
        media_div = sum(dividendos_5y) / len(dividendos_5y) if dividendos_5y else 0
        ultimo_div = dividendos_5y[-1] if dividendos_5y else 0
        primer_div = dividendos_5y[0] if dividendos_5y else 0
        
        # Crecimiento CAGR
        if primer_div > 0 and ultimo_div > 0:
            cagr = ((ultimo_div / primer_div) ** (1/5) - 1) * 100
        else:
            cagr = 0
        
        # Consistencia del dividendo
        años_con_dividendo = sum(1 for d in dividendos_5y if d > 0)
        if años_con_dividendo == 5:
            consistencia = "Excelente"
        elif años_con_dividendo >= 4:
            consistencia = "Buena"
        elif años_con_dividendo >= 3:
            consistencia = "Regular"
        else:
            consistencia = "Baja"
        
        # Yield actual
        precio = info.precio_actual
        yield_actual = (ultimo_div / precio * 100) if precio > 0 else 0
        
        # Cálculos de inversión
        num_acciones = inversion / precio if precio > 0 else 0
        dividendos_anuales = num_acciones * ultimo_div
        
        return {
            "ticker": self.ticker,
            "nombre": info.nombre,
            "sector": info.sector,
            "precio_actual": precio,
            "inversion": inversion,
            "num_acciones": round(num_acciones, 0),
            "dividendo_ultimo_año": ultimo_div,
            "dividendos_5_años": dividendos_5y,
            "años": ["2019", "2020", "2021", "2022", "2023"],
            "media_dividendos_5_años": round(media_div, 2),
            "yield_actual": round(yield_actual, 2),
            "yield_actual_pct": f"{yield_actual:.2f}%",
            "crecimiento_cagr_5y": round(cagr, 1),
            "crecimiento_cagr_5y_pct": f"{cagr:.1f}%",
            "consistencia": consistencia,
            "años_con_dividendo": años_con_dividendo,
            "dividendos_anuales_estimados": round(dividendos_anuales, 2),
            "dividendos_mensuales_estimados": round(dividendos_anuales / 12, 2)
        }
    
    def analizar_riesgo(self) -> AnalisisRiesgo:
        """Analiza el riesgo del activo para determinar LTV apropiado"""
        volatilidad = self._datos_referencia.get("volatilidad", 0.30)
        beta = self._datos_referencia.get("beta", 1.0)
        max_dd = self._datos_referencia.get("max_drawdown_5y", 0.50)
        
        # Calcular LTV recomendado basado en volatilidad
        if volatilidad < 0.22:
            ltv_recomendado = 0.75
        elif volatilidad < 0.28:
            ltv_recomendado = 0.70
        elif volatilidad < 0.35:
            ltv_recomendado = 0.65
        elif volatilidad < 0.45:
            ltv_recomendado = 0.55
        else:
            ltv_recomendado = 0.50
        
        return AnalisisRiesgo(
            ticker=self.ticker,
            volatilidad_anual=volatilidad,
            beta=beta,
            max_drawdown_5_años=max_dd,
            ltv_recomendado=ltv_recomendado
        )
    
    def resumen_completo(self, inversion: float = 100_000) -> dict:
        """Genera resumen completo del activo"""
        info = self.obtener_info()
        dividendos = self.analizar_dividendos(inversion)
        riesgo = self.analizar_riesgo()
        
        return {
            "activo": {
                "ticker": info.ticker,
                "nombre": info.nombre,
                "precio": info.precio_actual,
                "sector": info.sector,
                "mercado": info.mercado
            },
            "inversion": {
                "capital": inversion,
                "num_acciones": dividendos["num_acciones"],
                "valor_total": dividendos["num_acciones"] * info.precio_actual
            },
            "dividendos": {
                "yield": dividendos["yield_actual_pct"],
                "yield_valor": dividendos["yield_actual"],
                "dividendo_ultimo": dividendos["dividendo_ultimo_año"],
                "media_5_años": dividendos["media_dividendos_5_años"],
                "crecimiento_cagr": dividendos["crecimiento_cagr_5y_pct"],
                "consistencia": dividendos["consistencia"],
                "años_con_dividendo": dividendos["años_con_dividendo"],
                "historico": dividendos["dividendos_5_años"],
                "años": dividendos["años"],
                "total_anual": dividendos["dividendos_anuales_estimados"],
                "total_mensual": dividendos["dividendos_mensuales_estimados"]
            },
            "riesgo": {
                "volatilidad": f"{riesgo.volatilidad_anual*100:.0f}%",
                "volatilidad_valor": riesgo.volatilidad_anual,
                "beta": riesgo.beta,
                "max_drawdown_5y": f"{riesgo.max_drawdown_5_años*100:.0f}%",
                "ltv_recomendado": f"{riesgo.ltv_recomendado*100:.0f}%",
                "ltv_valor": riesgo.ltv_recomendado
            },
            "para_lombardo": {
                "ltv_maximo": riesgo.ltv_recomendado,
                "prestamo_maximo": inversion * riesgo.ltv_recomendado,
                "margen_seguridad": f"{(1-riesgo.ltv_recomendado)*100:.0f}%"
            }
        }


def comparar_ibex35(inversion: float = 100_000, filtro_sector: str = None) -> list[dict]:
    """
    Compara todos los valores del IBEX 35 como opción de inversión.
    
    Args:
        inversion: Cantidad a invertir
        filtro_sector: Filtrar por sector (opcional)
    """
    resultados = []
    
    for ticker in IBEX35_DATOS:
        datos = IBEX35_DATOS[ticker]
        
        # Filtrar por sector si se especifica
        if filtro_sector and datos.get("sector", "").lower() != filtro_sector.lower():
            continue
        
        analizador = AnalizadorActivo(ticker, usar_api=False)
        resumen = analizador.resumen_completo(inversion)
        resultados.append(resumen)
    
    # Ordenar por yield de dividendo (mayor primero)
    resultados.sort(
        key=lambda x: x["dividendos"]["yield_valor"],
        reverse=True
    )
    
    return resultados


def ranking_por_rentabilidad_dividendo(top_n: int = None) -> list[dict]:
    """Devuelve ranking de valores del IBEX 35 por rentabilidad por dividendo"""
    comparativa = comparar_ibex35(100_000)
    
    ranking = []
    for i, valor in enumerate(comparativa, 1):
        ranking.append({
            "posicion": i,
            "ticker": valor["activo"]["ticker"],
            "nombre": valor["activo"]["nombre"],
            "sector": valor["activo"]["sector"],
            "yield": valor["dividendos"]["yield"],
            "yield_valor": valor["dividendos"]["yield_valor"],
            "consistencia": valor["dividendos"]["consistencia"],
            "crecimiento_5y": valor["dividendos"]["crecimiento_cagr"],
            "ltv_recomendado": valor["riesgo"]["ltv_recomendado"],
            "prestamo_sobre_100k": valor["para_lombardo"]["prestamo_maximo"],
            "dividendos_historico": valor["dividendos"]["historico"]
        })
        
        if top_n and i >= top_n:
            break
    
    return ranking


def obtener_sectores() -> list[str]:
    """Devuelve lista de sectores disponibles"""
    sectores = set()
    for datos in IBEX35_DATOS.values():
        sectores.add(datos.get("sector", "Otros"))
    return sorted(list(sectores))


def comparar_por_sector(sector: str, inversion: float = 100_000) -> list[dict]:
    """Compara valores de un sector específico"""
    return comparar_ibex35(inversion, filtro_sector=sector)


# Mantener compatibilidad con código anterior
def comparar_bancos_españoles(inversion: float = 100_000) -> list[dict]:
    """Comparar solo bancos (compatibilidad)"""
    return comparar_por_sector("Banca", inversion)
