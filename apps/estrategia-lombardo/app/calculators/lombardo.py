"""
Estudio 1: Calculadora de Crédito Lombardo
==========================================

Un préstamo lombardo es un crédito garantizado con valores (acciones, bonos, fondos).
Los bancos típicamente prestan entre 50-80% del valor de los activos.

Características:
- LTV (Loan-to-Value): 50-80% según el activo
- Tipo de interés: Euribor + spread (típicamente 1-3%)
- Sin amortización obligatoria (suele ser bullet o renovable)
- Margin Call si el valor de la garantía cae por debajo de cierto umbral
"""

from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass
class CostesLombardo:
    """Estructura de costes de un préstamo lombardo"""
    capital_prestado: float
    tin_anual: float  # Tipo de Interés Nominal anual
    comision_apertura: float  # Porcentaje
    comision_apertura_euros: float
    comision_mantenimiento_anual: float  # Euros/año
    gastos_estudio: float  # Euros
    gastos_notaria: float  # Euros (si aplica)
    
    # Calculados
    intereses_anuales: float
    coste_total_primer_año: float
    tae_efectiva: float
    coste_mensual: float


@dataclass 
class AnalisisMarginCall:
    """Análisis de riesgo de margin call"""
    valor_garantia_inicial: float
    ltv_inicial: float
    ltv_margin_call: float  # Típicamente 80-90%
    ltv_liquidacion: float  # Típicamente 95-100%
    
    caida_hasta_margin_call: float  # Porcentaje de caída del activo
    caida_hasta_liquidacion: float
    valor_margin_call: float  # Valor de garantía que dispara margin call
    valor_liquidacion: float


class CalculadoraLombardo:
    """
    Calculadora completa de préstamos lombardos.
    
    Ejemplo de uso:
        calc = CalculadoraLombardo(
            valor_garantia=100_000,
            ltv=0.70,
            euribor=0.035,
            spread=0.015
        )
        costes = calc.calcular_costes()
        margin = calc.analizar_margin_call()
    """
    
    # Costes típicos del mercado español
    COMISION_APERTURA_TIPICA = 0.005  # 0.5%
    COMISION_MANTENIMIENTO_ANUAL = 50  # €
    GASTOS_ESTUDIO = 150  # €
    
    # Umbrales de margin call típicos
    LTV_MARGIN_CALL = 0.85  # Te llaman para pedir más garantía
    LTV_LIQUIDACION = 0.95  # Venden tu garantía
    
    def __init__(
        self,
        valor_garantia: float,
        ltv: float = 0.70,
        euribor: float = 0.025,  # Euribor 12M actual ~2.5%
        spread: float = 0.015,   # Spread típico 1-2%
        comision_apertura: Optional[float] = None,
        plazo_años: int = 1
    ):
        """
        Args:
            valor_garantia: Valor de los activos en garantía (€)
            ltv: Loan-to-Value (0.50-0.80 típico)
            euribor: Euribor de referencia (anual)
            spread: Diferencial sobre Euribor
            comision_apertura: Comisión de apertura (% decimal)
            plazo_años: Plazo del préstamo
        """
        self.valor_garantia = valor_garantia
        self.ltv = ltv
        self.euribor = euribor
        self.spread = spread
        self.comision_apertura = comision_apertura or self.COMISION_APERTURA_TIPICA
        self.plazo_años = plazo_años
        
        # Capital que te prestan
        self.capital_prestado = valor_garantia * ltv
        
        # TIN = Euribor + Spread
        self.tin = euribor + spread
        
    def calcular_costes(self) -> CostesLombardo:
        """Calcula todos los costes del préstamo lombardo"""
        
        # Comisión de apertura
        comision_apertura_euros = self.capital_prestado * self.comision_apertura
        
        # Intereses anuales (préstamo bullet, solo intereses)
        intereses_anuales = self.capital_prestado * self.tin
        
        # Coste total primer año
        coste_total_primer_año = (
            comision_apertura_euros +
            self.GASTOS_ESTUDIO +
            self.COMISION_MANTENIMIENTO_ANUAL +
            intereses_anuales
        )
        
        # TAE efectiva (considerando todos los costes)
        # TAE = ((1 + coste_total/capital)^(1/plazo) - 1)
        tae_efectiva = coste_total_primer_año / self.capital_prestado
        
        # Coste mensual (solo intereses, sin amortización)
        coste_mensual = intereses_anuales / 12
        
        return CostesLombardo(
            capital_prestado=self.capital_prestado,
            tin_anual=self.tin,
            comision_apertura=self.comision_apertura,
            comision_apertura_euros=comision_apertura_euros,
            comision_mantenimiento_anual=self.COMISION_MANTENIMIENTO_ANUAL,
            gastos_estudio=self.GASTOS_ESTUDIO,
            gastos_notaria=0,  # Los lombardos no suelen ir a notaría
            intereses_anuales=intereses_anuales,
            coste_total_primer_año=coste_total_primer_año,
            tae_efectiva=tae_efectiva,
            coste_mensual=coste_mensual
        )
    
    def analizar_margin_call(
        self,
        ltv_margin_call: Optional[float] = None,
        ltv_liquidacion: Optional[float] = None
    ) -> AnalisisMarginCall:
        """
        Analiza cuánto puede caer el activo antes de recibir un margin call.
        
        El margin call ocurre cuando:
        LTV_actual = Préstamo / Valor_Garantía_Actual > LTV_margin_call
        
        Despejando:
        Valor_Garantía_Actual = Préstamo / LTV_margin_call
        Caída = 1 - (Valor_Garantía_Actual / Valor_Garantía_Inicial)
        """
        ltv_margin = ltv_margin_call or self.LTV_MARGIN_CALL
        ltv_liquid = ltv_liquidacion or self.LTV_LIQUIDACION
        
        # Valor de la garantía que dispara margin call
        valor_margin_call = self.capital_prestado / ltv_margin
        valor_liquidacion = self.capital_prestado / ltv_liquid
        
        # Caída porcentual hasta margin call
        caida_margin = 1 - (valor_margin_call / self.valor_garantia)
        caida_liquidacion = 1 - (valor_liquidacion / self.valor_garantia)
        
        return AnalisisMarginCall(
            valor_garantia_inicial=self.valor_garantia,
            ltv_inicial=self.ltv,
            ltv_margin_call=ltv_margin,
            ltv_liquidacion=ltv_liquid,
            caida_hasta_margin_call=caida_margin,
            caida_hasta_liquidacion=caida_liquidacion,
            valor_margin_call=valor_margin_call,
            valor_liquidacion=valor_liquidacion
        )
    
    def tabla_amortizacion(self, años: int = 5) -> list[dict]:
        """
        Genera tabla de costes anuales (préstamo bullet, solo intereses).
        
        En un lombardo típico no hay amortización obligatoria.
        Solo pagas intereses y al final devuelves el principal.
        """
        costes = self.calcular_costes()
        tabla = []
        
        for año in range(1, años + 1):
            es_primer_año = año == 1
            
            # Costes fijos solo el primer año
            costes_iniciales = 0
            if es_primer_año:
                costes_iniciales = (
                    costes.comision_apertura_euros + 
                    costes.gastos_estudio
                )
            
            tabla.append({
                "año": año,
                "capital_pendiente": self.capital_prestado,
                "intereses": costes.intereses_anuales,
                "mantenimiento": costes.comision_mantenimiento_anual,
                "costes_iniciales": costes_iniciales,
                "coste_total_año": (
                    costes.intereses_anuales + 
                    costes.comision_mantenimiento_anual +
                    costes_iniciales
                )
            })
        
        return tabla
    
    def resumen(self) -> dict:
        """Genera resumen completo del préstamo"""
        costes = self.calcular_costes()
        margin = self.analizar_margin_call()
        
        return {
            "prestamo": {
                "valor_garantia": self.valor_garantia,
                "ltv": self.ltv,
                "capital_prestado": self.capital_prestado,
                "euribor": self.euribor,
                "spread": self.spread,
                "tin": self.tin,
                "plazo_años": self.plazo_años
            },
            "costes": {
                "tin_anual": f"{self.tin*100:.2f}%",
                "tae_efectiva": f"{costes.tae_efectiva*100:.2f}%",
                "intereses_anuales": costes.intereses_anuales,
                "coste_mensual": costes.coste_mensual,
                "comision_apertura": costes.comision_apertura_euros,
                "gastos_totales_inicio": (
                    costes.comision_apertura_euros + 
                    costes.gastos_estudio
                ),
                "coste_total_primer_año": costes.coste_total_primer_año
            },
            "riesgo": {
                "ltv_margin_call": f"{margin.ltv_margin_call*100:.0f}%",
                "caida_hasta_margin_call": f"{margin.caida_hasta_margin_call*100:.1f}%",
                "valor_margin_call": margin.valor_margin_call,
                "ltv_liquidacion": f"{margin.ltv_liquidacion*100:.0f}%",
                "caida_hasta_liquidacion": f"{margin.caida_hasta_liquidacion*100:.1f}%"
            }
        }


def comparar_lombardos(
    valor_garantia: float,
    escenarios: list[dict]
) -> list[dict]:
    """
    Compara diferentes escenarios de préstamos lombardos.
    
    Args:
        valor_garantia: Valor de la garantía
        escenarios: Lista de dicts con parámetros {nombre, ltv, euribor, spread}
    
    Returns:
        Lista de resúmenes comparativos
    """
    resultados = []
    
    for escenario in escenarios:
        calc = CalculadoraLombardo(
            valor_garantia=valor_garantia,
            ltv=escenario.get("ltv", 0.70),
            euribor=escenario.get("euribor", 0.025),
            spread=escenario.get("spread", 0.015)
        )
        
        resumen = calc.resumen()
        resumen["nombre"] = escenario.get("nombre", "Sin nombre")
        resultados.append(resumen)
    
    return resultados

