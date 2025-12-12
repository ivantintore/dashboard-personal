"""
Comparativa: Préstamo Hipotecario vs Lombardo
==============================================

Para que puedas comparar los costes de financiación, incluimos
también una calculadora de préstamo hipotecario tradicional.

Diferencias clave:
- Hipoteca: Garantía inmobiliaria, amortización mensual, más barato
- Lombardo: Garantía valores, sin amortización, más flexible
"""

from dataclasses import dataclass
from typing import Optional
import math


@dataclass
class CostesHipoteca:
    """Estructura de costes de una hipoteca"""
    capital_prestado: float
    plazo_años: int
    tin_anual: float
    
    # Cuota
    cuota_mensual: float
    total_intereses: float
    total_a_pagar: float
    
    # Gastos iniciales
    gastos_tasacion: float
    gastos_notaria: float
    gastos_registro: float
    gastos_gestoria: float
    comision_apertura: float
    impuestos: float  # AJD
    
    gastos_totales_inicio: float
    tae_efectiva: float


class CalculadoraHipoteca:
    """
    Calculadora de hipotecas tradicionales.
    
    Para comparar con el préstamo lombardo y entender
    la diferencia de costes y estructura.
    """
    
    # Costes típicos mercado español
    TASACION = 300  # €
    NOTARIA_BASE = 500  # € base + variable
    REGISTRO_BASE = 400  # €
    GESTORIA = 400  # €
    AJD = 0.015  # 1.5% en la mayoría de CCAA
    COMISION_APERTURA_TIPICA = 0.005  # 0.5%
    
    def __init__(
        self,
        capital: float,
        plazo_años: int = 25,
        euribor: float = 0.025,
        spread: float = 0.01,  # Hipotecas suelen tener menor spread
        comision_apertura: Optional[float] = None,
        valor_vivienda: Optional[float] = None
    ):
        """
        Args:
            capital: Capital a solicitar
            plazo_años: Plazo de amortización
            euribor: Euribor de referencia
            spread: Diferencial
            comision_apertura: Comisión de apertura (%)
            valor_vivienda: Valor de tasación de la vivienda
        """
        self.capital = capital
        self.plazo_años = plazo_años
        self.euribor = euribor
        self.spread = spread
        self.comision_apertura = comision_apertura or self.COMISION_APERTURA_TIPICA
        self.valor_vivienda = valor_vivienda or capital / 0.8  # Asumimos LTV 80%
        
        self.tin = euribor + spread
        
    def _calcular_cuota_francesa(self) -> float:
        """
        Calcula la cuota mensual con sistema francés (cuota constante).
        
        Fórmula: C = P * (r * (1+r)^n) / ((1+r)^n - 1)
        donde:
            P = Principal
            r = tipo mensual
            n = número de cuotas
        """
        r = self.tin / 12  # Tipo mensual
        n = self.plazo_años * 12  # Número de cuotas
        
        if r == 0:
            return self.capital / n
        
        cuota = self.capital * (r * (1 + r)**n) / ((1 + r)**n - 1)
        return cuota
    
    def calcular_costes(self) -> CostesHipoteca:
        """Calcula todos los costes de la hipoteca"""
        
        cuota_mensual = self._calcular_cuota_francesa()
        n_cuotas = self.plazo_años * 12
        
        total_a_pagar = cuota_mensual * n_cuotas
        total_intereses = total_a_pagar - self.capital
        
        # Gastos iniciales
        comision_apertura_euros = self.capital * self.comision_apertura
        
        # Notaría escala según importe
        gastos_notaria = self.NOTARIA_BASE + self.capital * 0.001
        gastos_registro = self.REGISTRO_BASE + self.capital * 0.0005
        
        # AJD sobre el capital
        impuestos = self.capital * self.AJD
        
        gastos_totales = (
            self.TASACION +
            gastos_notaria +
            gastos_registro +
            self.GESTORIA +
            comision_apertura_euros +
            impuestos
        )
        
        # TAE efectiva (aproximada)
        # Considera todos los gastos distribuidos en el tiempo
        coste_total = total_a_pagar + gastos_totales - self.capital
        tae = (coste_total / self.capital) / self.plazo_años
        
        return CostesHipoteca(
            capital_prestado=self.capital,
            plazo_años=self.plazo_años,
            tin_anual=self.tin,
            cuota_mensual=cuota_mensual,
            total_intereses=total_intereses,
            total_a_pagar=total_a_pagar,
            gastos_tasacion=self.TASACION,
            gastos_notaria=gastos_notaria,
            gastos_registro=gastos_registro,
            gastos_gestoria=self.GESTORIA,
            comision_apertura=comision_apertura_euros,
            impuestos=impuestos,
            gastos_totales_inicio=gastos_totales,
            tae_efectiva=tae
        )
    
    def tabla_amortizacion(self, primeros_años: int = 5) -> list[dict]:
        """
        Genera tabla de amortización (sistema francés).
        """
        cuota = self._calcular_cuota_francesa()
        capital_pendiente = self.capital
        tabla = []
        
        for año in range(1, min(primeros_años + 1, self.plazo_años + 1)):
            intereses_año = 0
            amortizacion_año = 0
            
            for mes in range(12):
                if capital_pendiente <= 0:
                    break
                    
                interes_mes = capital_pendiente * (self.tin / 12)
                amortizacion_mes = min(cuota - interes_mes, capital_pendiente)
                
                intereses_año += interes_mes
                amortizacion_año += amortizacion_mes
                capital_pendiente -= amortizacion_mes
            
            tabla.append({
                "año": año,
                "capital_pendiente_inicio": capital_pendiente + amortizacion_año,
                "cuota_anual": cuota * 12,
                "intereses": intereses_año,
                "amortizacion": amortizacion_año,
                "capital_pendiente_fin": max(0, capital_pendiente)
            })
        
        return tabla
    
    def resumen(self) -> dict:
        """Genera resumen completo de la hipoteca"""
        costes = self.calcular_costes()
        
        return {
            "prestamo": {
                "capital": self.capital,
                "plazo_años": self.plazo_años,
                "valor_vivienda": self.valor_vivienda,
                "ltv": self.capital / self.valor_vivienda,
                "euribor": self.euribor,
                "spread": self.spread,
                "tin": self.tin
            },
            "cuota": {
                "cuota_mensual": costes.cuota_mensual,
                "cuota_anual": costes.cuota_mensual * 12,
                "total_intereses": costes.total_intereses,
                "total_a_pagar": costes.total_a_pagar
            },
            "gastos_iniciales": {
                "tasacion": costes.gastos_tasacion,
                "notaria": costes.gastos_notaria,
                "registro": costes.gastos_registro,
                "gestoria": costes.gastos_gestoria,
                "comision_apertura": costes.comision_apertura,
                "impuestos_ajd": costes.impuestos,
                "total": costes.gastos_totales_inicio
            },
            "resumen": {
                "tin": f"{self.tin*100:.2f}%",
                "tae_efectiva": f"{costes.tae_efectiva*100:.2f}%",
                "coste_primer_año": costes.cuota_mensual * 12 + costes.gastos_totales_inicio
            }
        }


def comparar_hipoteca_vs_lombardo(
    capital: float,
    hipoteca_params: dict,
    lombardo_params: dict
) -> dict:
    """
    Compara los costes de una hipoteca vs un préstamo lombardo.
    
    Útil para entender las diferencias de coste y estructura.
    """
    from .lombardo import CalculadoraLombardo
    
    # Calcular hipoteca
    hipoteca = CalculadoraHipoteca(
        capital=capital,
        plazo_años=hipoteca_params.get("plazo_años", 25),
        euribor=hipoteca_params.get("euribor", 0.025),
        spread=hipoteca_params.get("spread", 0.01)
    )
    
    # Calcular lombardo
    # Para el lombardo, necesitamos más garantía
    valor_garantia = capital / lombardo_params.get("ltv", 0.70)
    lombardo = CalculadoraLombardo(
        valor_garantia=valor_garantia,
        ltv=lombardo_params.get("ltv", 0.70),
        euribor=lombardo_params.get("euribor", 0.025),
        spread=lombardo_params.get("spread", 0.015)
    )
    
    h_costes = hipoteca.calcular_costes()
    l_costes = lombardo.calcular_costes()
    
    return {
        "capital_solicitado": capital,
        "hipoteca": {
            "tipo": "Hipoteca tradicional",
            "tin": f"{hipoteca.tin*100:.2f}%",
            "cuota_mensual": h_costes.cuota_mensual,
            "coste_anual": h_costes.cuota_mensual * 12,
            "gastos_iniciales": h_costes.gastos_totales_inicio,
            "plazo": f"{hipoteca.plazo_años} años",
            "garantia": "Inmueble",
            "amortizacion": "Mensual (sistema francés)"
        },
        "lombardo": {
            "tipo": "Préstamo Lombardo",
            "tin": f"{lombardo.tin*100:.2f}%",
            "cuota_mensual": l_costes.coste_mensual,
            "coste_anual": l_costes.intereses_anuales,
            "gastos_iniciales": l_costes.comision_apertura_euros + l_costes.gastos_estudio,
            "plazo": "Renovable anualmente",
            "garantia": f"Valores ({valor_garantia:,.0f}€)",
            "amortizacion": "Bullet (solo intereses)"
        },
        "comparativa": {
            "diferencia_cuota_mensual": l_costes.coste_mensual - h_costes.cuota_mensual,
            "diferencia_gastos_iniciales": (
                (l_costes.comision_apertura_euros + l_costes.gastos_estudio) - 
                h_costes.gastos_totales_inicio
            ),
            "nota": (
                "El lombardo tiene cuota más baja (solo intereses) pero no amortiza capital. "
                "La hipoteca tiene cuota más alta pero al final eres propietario."
            )
        }
    }

