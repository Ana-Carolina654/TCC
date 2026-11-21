# communication.py

from dataclasses import dataclass

import config


@dataclass
class CommunicationState:
    """
    Representa o estado atual da comunicação do dispositivo.

    Este módulo avalia apenas as condições da comunicação.
    Não realiza detecção de ameaças ou ataques.
    """

    signal_strength: float
    interference: float

    signal_status: str
    interference_status: str
    communication_status: str


class CommunicationMonitor:
    """
    Monitora e classifica as condições da comunicação.

    Variáveis analisadas:
        signal_strength: intensidade do sinal Wi-Fi em dBm.
        interference: nível estimado de interferência em porcentagem.

    O resultado representa apenas a qualidade da comunicação.
    """

    
    def __init__(self):
        # Estado inicial do sinal ainda não avaliado.
        self.previous_signal_status = None


    def classify_signal(self, signal_strength: float) -> str:
        """
        Classifica o sinal Wi-Fi com histerese.

        CRÍTICO:
            Sinal abaixo do limite crítico.

        DEGRADADO:
            Sinal abaixo do limite de degradação,
            mas não crítico.

        NORMAL:
            Sinal recuperado acima do limite de recuperação.

        Na faixa entre os limites de degradação e recuperação,
        mantém o estado anterior para evitar oscilações.
        """

        if signal_strength < config.SIGNAL_STRENGTH_DEGRADED:
            self.previous_signal_status = "CRÍTICO"
            return "CRÍTICO"

        if signal_strength < config.SIGNAL_STRENGTH_DEGRADE_THRESHOLD:
            self.previous_signal_status = "DEGRADADO"
            return "DEGRADADO"

        if signal_strength >= config.SIGNAL_STRENGTH_RECOVERY_THRESHOLD:
            self.previous_signal_status = "NORMAL"
            return "NORMAL"

        # Entre os limites, mantém o estado anterior.
        if self.previous_signal_status is None:
            self.previous_signal_status = "NORMAL"

        return self.previous_signal_status


    def classify_interference(self, interference: float) -> str:
        """
        Classifica o nível de interferência.

        Retorna:
            NORMAL
            DEGRADADO
            CRÍTICO
        """

        if interference <= config.INTERFERENCE_NORMAL:
            return "NORMAL"

        elif interference <= config.INTERFERENCE_DEGRADED:
            return "DEGRADADO"

        return "CRÍTICO"

    def classify_communication(
        self,
        signal_status: str,
        interference_status: str
    ) -> str:
        """
        Determina o estado geral da comunicação a partir
        das condições do sinal e da interferência.

        A pior condição determina o estado geral.

        Exemplos:
            NORMAL + NORMAL       -> NORMAL
            NORMAL + DEGRADADO    -> DEGRADADO
            DEGRADADO + NORMAL    -> DEGRADADO
            DEGRADADO + CRÍTICO   -> CRÍTICO
            CRÍTICO + NORMAL      -> CRÍTICO
        """

        if (
            signal_status == "CRÍTICO"
            or interference_status == "CRÍTICO"
        ):
            return "CRÍTICO"

        if (
            signal_status == "DEGRADADO"
            or interference_status == "DEGRADADO"
        ):
            return "DEGRADADO"

        return "NORMAL"

    def evaluate(
        self,
        signal_strength: float,
        interference: float
    ) -> CommunicationState:
        """
        Avalia as condições atuais da comunicação.

        Parâmetros:
            signal_strength: intensidade do sinal em dBm.
            interference: interferência em porcentagem.

        Retorna:
            CommunicationState
        """

        signal_status = self.classify_signal(signal_strength)

        interference_status = self.classify_interference(
            interference
        )

        communication_status = self.classify_communication(
            signal_status,
            interference_status
        )

        return CommunicationState(
            signal_strength=signal_strength,
            interference=interference,
            signal_status=signal_status,
            interference_status=interference_status,
            communication_status=communication_status
        )


# ============================================================
# TESTE DO MÓDULO
# ============================================================

#if __name__ == "__main__":

#    monitor = CommunicationMonitor()

    # Valores de teste
#    signal_strength = -52
#    interference = 12

#    state = monitor.evaluate(
#        signal_strength,
#        interference
#    )

#    print("=" * 60)
#    print("AVALIAÇÃO DA COMUNICAÇÃO")
#    print("=" * 60)

#    print(f"Signal strength: {state.signal_strength:.2f} dBm")
#    print(f"Interference:    {state.interference:.2f}%")

#    print()

#    print(f"Status do sinal:        {state.signal_status}")
#    print(f"Status da interferência: {state.interference_status}")

#    print()

#    print(
#        f"ESTADO DA COMUNICAÇÃO: {state.communication_status}"
#    )

#    print("=" * 60)

# ============================================================
# TESTES DO MÓDULO
# ============================================================

if __name__ == "__main__":

    monitor = CommunicationMonitor()

    testes = [
        {
            "nome": "COMUNICAÇÃO NORMAL",
            "signal_strength": -50,
            "interference": 10
        },
        {
            "nome": "COMUNICAÇÃO DEGRADADA",
            "signal_strength": -70,
            "interference": 30
        },
        {
            "nome": "COMUNICAÇÃO CRÍTICA",
            "signal_strength": -85,
            "interference": 75
        },
        {
            "nome": "SINAL RUIM + INTERFERÊNCIA NORMAL",
            "signal_strength": -85,
            "interference": 10
        },
        {
            "nome": "SINAL NORMAL + INTERFERÊNCIA ALTA",
            "signal_strength": -50,
            "interference": 75
        }
    ]

    for i, teste in enumerate(testes, start=1):

        state = monitor.evaluate(
            teste["signal_strength"],
            teste["interference"]
        )

        print()
        print("=" * 60)
        print(f"TESTE {i} - {teste['nome']}")
        print("=" * 60)

        print(
            f"Signal strength: {state.signal_strength:.2f} dBm"
        )

        print(
            f"Interference:    {state.interference:.2f}%"
        )

        print()

        print(
            f"Status do sinal:         {state.signal_status}"
        )

        print(
            f"Status da interferência: {state.interference_status}"
        )

        print()

        print(
            f"ESTADO DA COMUNICAÇÃO: {state.communication_status}"
        )

#    print()
#    print("=" * 60)
#    print("TESTES FINALIZADOS")
#    print("=" * 60)
    
    
if __name__ == "__main__":

    monitor = CommunicationMonitor()

    sinais = [
        -55,  # NORMAL
        -61,  # Continua NORMAL
        -62,  # Continua NORMAL
        -64,  # DEGRADADO
        -62,  # Continua DEGRADADO
        -60,  # Continua DEGRADADO
        -57,  # Recupera para NORMAL
        -85,  # CRÍTICO
        -70,  # Sai do crítico para DEGRADADO
        -57,  # Recupera para NORMAL
    ]

    print("=" * 60)
    print("TESTE DE HISTERESE DO SINAL WI-FI")
    print("=" * 60)

    for sinal in sinais:
        estado = monitor.classify_signal(sinal)
        print(f"Sinal: {sinal:6.1f} dBm -> {estado}")

    print("=" * 60)
    print("TESTE FINALIZADO")
    print("=" * 60)
