"""
Detecção de evidências de ameaça.

Este módulo analisa as anomalias identificadas nas camadas
operacional e de comunicação e estima um nível de ameaça.

Importante:
- Não detecta diretamente um ataque.
- Não define a criptografia.
- Não substitui a lógica fuzzy.
- Apenas transforma as anomalias observadas em evidências
  de ameaça para as próximas etapas do sistema.
"""

from dataclasses import dataclass


@dataclass
class ThreatState:
    """
    Representa o estado da avaliação de ameaça.
    """

    operational_evidence: int
    communication_evidence: int
    combined_evidence: bool
    threat_score: int
    threat_level: str


class ThreatDetector:
    """
    Avalia evidências de ameaça a partir das anomalias detectadas.
    """

    @staticmethod
    def _severity_from_anomaly(anomaly: str) -> int:
        """
        Converte a gravidade de uma anomalia em um valor numérico.

        NORMAL     = 0
        ATENÇÃO    = 1
        DEGRADADO  = 2
        CRÍTICO    = 3
        """

        text = anomaly.upper()

        if "CRÍTICO" in text:
            return 3

        if "DEGRADADO" in text:
            return 2

        if "ATENÇÃO" in text:
            return 1

        return 0

    def evaluate_operational_evidence(
        self,
        operational_anomalies: list[str]
    ) -> int:
        """
        Avalia a maior gravidade encontrada entre as
        anomalias operacionais.
        """

        if not operational_anomalies:
            return 0

        return max(
            self._severity_from_anomaly(anomaly)
            for anomaly in operational_anomalies
        )

    def evaluate_communication_evidence(
        self,
        communication_anomalies: list[str]
    ) -> int:
        """
        Avalia a maior gravidade encontrada entre as
        anomalias de comunicação.
        """

        if not communication_anomalies:
            return 0

        return max(
            self._severity_from_anomaly(anomaly)
            for anomaly in communication_anomalies
        )

    @staticmethod
    def classify_threat(threat_score: int) -> str:
        """
        Classifica a relevância das evidências observadas.

        0   = NORMAL
        1-2 = ATENÇÃO
        3   = ALTO
        4   = CRÍTICO
        """

        if threat_score == 0:
            return "NORMAL"

        if threat_score <= 2:
            return "ATENÇÃO"

        if threat_score == 3:
            return "ALTO"

        return "CRÍTICO"

    def analyze(
        self,
        operational_anomalies: list[str],
        communication_anomalies: list[str]
    ) -> ThreatState:
        """
        Analisa as evidências provenientes das duas camadas.

        A presença de anomalias nos dois domínios simultaneamente
        aumenta a relevância da evidência, pois indica uma possível
        relação entre comportamento operacional e comunicação.
        """

        operational_evidence = self.evaluate_operational_evidence(
            operational_anomalies
        )

        communication_evidence = self.evaluate_communication_evidence(
            communication_anomalies
        )

        combined_evidence = (
            operational_evidence > 0
            and communication_evidence > 0
        )

        # A maior evidência individual representa a base da pontuação.
        threat_score = max(
            operational_evidence,
            communication_evidence
        )

        # Evidências simultâneas nos dois domínios aumentam
        # a relevância da situação observada.
        if combined_evidence:
            threat_score += 1

        # Mantém a pontuação no intervalo definido pelo modelo.
        threat_score = min(threat_score, 4)

        threat_level = self.classify_threat(threat_score)

        return ThreatState(
            operational_evidence=operational_evidence,
            communication_evidence=communication_evidence,
            combined_evidence=combined_evidence,
            threat_score=threat_score,
            threat_level=threat_level
        )


# ============================================================
# TESTE DO DETECTOR DE AMEAÇAS
# ============================================================

if __name__ == "__main__":

    from operational import OperationalMonitor
    from anomaly_detection import AnomalyDetector

    print("=" * 60)
    print("TESTE DO DETECTOR DE AMEAÇAS")
    print("=" * 60)

    operational = OperationalMonitor()
    anomaly_detector = AnomalyDetector()
    threat_detector = ThreatDetector()

    # ========================================================
    # CASO 1 - Operação normal
    # ========================================================

    print("\nCASO 1: Operação normal")
    print("-" * 60)

    operational_state = operational.evaluate(
        temperature=40,
        rotation=3000,
        torque=100,
        wear=10,
        load=30
    )

    anomaly_state = anomaly_detector.analyze(
        operational_state=operational_state,
        signal_status="NORMAL",
        interference_status="NORMAL"
    )

    threat_state = threat_detector.analyze(
        operational_anomalies=anomaly_state.operational_anomalies,
        communication_anomalies=anomaly_state.communication_anomalies
    )

    print(
        f"Evidência operacional:    "
        f"{threat_state.operational_evidence}"
    )

    print(
        f"Evidência comunicação:    "
        f"{threat_state.communication_evidence}"
    )

    print(
        f"Evidência combinada:      "
        f"{threat_state.combined_evidence}"
    )

    print(f"Pontuação de ameaça:       {threat_state.threat_score}")
    print(f"Nível de ameaça:           {threat_state.threat_level}")

    # ========================================================
    # CASO 2 - Anomalia operacional isolada
    # ========================================================

    print("\nCASO 2: Anomalia operacional isolada")
    print("-" * 60)

    operational_state = operational.evaluate(
        temperature=65,
        rotation=2300,
        torque=200,
        wear=60,
        load=70
    )

    anomaly_state = anomaly_detector.analyze(
        operational_state=operational_state,
        signal_status="NORMAL",
        interference_status="NORMAL"
    )

    threat_state = threat_detector.analyze(
        operational_anomalies=anomaly_state.operational_anomalies,
        communication_anomalies=anomaly_state.communication_anomalies
    )

    print(
        f"Evidência operacional:    "
        f"{threat_state.operational_evidence}"
    )

    print(
        f"Evidência comunicação:    "
        f"{threat_state.communication_evidence}"
    )

    print(
        f"Evidência combinada:      "
        f"{threat_state.combined_evidence}"
    )

    print(f"Pontuação de ameaça:       {threat_state.threat_score}")
    print(f"Nível de ameaça:           {threat_state.threat_level}")

    # ========================================================
    # CASO 3 - Anomalia de comunicação isolada
    # ========================================================

    print("\nCASO 3: Anomalia de comunicação isolada")
    print("-" * 60)

    operational_state = operational.evaluate(
        temperature=40,
        rotation=3000,
        torque=100,
        wear=10,
        load=30
    )

    anomaly_state = anomaly_detector.analyze(
        operational_state=operational_state,
        signal_status="DEGRADADO",
        interference_status="CRÍTICO"
    )

    threat_state = threat_detector.analyze(
        operational_anomalies=anomaly_state.operational_anomalies,
        communication_anomalies=anomaly_state.communication_anomalies
    )

    print(
        f"Evidência operacional:    "
        f"{threat_state.operational_evidence}"
    )

    print(
        f"Evidência comunicação:    "
        f"{threat_state.communication_evidence}"
    )

    print(
        f"Evidência combinada:      "
        f"{threat_state.combined_evidence}"
    )

    print(f"Pontuação de ameaça:       {threat_state.threat_score}")
    print(f"Nível de ameaça:           {threat_state.threat_level}")

    # ========================================================
    # CASO 4 - Evidências operacionais e de comunicação
    # ========================================================

    print("\nCASO 4: Evidências operacionais e de comunicação")
    print("-" * 60)

    operational_state = operational.evaluate(
        temperature=80,
        rotation=1800,
        torque=300,
        wear=80,
        load=85
    )

    anomaly_state = anomaly_detector.analyze(
        operational_state=operational_state,
        signal_status="DEGRADADO",
        interference_status="CRÍTICO"
    )

    threat_state = threat_detector.analyze(
        operational_anomalies=anomaly_state.operational_anomalies,
        communication_anomalies=anomaly_state.communication_anomalies
    )

    print(
        f"Evidência operacional:    "
        f"{threat_state.operational_evidence}"
    )

    print(
        f"Evidência comunicação:    "
        f"{threat_state.communication_evidence}"
    )

    print(
        f"Evidência combinada:      "
        f"{threat_state.combined_evidence}"
    )

    print(f"Pontuação de ameaça:       {threat_state.threat_score}")
    print(f"Nível de ameaça:           {threat_state.threat_level}")

    print("\n" + "=" * 60)
    print("TESTE FINALIZADO")
    print("=" * 60)

