"""
Estudio 3: Análisis de Inversión del Préstamo
=============================================

¿En qué invertir el dinero del préstamo lombardo para que rinda
más que el coste del préstamo?

Opciones típicas ordenadas por riesgo:
1. Letras del Tesoro / Bonos del Estado (bajo riesgo)
2. Depósitos bancarios (muy bajo riesgo)
3. Fondos de renta fija (bajo-medio riesgo)
4. Fondos mixtos (medio riesgo)
5. Acciones adicionales (alto riesgo - apalancamiento sobre apalancamiento)
6. REITs / SOCIMIs (medio riesgo, buen yield)

La clave es que el SPREAD (rentabilidad - coste) sea positivo.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class OpcionInversion:
    """Representa una opción de inversión"""
    nombre: str
    tipo: str
    rentabilidad_esperada: float  # Anual
    riesgo: str  # Bajo, Medio, Alto
    liquidez: str  # Alta, Media, Baja
    plazo_minimo: str
    fiscalidad: str
    descripcion: str


# Opciones de inversión actualizadas 2024
OPCIONES_INVERSION = {
    "letras_tesoro_12m": OpcionInversion(
        nombre="Letras del Tesoro 12 meses",
        tipo="Renta Fija Gobierno",
        rentabilidad_esperada=0.030,  # ~3.0% dic 2024
        riesgo="Muy Bajo",
        liquidez="Alta",
        plazo_minimo="12 meses",
        fiscalidad="Base del ahorro (19-26%)",
        descripcion="Deuda del Estado español. Máxima seguridad. Subastas mensuales."
    ),
    "letras_tesoro_6m": OpcionInversion(
        nombre="Letras del Tesoro 6 meses",
        tipo="Renta Fija Gobierno",
        rentabilidad_esperada=0.028,  # ~2.8%
        riesgo="Muy Bajo",
        liquidez="Alta",
        plazo_minimo="6 meses",
        fiscalidad="Base del ahorro (19-26%)",
        descripcion="Plazo más corto. Ideal para gestionar liquidez."
    ),
    "bonos_estado_3a": OpcionInversion(
        nombre="Bonos del Estado 3 años",
        tipo="Renta Fija Gobierno",
        rentabilidad_esperada=0.025,  # ~2.5%
        riesgo="Muy Bajo",
        liquidez="Alta",
        plazo_minimo="3 años (o venta secundario)",
        fiscalidad="Base del ahorro (19-26%)",
        descripcion="Mayor duración, cupón periódico."
    ),
    "deposito_12m": OpcionInversion(
        nombre="Depósito Bancario 12 meses",
        tipo="Depósito Garantizado",
        rentabilidad_esperada=0.030,  # Mejores ofertas ~3%
        riesgo="Muy Bajo",
        liquidez="Baja",
        plazo_minimo="12 meses",
        fiscalidad="Base del ahorro (19-26%)",
        descripcion="Cubierto por FGD hasta 100.000€. Penalización por cancelación anticipada."
    ),
    "cuenta_remunerada": OpcionInversion(
        nombre="Cuenta Remunerada",
        tipo="Cuenta Corriente",
        rentabilidad_esperada=0.025,  # Trade Republic, etc ~2.5%
        riesgo="Muy Bajo",
        liquidez="Muy Alta",
        plazo_minimo="Sin mínimo",
        fiscalidad="Base del ahorro (19-26%)",
        descripcion="Liquidez inmediata. Sin penalizaciones. Trade Republic, Revolut, etc."
    ),
    "fondo_monetario": OpcionInversion(
        nombre="Fondo Monetario",
        tipo="Fondo de Inversión",
        rentabilidad_esperada=0.032,  # ~3.2%
        riesgo="Muy Bajo",
        liquidez="Alta",
        plazo_minimo="1-2 días (reembolso)",
        fiscalidad="Base del ahorro + traspaso sin tributar",
        descripcion="Invierte en activos a muy corto plazo. Ventaja fiscal de los fondos."
    ),
    "fondo_rf_corto": OpcionInversion(
        nombre="Fondo Renta Fija Corto Plazo",
        tipo="Fondo de Inversión",
        rentabilidad_esperada=0.035,  # ~3.5%
        riesgo="Bajo",
        liquidez="Alta",
        plazo_minimo="1-2 días (reembolso)",
        fiscalidad="Base del ahorro + traspaso sin tributar",
        descripcion="Deuda corporativa y gobierno a corto plazo. Mayor yield que monetarios."
    ),
    "fondo_rf_flexible": OpcionInversion(
        nombre="Fondo Renta Fija Flexible",
        tipo="Fondo de Inversión",
        rentabilidad_esperada=0.040,  # ~4%
        riesgo="Medio-Bajo",
        liquidez="Alta",
        plazo_minimo="1-2 días (reembolso)",
        fiscalidad="Base del ahorro + traspaso sin tributar",
        descripcion="Gestión activa de duración. Mayor potencial pero más volatilidad."
    ),
    "socimi_merlin": OpcionInversion(
        nombre="SOCIMI (Merlin Properties)",
        tipo="REIT / Inmobiliario",
        rentabilidad_esperada=0.055,  # ~5.5% yield
        riesgo="Medio",
        liquidez="Alta",
        plazo_minimo="Sin mínimo (cotiza)",
        fiscalidad="Base del ahorro (19-26%)",
        descripcion="Oficinas, centros comerciales, logístico. Alto dividendo pero volátil."
    ),
    "etf_dividendos_europa": OpcionInversion(
        nombre="ETF Dividendos Europa",
        tipo="ETF Renta Variable",
        rentabilidad_esperada=0.045,  # ~4.5% yield
        riesgo="Medio-Alto",
        liquidez="Alta",
        plazo_minimo="Sin mínimo",
        fiscalidad="Base del ahorro (19-26%)",
        descripcion="Diversificación en acciones europeas de alto dividendo."
    )
}


class AnalizadorInversion:
    """
    Analiza las opciones de inversión para el préstamo lombardo.
    
    Ejemplo:
        analizador = AnalizadorInversion(
            capital_prestamo=70_000,
            coste_prestamo=0.04  # 4% TAE
        )
        opciones = analizador.analizar_todas_opciones()
        mejor = analizador.mejor_opcion_por_criterio("spread")
    """
    
    def __init__(
        self,
        capital_prestamo: float,
        coste_prestamo: float,  # TAE del préstamo
        perfil_riesgo: str = "conservador"  # conservador, moderado, agresivo
    ):
        """
        Args:
            capital_prestamo: Capital del préstamo lombardo
            coste_prestamo: Coste TAE del préstamo (decimal)
            perfil_riesgo: Perfil de riesgo del inversor
        """
        self.capital = capital_prestamo
        self.coste = coste_prestamo
        self.perfil = perfil_riesgo
        
    def analizar_opcion(self, opcion: OpcionInversion) -> dict:
        """Analiza una opción de inversión específica"""
        
        # Rentabilidad bruta anual
        rentabilidad_bruta = self.capital * opcion.rentabilidad_esperada
        
        # Coste del préstamo
        coste_prestamo = self.capital * self.coste
        
        # Spread (beneficio neto antes de impuestos)
        spread = opcion.rentabilidad_esperada - self.coste
        beneficio_neto = self.capital * spread
        
        # Rentabilidad neta después de impuestos (estimación)
        # Asumimos tipo marginal 21% sobre beneficio
        tipo_impuesto = 0.21
        rentabilidad_neta_impuestos = rentabilidad_bruta * (1 - tipo_impuesto)
        beneficio_neto_impuestos = beneficio_neto * (1 - tipo_impuesto) if beneficio_neto > 0 else beneficio_neto
        
        # ¿Es rentable?
        es_rentable = spread > 0
        
        return {
            "opcion": {
                "nombre": opcion.nombre,
                "tipo": opcion.tipo,
                "riesgo": opcion.riesgo,
                "liquidez": opcion.liquidez,
                "plazo_minimo": opcion.plazo_minimo
            },
            "numeros": {
                "capital_invertido": self.capital,
                "rentabilidad_esperada": f"{opcion.rentabilidad_esperada*100:.2f}%",
                "coste_prestamo": f"{self.coste*100:.2f}%",
                "spread": f"{spread*100:.2f}%",
                "rentabilidad_bruta_anual": rentabilidad_bruta,
                "coste_prestamo_anual": coste_prestamo,
                "beneficio_neto_anual": beneficio_neto,
                "beneficio_neto_mensual": beneficio_neto / 12
            },
            "fiscal": {
                "tipo_impuesto_estimado": f"{tipo_impuesto*100:.0f}%",
                "rentabilidad_neta_impuestos": rentabilidad_neta_impuestos,
                "beneficio_neto_impuestos": beneficio_neto_impuestos
            },
            "conclusion": {
                "es_rentable": es_rentable,
                "veredicto": "✅ RENTABLE" if es_rentable else "❌ NO RENTABLE",
                "nota": opcion.descripcion
            }
        }
    
    def analizar_todas_opciones(self) -> list[dict]:
        """Analiza todas las opciones de inversión disponibles"""
        resultados = []
        
        for key, opcion in OPCIONES_INVERSION.items():
            analisis = self.analizar_opcion(opcion)
            analisis["key"] = key
            resultados.append(analisis)
        
        # Ordenar por spread (mayor primero)
        resultados.sort(
            key=lambda x: float(x["numeros"]["spread"].replace("%", "")),
            reverse=True
        )
        
        return resultados
    
    def filtrar_por_perfil(self) -> list[dict]:
        """Filtra opciones según el perfil de riesgo"""
        todas = self.analizar_todas_opciones()
        
        if self.perfil == "conservador":
            riesgos_permitidos = ["Muy Bajo", "Bajo"]
        elif self.perfil == "moderado":
            riesgos_permitidos = ["Muy Bajo", "Bajo", "Medio-Bajo", "Medio"]
        else:  # agresivo
            riesgos_permitidos = ["Muy Bajo", "Bajo", "Medio-Bajo", "Medio", "Medio-Alto", "Alto"]
        
        return [
            op for op in todas 
            if op["opcion"]["riesgo"] in riesgos_permitidos
        ]
    
    def mejor_opcion(self, criterio: str = "spread") -> dict:
        """
        Encuentra la mejor opción según criterio.
        
        Criterios:
            - spread: Mayor diferencia entre rentabilidad y coste
            - rentabilidad: Mayor rentabilidad (sin considerar riesgo)
            - seguridad: Menor riesgo con spread positivo
        """
        opciones = self.filtrar_por_perfil()
        
        if not opciones:
            return {"error": "No hay opciones disponibles para tu perfil"}
        
        if criterio == "spread":
            return opciones[0]  # Ya ordenadas por spread
        
        elif criterio == "rentabilidad":
            return max(
                opciones,
                key=lambda x: float(x["numeros"]["rentabilidad_esperada"].replace("%", ""))
            )
        
        elif criterio == "seguridad":
            # Solo opciones rentables con bajo riesgo
            seguras = [
                op for op in opciones
                if op["conclusion"]["es_rentable"] and 
                op["opcion"]["riesgo"] in ["Muy Bajo", "Bajo"]
            ]
            return seguras[0] if seguras else opciones[0]
        
        return opciones[0]
    
    def resumen_estrategia(self) -> dict:
        """Genera resumen de la estrategia de inversión"""
        mejor = self.mejor_opcion("spread")
        opciones_rentables = [
            op for op in self.analizar_todas_opciones()
            if op["conclusion"]["es_rentable"]
        ]
        
        return {
            "capital_prestamo": self.capital,
            "coste_prestamo": f"{self.coste*100:.2f}%",
            "perfil_riesgo": self.perfil,
            "opciones_rentables": len(opciones_rentables),
            "mejor_opcion": {
                "nombre": mejor["opcion"]["nombre"],
                "spread": mejor["numeros"]["spread"],
                "beneficio_anual": mejor["numeros"]["beneficio_neto_anual"],
                "riesgo": mejor["opcion"]["riesgo"]
            },
            "estrategia_recomendada": self._generar_recomendacion(mejor)
        }
    
    def _generar_recomendacion(self, mejor_opcion: dict) -> str:
        """Genera texto de recomendación"""
        spread_val = float(mejor_opcion["numeros"]["spread"].replace("%", ""))
        
        if spread_val > 1.0:
            return (
                f"RECOMENDACIÓN: Invertir en {mejor_opcion['opcion']['nombre']}. "
                f"Con un spread de {mejor_opcion['numeros']['spread']}, obtienes "
                f"{mejor_opcion['numeros']['beneficio_neto_anual']:,.0f}€ anuales "
                f"después de pagar el préstamo."
            )
        elif spread_val > 0:
            return (
                f"VIABLE CON PRUDENCIA: {mejor_opcion['opcion']['nombre']} ofrece "
                f"un spread ajustado de {mejor_opcion['numeros']['spread']}. "
                f"El beneficio es modesto pero positivo."
            )
        else:
            return (
                f"NO RECOMENDADO: Con el coste actual del préstamo ({self.coste*100:.2f}%), "
                f"las opciones de inversión de bajo riesgo no cubren el coste. "
                f"Considera esperar a mejores condiciones o reducir el spread del préstamo."
            )


def analisis_escenarios(
    capital: float,
    escenarios_coste: list[float]
) -> list[dict]:
    """
    Analiza diferentes escenarios de coste del préstamo.
    
    Útil para ver qué pasa si sube/baja el Euribor.
    """
    resultados = []
    
    for coste in escenarios_coste:
        analizador = AnalizadorInversion(
            capital_prestamo=capital,
            coste_prestamo=coste
        )
        
        mejor = analizador.mejor_opcion("seguridad")
        
        resultados.append({
            "coste_prestamo": f"{coste*100:.2f}%",
            "mejor_opcion": mejor["opcion"]["nombre"],
            "spread": mejor["numeros"]["spread"],
            "beneficio_anual": mejor["numeros"]["beneficio_neto_anual"],
            "es_rentable": mejor["conclusion"]["es_rentable"]
        })
    
    return resultados


def calcular_rentabilidad_total_estrategia(
    capital_inicial: float,
    dividendo_activo: float,  # yield del activo inicial
    ltv: float,
    coste_prestamo: float,
    rentabilidad_inversion: float  # yield de la inversión con el préstamo
) -> dict:
    """
    Calcula la rentabilidad total de la estrategia completa.
    
    Estrategia:
    1. Comprar activo con capital_inicial -> recibir dividendos
    2. Pedir lombardo sobre activo -> obtener préstamo
    3. Invertir préstamo -> recibir rentabilidad
    
    Returns:
        Análisis completo de la rentabilidad total
    """
    # 1. Dividendos del activo inicial
    prestamo = capital_inicial * ltv
    dividendos_anuales = capital_inicial * dividendo_activo
    
    # 2. Coste del préstamo
    coste_anual_prestamo = prestamo * coste_prestamo
    
    # 3. Rentabilidad de la inversión del préstamo
    rentabilidad_anual_inversion = prestamo * rentabilidad_inversion
    
    # Totales
    ingresos_totales = dividendos_anuales + rentabilidad_anual_inversion
    gastos_totales = coste_anual_prestamo
    beneficio_neto = ingresos_totales - gastos_totales
    
    # Rentabilidad sobre capital propio
    roi = beneficio_neto / capital_inicial
    
    return {
        "capital_inicial": capital_inicial,
        "desglose": {
            "activo_inicial": {
                "valor": capital_inicial,
                "yield": f"{dividendo_activo*100:.2f}%",
                "dividendos_anuales": dividendos_anuales
            },
            "prestamo_lombardo": {
                "ltv": f"{ltv*100:.0f}%",
                "importe": prestamo,
                "coste": f"{coste_prestamo*100:.2f}%",
                "coste_anual": coste_anual_prestamo
            },
            "inversion_prestamo": {
                "importe": prestamo,
                "rentabilidad": f"{rentabilidad_inversion*100:.2f}%",
                "rentabilidad_anual": rentabilidad_anual_inversion
            }
        },
        "resultado": {
            "ingresos_totales": ingresos_totales,
            "gastos_totales": gastos_totales,
            "beneficio_neto_anual": beneficio_neto,
            "beneficio_neto_mensual": beneficio_neto / 12,
            "roi_sobre_capital": f"{roi*100:.2f}%"
        },
        "analisis": {
            "es_rentable": beneficio_neto > 0,
            "rentabilidad_sin_apalancamiento": f"{dividendo_activo*100:.2f}%",
            "rentabilidad_con_apalancamiento": f"{roi*100:.2f}%",
            "mejora_por_apalancamiento": f"{(roi - dividendo_activo)*100:.2f}%",
            "apalancamiento_efectivo": 1 + ltv
        }
    }

