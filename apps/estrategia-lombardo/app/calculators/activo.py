"""
Estudio 2: Análisis del Activo (Acciones)
=========================================

Análisis de los activos que usarás como garantía del préstamo lombardo.
Nos centramos en acciones bancarias españolas por su alto dividendo.

Bancos españoles principales:
- Santander (SAN.MC): Gran diversificación geográfica
- BBVA (BBVA.MC): Fuerte presencia en México y España
- CaixaBank (CABK.MC): Líder en banca retail España
- Bankinter (BKT.MC): Rentabilidad sobre recursos propios alta
- Sabadell (SAB.MC): Banca retail y TSB en UK

Consideraciones para el Lombardo:
- Mayor volatilidad = menor LTV concedido
- Historial de dividendos importa
- Liquidez del valor
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
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
    dividendo_anual: float  # € por acción
    rentabilidad_dividendo: float  # Yield %
    payout_ratio: Optional[float]  # % del beneficio repartido
    dividendos_ultimos_5_años: list[float]
    media_dividendos_5_años: float
    crecimiento_dividendo: float  # CAGR 5 años
    proximo_dividendo: Optional[dict]


@dataclass
class AnalisisRiesgo:
    """Análisis de riesgo de la acción"""
    ticker: str
    volatilidad_anual: float  # Desviación estándar anualizada
    beta: float  # Beta respecto al mercado
    max_drawdown_1_año: float  # Máxima caída en 1 año
    max_drawdown_5_años: float  # Máxima caída en 5 años
    ltv_recomendado: float  # LTV recomendado dado el riesgo


# Datos de referencia de bancos españoles
# (En producción, estos vendrían de yfinance o API)
BANCOS_ESPAÑOLES = {
    "SAN.MC": {
        "nombre": "Banco Santander",
        "ticker": "SAN.MC",
        "sector": "Financiero - Banca",
        "descripcion": "Mayor banco de la zona euro por capitalización",
        "precio_referencia": 4.50,
        "dividendo_2023": 0.17,  # € por acción aprox
        "yield_aprox": 3.8,
        "volatilidad_historica": 0.35,
        "ltv_tipico": 0.60,  # Más volátil = menor LTV
        "beta": 1.3
    },
    "BBVA.MC": {
        "nombre": "BBVA",
        "ticker": "BBVA.MC", 
        "sector": "Financiero - Banca",
        "descripcion": "Fuerte presencia en México y España",
        "precio_referencia": 9.50,
        "dividendo_2023": 0.66,
        "yield_aprox": 7.0,
        "volatilidad_historica": 0.32,
        "ltv_tipico": 0.65,
        "beta": 1.2
    },
    "CABK.MC": {
        "nombre": "CaixaBank",
        "ticker": "CABK.MC",
        "sector": "Financiero - Banca",
        "descripcion": "Líder en banca retail en España",
        "precio_referencia": 5.20,
        "dividendo_2023": 0.39,
        "yield_aprox": 7.5,
        "volatilidad_historica": 0.30,
        "ltv_tipico": 0.65,
        "beta": 1.1
    },
    "BKT.MC": {
        "nombre": "Bankinter",
        "ticker": "BKT.MC",
        "sector": "Financiero - Banca",
        "descripcion": "Alta rentabilidad, banca selectiva",
        "precio_referencia": 7.50,
        "dividendo_2023": 0.45,
        "yield_aprox": 6.0,
        "volatilidad_historica": 0.28,
        "ltv_tipico": 0.70,
        "beta": 0.95
    },
    "SAB.MC": {
        "nombre": "Banco Sabadell",
        "ticker": "SAB.MC",
        "sector": "Financiero - Banca",
        "descripcion": "Banca retail España y TSB en UK",
        "precio_referencia": 1.80,
        "dividendo_2023": 0.08,
        "yield_aprox": 4.5,
        "volatilidad_historica": 0.40,
        "ltv_tipico": 0.55,
        "beta": 1.4
    }
}


class AnalizadorActivo:
    """
    Analizador de activos para usar como garantía.
    
    Ejemplo:
        analizador = AnalizadorActivo("BBVA.MC")
        info = analizador.obtener_info()
        dividendos = analizador.analizar_dividendos()
        riesgo = analizador.analizar_riesgo()
    """
    
    def __init__(self, ticker: str, usar_api: bool = False):
        """
        Args:
            ticker: Símbolo del valor (ej: "BBVA.MC")
            usar_api: Si True, intenta obtener datos de yfinance
        """
        self.ticker = ticker.upper()
        self.usar_api = usar_api
        self._datos_referencia = BANCOS_ESPAÑOLES.get(self.ticker, {})
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
                    sector=info.get("sector", "Financiero"),
                    mercado=info.get("exchange", "MC")
                )
            except Exception:
                pass
        
        # Usar datos de referencia
        return InfoAccion(
            ticker=self.ticker,
            nombre=self._datos_referencia.get("nombre", self.ticker),
            precio_actual=self._datos_referencia.get("precio_referencia", 0),
            moneda="EUR",
            sector=self._datos_referencia.get("sector", "Financiero"),
            mercado="BME"
        )
    
    def analizar_dividendos(self, inversion: float = 100_000) -> dict:
        """
        Analiza los dividendos del activo.
        
        Args:
            inversion: Cantidad invertida en euros
        
        Returns:
            Análisis completo de dividendos
        """
        info = self.obtener_info()
        
        yield_aprox = self._datos_referencia.get("yield_aprox", 5.0) / 100
        dividendo_por_accion = self._datos_referencia.get("dividendo_2023", 0)
        
        # Calcular con datos reales si están disponibles
        if self._datos_yfinance:
            try:
                yf_info = self._datos_yfinance.info
                yield_aprox = yf_info.get("dividendYield", yield_aprox)
                dividendo_por_accion = yf_info.get("dividendRate", dividendo_por_accion)
            except Exception:
                pass
        
        # Número de acciones que puedes comprar
        precio = info.precio_actual
        if precio > 0:
            num_acciones = inversion / precio
            dividendos_anuales = num_acciones * dividendo_por_accion
        else:
            num_acciones = 0
            dividendos_anuales = inversion * yield_aprox
        
        return {
            "ticker": self.ticker,
            "nombre": info.nombre,
            "precio_actual": precio,
            "inversion": inversion,
            "num_acciones": num_acciones,
            "dividendo_por_accion": dividendo_por_accion,
            "rentabilidad_dividendo": yield_aprox,
            "rentabilidad_dividendo_pct": f"{yield_aprox*100:.2f}%",
            "dividendos_anuales_estimados": dividendos_anuales,
            "dividendos_mensuales_estimados": dividendos_anuales / 12,
            "nota": (
                "Los dividendos no están garantizados y pueden variar. "
                "Datos basados en histórico reciente."
            )
        }
    
    def analizar_riesgo(self) -> AnalisisRiesgo:
        """Analiza el riesgo del activo para determinar LTV apropiado"""
        volatilidad = self._datos_referencia.get("volatilidad_historica", 0.30)
        beta = self._datos_referencia.get("beta", 1.0)
        
        if self._datos_yfinance:
            try:
                # Calcular volatilidad histórica
                hist = self._datos_yfinance.history(period="1y")
                if not hist.empty and "Close" in hist.columns:
                    returns = hist["Close"].pct_change().dropna()
                    volatilidad = returns.std() * (252 ** 0.5)  # Anualizada
                    
                yf_info = self._datos_yfinance.info
                beta = yf_info.get("beta", beta)
            except Exception:
                pass
        
        # Calcular LTV recomendado basado en volatilidad
        # Regla: Mayor volatilidad = menor LTV
        if volatilidad < 0.25:
            ltv_recomendado = 0.75
        elif volatilidad < 0.35:
            ltv_recomendado = 0.65
        elif volatilidad < 0.45:
            ltv_recomendado = 0.55
        else:
            ltv_recomendado = 0.50
        
        # Max drawdown estimado (aproximación basada en volatilidad)
        max_dd_1y = volatilidad * 2.5  # Aproximación
        max_dd_5y = volatilidad * 3.5
        
        return AnalisisRiesgo(
            ticker=self.ticker,
            volatilidad_anual=volatilidad,
            beta=beta,
            max_drawdown_1_año=min(max_dd_1y, 0.70),
            max_drawdown_5_años=min(max_dd_5y, 0.85),
            ltv_recomendado=self._datos_referencia.get("ltv_tipico", ltv_recomendado)
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
                "yield": dividendos["rentabilidad_dividendo_pct"],
                "dividendo_por_accion": dividendos["dividendo_por_accion"],
                "total_anual": dividendos["dividendos_anuales_estimados"],
                "total_mensual": dividendos["dividendos_mensuales_estimados"]
            },
            "riesgo": {
                "volatilidad": f"{riesgo.volatilidad_anual*100:.1f}%",
                "beta": riesgo.beta,
                "max_drawdown_1y": f"{riesgo.max_drawdown_1_año*100:.0f}%",
                "ltv_recomendado": f"{riesgo.ltv_recomendado*100:.0f}%"
            },
            "para_lombardo": {
                "ltv_maximo": riesgo.ltv_recomendado,
                "prestamo_maximo": inversion * riesgo.ltv_recomendado,
                "margen_seguridad": f"{(1-riesgo.ltv_recomendado)*100:.0f}%"
            }
        }


def comparar_bancos_españoles(inversion: float = 100_000) -> list[dict]:
    """
    Compara los principales bancos españoles como opción de inversión.
    
    Útil para decidir qué banco usar como garantía.
    """
    resultados = []
    
    for ticker in BANCOS_ESPAÑOLES:
        analizador = AnalizadorActivo(ticker, usar_api=False)
        resumen = analizador.resumen_completo(inversion)
        
        # Añadir descripción
        resumen["descripcion"] = BANCOS_ESPAÑOLES[ticker].get("descripcion", "")
        
        resultados.append(resumen)
    
    # Ordenar por yield de dividendo (mayor primero)
    resultados.sort(
        key=lambda x: float(x["dividendos"]["yield"].replace("%", "")),
        reverse=True
    )
    
    return resultados


def ranking_por_rentabilidad_dividendo() -> list[dict]:
    """Devuelve ranking de bancos por rentabilidad por dividendo"""
    comparativa = comparar_bancos_españoles(100_000)
    
    ranking = []
    for i, banco in enumerate(comparativa, 1):
        ranking.append({
            "posicion": i,
            "ticker": banco["activo"]["ticker"],
            "nombre": banco["activo"]["nombre"],
            "yield": banco["dividendos"]["yield"],
            "ltv_recomendado": banco["riesgo"]["ltv_recomendado"],
            "prestamo_sobre_100k": banco["para_lombardo"]["prestamo_maximo"]
        })
    
    return ranking

