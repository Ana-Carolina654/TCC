# device_state.py

from dataclasses import dataclass
from enum import Enum

import config
from sensors import SensorData


# ============================================================
# ESTADOS DO DISPOSITIVO
# ============================================================

class DeviceStatus(Enum):
    """
    Estados possíveis do dispositivo.
    """

    NORMAL = "NORMAL"
    ATTENTION = "ATENÇÃO"
    DEGRADED = "DEGRADADO"
    CRITICAL = "CRÍTICO"


# ============================================================
# ESTRUTURA DO ESTADO DO DISPOSITIVO
# ============================================================

@dataclass
class DeviceState:
    """
    Representa o estado atual do dispositivo.
    """

    status: DeviceStatus

    battery_status: str
    temperature_status: str
    load_status: str


# ============================================================
# ANALISADOR DO ESTADO DO DISPOSITIVO
# ============================================================

class DeviceStateAnalyzer:
    """
    Analisa as condições internas do dispositivo.

    Este módulo não detecta ameaças cibernéticas.
    Ele apenas determina o estado do dispositivo.
    """

    # --------------------------------------------------------
    # ANÁLISE DA BATERIA
    # --------------------------------------------------------

    def analyze_battery(self, battery: float) -> str:

        if battery >= config.BATTERY_NORMAL_MIN:
            return "NORMAL"

        elif battery >= config.BATTERY_ATTENTION_MIN:
            return "ATENÇÃO"

        elif battery >= config.BATTERY_LOW_MIN:
            return "BAIXA"

        else:
            return "CRÍTICA"

    # --------------------------------------------------------
    # ANÁLISE DA TEMPERATURA
    # --------------------------------------------------------

    def analyze_temperature(self, temperature: float) -> str:

        if temperature < config.TEMPERATURE_NORMAL_MAX:
            return "NORMAL"

        elif temperature < config.TEMPERATURE_ATTENTION_MAX:
            return "ATENÇÃO"

        elif temperature < config.TEMPERATURE_HIGH_MAX:
            return "ALTA"

        else:
            return "CRÍTICA"

    # --------------------------------------------------------
    # ANÁLISE DA CARGA
    # --------------------------------------------------------

    def analyze_load(self, load: float) -> str:

        if load < config.LOAD_NORMAL_MAX:
            return "NORMAL"

        elif load < config.LOAD_ATTENTION_MAX:
            return "ATENÇÃO"

        elif load < config.LOAD_HIGH_MAX:
            return "ALTA"

        else:
            return "CRÍTICA"

    # --------------------------------------------------------
    # ANÁLISE GERAL
    # --------------------------------------------------------

    def analyze(self, sensor_data: SensorData) -> DeviceState:

        battery_status = self.analyze_battery(
            sensor_data.battery
        )

        temperature_status = self.analyze_temperature(
            sensor_data.temperature
        )

        load_status = self.analyze_load(
            sensor_data.load
        )

        # ----------------------------------------------------
        # CONDIÇÕES CRÍTICAS
        # ----------------------------------------------------

        critical_conditions = [
            battery_status == "CRÍTICA",
            temperature_status == "CRÍTICA",
            load_status == "CRÍTICA"
        ]

        # ----------------------------------------------------
        # CONDIÇÕES DEGRADADAS
        # ----------------------------------------------------

        degraded_conditions = [
            battery_status == "BAIXA",
            temperature_status == "ALTA",
            load_status == "ALTA"
        ]

        # ----------------------------------------------------
        # CONDIÇÕES DE ATENÇÃO
        # ----------------------------------------------------

        attention_conditions = [
            battery_status == "ATENÇÃO",
            temperature_status == "ATENÇÃO",
            load_status == "ATENÇÃO"
        ]

        # ----------------------------------------------------
        # DETERMINAÇÃO DO ESTADO GERAL
        # ----------------------------------------------------

        if any(critical_conditions):

            overall_status = DeviceStatus.CRITICAL

        elif any(degraded_conditions):

            overall_status = DeviceStatus.DEGRADED

        elif any(attention_conditions):

            overall_status = DeviceStatus.ATTENTION

        else:

            overall_status = DeviceStatus.NORMAL

        # ----------------------------------------------------
        # RETORNO
        # ----------------------------------------------------

        return DeviceState(
            status=overall_status,
            battery_status=battery_status,
            temperature_status=temperature_status,
            load_status=load_status
        )