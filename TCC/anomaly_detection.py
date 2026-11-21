"""
anomaly_detection.py

Módulo responsável pela identificação de anomalias
operacionais e de comunicação do dispositivo IoT.

O módulo identifica evidências de comportamento anormal,
mas não determina se o evento representa um ataque.
"""

from dataclasses import dataclass


# ============================================================
# ESTRUTURA DA ANOMALIA
# ============================================================

@dataclass
class AnomalyState:
    operational_anomalies: list
    communication_anomalies: list

    total_anomalies: int
    anomaly_level: str


# ============================================================
# DETECTOR DE ANOMALIAS
# ============================================================

class AnomalyDetector:

    # --------------------------------------------------------
    # Anomalias operacionais
    # --------------------------------------------------------

    @staticmethod
    def detect_operational_anomalies(operational_state):

        anomalies = []

        if operational_state.temperature_status != "NORMAL":
            anomalies.append(
                f"Temperatura {operational_state.temperature_status.lower()}"
            )

        if operational_state.rotation_status != "NORMAL":
            anomalies.append(
                f"Rotação {operational_state.rotation_status.lower()}"
            )

        if operational_state.torque_status != "NORMAL":
            anomalies.append(
                f"Torque {operational_state.torque_status.lower()}"
            )

        if operational_state.wear_status != "NORMAL":
            anomalies.append(
                f"Desgaste {operational_state.wear_status.lower()}"
            )

        if operational_state.load_status != "NORMAL":
            anomalies.append(
                f"Carga {operational_state.load_status.lower()}"
            )

        return anomalies

    # --------------------------------------------------------
    # Anomalias de comunicação
    # --------------------------------------------------------

    @staticmethod
    def detect_communication_anomalies(
        signal_status,
        interference_status
    ):

        anomalies = []

        if signal_status != "NORMAL":
            anomalies.append(
                f"Sinal de comunicação {signal_status.lower()}"
            )

        if interference_status != "NORMAL":
            anomalies.append(
                f"Interferência {interference_status.lower()}"
            )

        return anomalies

    # --------------------------------------------------------
    # Análise completa
    # --------------------------------------------------------

    def analyze(
        self,
        operational_state,
        signal_status,
        interference_status
    ):

        # Detecta anomalias operacionais
        operational_anomalies = (
            self.detect_operational_anomalies(
                operational_state
            )
        )

        # Detecta anomalias de comunicação
        communication_anomalies = (
            self.detect_communication_anomalies(
                signal_status,
                interference_status
            )
        )

        # Quantidade total de anomalias
        total_anomalies = (
            len(operational_anomalies)
            + len(communication_anomalies)
        )

        # ----------------------------------------------------
        # Classificação do nível geral
        #
        # O nível é determinado pela condição de maior
        # gravidade, e não pela quantidade de anomalias.
        # ----------------------------------------------------

        statuses = [
            operational_state.temperature_status,
            operational_state.rotation_status,
            operational_state.torque_status,
            operational_state.wear_status,
            operational_state.load_status,
            signal_status,
            interference_status
        ]

        priority = {
            "NORMAL": 0,
            "ATENÇÃO": 1,
            "DEGRADADO": 2,
            "CRÍTICO": 3
        }

        anomaly_level = max(
            statuses,
            key=lambda status: priority[status]
        )

        # Retorna o resultado da análise
        return AnomalyState(
            operational_anomalies=operational_anomalies,
            communication_anomalies=communication_anomalies,
            total_anomalies=total_anomalies,
            anomaly_level=anomaly_level
        )


# ============================================================
# TESTE DO MÓDULO
# ============================================================

if __name__ == "__main__":

    from operational import OperationalMonitor

    monitor = OperationalMonitor()
    detector = AnomalyDetector()

    print("=" * 60)
    print("TESTE DO DETECTOR DE ANOMALIAS")
    print("=" * 60)

    # --------------------------------------------------------
    # CASO 1: Operação normal
    # --------------------------------------------------------

    state = monitor.evaluate(
        temperature=40.0,
        rotation=3000.0,
        torque=100.0,
        wear=10.0,
        load=30.0
    )

    result = detector.analyze(
        operational_state=state,
        signal_status="NORMAL",
        interference_status="NORMAL"
    )

    print("\nCASO 1: Operação normal")
    print("-" * 60)

    print(f"Anomalias operacionais: {len(result.operational_anomalies)}")
    print(f"Anomalias comunicação:  {len(result.communication_anomalies)}")
    print(f"Total de anomalias:    {result.total_anomalies}")
    print(f"Nível de anomalia:     {result.anomaly_level}")

    # --------------------------------------------------------
    # CASO 2: Anomalia operacional
    # --------------------------------------------------------

    state = monitor.evaluate(
        temperature=65.0,
        rotation=2300.0,
        torque=200.0,
        wear=60.0,
        load=70.0
    )

    result = detector.analyze(
        operational_state=state,
        signal_status="NORMAL",
        interference_status="NORMAL"
    )

    print("\nCASO 2: Anomalia operacional")
    print("-" * 60)

    for anomaly in result.operational_anomalies:
        print(f"  - {anomaly}")

    print(f"Total de anomalias: {result.total_anomalies}")
    print(f"Nível de anomalia:  {result.anomaly_level}")

    # --------------------------------------------------------
    # CASO 3: Anomalia de comunicação
    # --------------------------------------------------------

    state = monitor.evaluate(
        temperature=40.0,
        rotation=3000.0,
        torque=100.0,
        wear=10.0,
        load=30.0
    )

    result = detector.analyze(
        operational_state=state,
        signal_status="DEGRADADO",
        interference_status="CRÍTICO"
    )

    print("\nCASO 3: Anomalia de comunicação")
    print("-" * 60)

    for anomaly in result.communication_anomalies:
        print(f"  - {anomaly}")

    print(f"Total de anomalias: {result.total_anomalies}")
    print(f"Nível de anomalia:  {result.anomaly_level}")

    # --------------------------------------------------------
    # CASO 4: Anomalias combinadas
    # --------------------------------------------------------

    state = monitor.evaluate(
        temperature=80.0,
        rotation=1800.0,
        torque=300.0,
        wear=80.0,
        load=85.0
    )

    result = detector.analyze(
        operational_state=state,
        signal_status="DEGRADADO",
        interference_status="CRÍTICO"
    )

    print("\nCASO 4: Anomalias combinadas")
    print("-" * 60)

    print("Anomalias operacionais:")

    for anomaly in result.operational_anomalies:
        print(f"  - {anomaly}")

    print("Anomalias de comunicação:")

    for anomaly in result.communication_anomalies:
        print(f"  - {anomaly}")

    print(f"\nTotal de anomalias: {result.total_anomalies}")
    print(f"Nível de anomalia:  {result.anomaly_level}")

    print("\n" + "=" * 60)
    print("TESTE FINALIZADO")
    print("=" * 60)

