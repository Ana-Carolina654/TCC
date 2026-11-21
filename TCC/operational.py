# operational.py

from dataclasses import dataclass
import config


# ============================================================
# ESTRUTURA DO ESTADO OPERACIONAL
# ============================================================

@dataclass
class OperationalState:
    temperature: float
    rotation: float
    torque: float
    wear: float
    load: float

    temperature_status: str
    rotation_status: str
    torque_status: str
    wear_status: str
    load_status: str

    operational_status: str


# ============================================================
# MONITOR OPERACIONAL
# ============================================================

class OperationalMonitor:

    # --------------------------------------------------------
    # Temperatura
    # --------------------------------------------------------

    @staticmethod
    def classify_temperature(temperature):

        if temperature < config.TEMPERATURE_NORMAL_MAX:
            return "NORMAL"

        elif temperature < config.TEMPERATURE_ATTENTION_MAX:
            return "ATENÇÃO"

        elif temperature < config.TEMPERATURE_DEGRADED_MAX:
            return "DEGRADADO"

        else:
            return "CRÍTICO"

    # --------------------------------------------------------
    # Carga
    # --------------------------------------------------------

    @staticmethod
    def classify_load(load):

        if load < config.LOAD_NORMAL_MAX:
            return "NORMAL"

        elif load < config.LOAD_ATTENTION_MAX:
            return "ATENÇÃO"

        elif load < config.LOAD_DEGRADED_MAX:
            return "DEGRADADO"

        else:
            return "CRÍTICO"

    # --------------------------------------------------------
    # Rotação
    # --------------------------------------------------------

    @staticmethod
    def classify_rotation(rotation):

        if (
            config.ROTATION_NORMAL_MIN
            <= rotation
            <= config.ROTATION_NORMAL_MAX
        ):
            return "NORMAL"

        elif (
            config.ROTATION_ATTENTION_MIN
            <= rotation
            <= config.ROTATION_ATTENTION_MAX
        ):
            return "ATENÇÃO"

        elif (
            config.ROTATION_DEGRADED_MIN
            <= rotation
            <= config.ROTATION_DEGRADED_MAX
        ):
            return "DEGRADADO"

        else:
            return "CRÍTICO"

    # --------------------------------------------------------
    # Torque
    # --------------------------------------------------------

    @staticmethod
    def classify_torque(torque):

        if torque <= config.TORQUE_NORMAL_MAX:
            return "NORMAL"

        elif torque <= config.TORQUE_ATTENTION_MAX:
            return "ATENÇÃO"

        elif torque <= config.TORQUE_DEGRADED_MAX:
            return "DEGRADADO"

        else:
            return "CRÍTICO"

    # --------------------------------------------------------
    # Desgaste
    # --------------------------------------------------------

    @staticmethod
    def classify_wear(wear):

        if wear < config.WEAR_NORMAL_MAX:
            return "NORMAL"

        elif wear < config.WEAR_ATTENTION_MAX:
            return "ATENÇÃO"

        elif wear < config.WEAR_DEGRADED_MAX:
            return "DEGRADADO"

        else:
            return "CRÍTICO"

    # --------------------------------------------------------
    # Estado operacional geral
    # --------------------------------------------------------

    @staticmethod
    def classify_operational(
        temperature_status,
        rotation_status,
        torque_status,
        wear_status,
        load_status
    ):

        priority = {
            "NORMAL": 0,
            "ATENÇÃO": 1,
            "DEGRADADO": 2,
            "CRÍTICO": 3
        }

        statuses = [
            temperature_status,
            rotation_status,
            torque_status,
            wear_status,
            load_status
        ]

        return max(statuses, key=lambda status: priority[status])

    # --------------------------------------------------------
    # Avaliação completa
    # --------------------------------------------------------

    def evaluate(
        self,
        temperature,
        rotation,
        torque,
        wear,
        load
    ):

        temperature_status = self.classify_temperature(temperature)
        rotation_status = self.classify_rotation(rotation)
        torque_status = self.classify_torque(torque)
        wear_status = self.classify_wear(wear)
        load_status = self.classify_load(load)

        operational_status = self.classify_operational(
            temperature_status,
            rotation_status,
            torque_status,
            wear_status,
            load_status
        )

        return OperationalState(
            temperature=temperature,
            rotation=rotation,
            torque=torque,
            wear=wear,
            load=load,

            temperature_status=temperature_status,
            rotation_status=rotation_status,
            torque_status=torque_status,
            wear_status=wear_status,
            load_status=load_status,

            operational_status=operational_status
        )


# ============================================================
# TESTE DO MÓDULO
# ============================================================

if __name__ == "__main__":

    monitor = OperationalMonitor()

    test_cases = [
        {
            "name": "Operação normal",
            "temperature": 40.0,
            "rotation": 3000.0,
            "torque": 100.0,
            "wear": 10.0,
            "load": 30.0
        },

        {
            "name": "Atenção",
            "temperature": 65.0,
            "rotation": 2300.0,
            "torque": 200.0,
            "wear": 60.0,
            "load": 70.0
        },

        {
            "name": "Degradado",
            "temperature": 80.0,
            "rotation": 1800.0,
            "torque": 300.0,
            "wear": 80.0,
            "load": 85.0
        },

        {
            "name": "Crítico",
            "temperature": 95.0,
            "rotation": 600.0,
            "torque": 450.0,
            "wear": 95.0,
            "load": 98.0
        },

        {
            "name": "Problema isolado de comunicação não afeta operação",
            "temperature": 40.0,
            "rotation": 3000.0,
            "torque": 100.0,
            "wear": 10.0,
            "load": 30.0
        }
    ]

    print("=" * 60)
    print("TESTE DO MONITOR OPERACIONAL")
    print("=" * 60)

    for i, case in enumerate(test_cases, start=1):

        state = monitor.evaluate(
            temperature=case["temperature"],
            rotation=case["rotation"],
            torque=case["torque"],
            wear=case["wear"],
            load=case["load"]
        )

        print(f"\nCASO {i}: {case['name']}")
        print("-" * 60)

        print(f"Temperatura: {state.temperature:.2f} °C")
        print(f"  Status:    {state.temperature_status}")

        print(f"Rotação:     {state.rotation:.2f} RPM")
        print(f"  Status:    {state.rotation_status}")

        print(f"Torque:      {state.torque:.2f} N.m")
        print(f"  Status:    {state.torque_status}")

        print(f"Desgaste:    {state.wear:.2f} %")
        print(f"  Status:    {state.wear_status}")

        print(f"Carga:       {state.load:.2f} %")
        print(f"  Status:    {state.load_status}")

        print(f"\nESTADO OPERACIONAL: {state.operational_status}")

    print("\n" + "=" * 60)
    print("TESTE FINALIZADO")
    print("=" * 60)