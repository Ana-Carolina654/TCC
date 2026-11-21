
"""
simulation.py

Integra os módulos do sistema adaptativo de segurança IoT.

Fluxo:
    Sensores
       ↓
    Estado do dispositivo
       ↓
    Comunicação e operação
       ↓
    Detecção de anomalias
       ↓
    Detecção de ameaças
       ↓
    Sistema fuzzy
       ↓
    Política criptográfica adaptativa

Os cenários modificam as condições observadas na simulação.
Os níveis de ameaça e segurança são calculados pelos módulos
responsáveis por essas decisões.
"""

import csv
from collections import Counter
from dataclasses import replace

from sensors import SensorSimulator
from device_state import DeviceStateAnalyzer
from communication import CommunicationMonitor
from operational import OperationalMonitor
from anomaly_detection import AnomalyDetector
from threat_detection import ThreatDetector
from fuzzy_security import calcular_nivel_seguranca
from crypto_manager import CryptoManager


# ============================================================
# CENÁRIOS DE SIMULAÇÃO
# ============================================================

SCENARIOS = {
    "NORMAL": {
        "description": "Operação normal",
        "changes": {},
    },

    "DEGRADACAO_OPERACIONAL": {
        "description": "Degradação das condições operacionais",
        "changes": {
            "temperature": 82.0,
            "rotation_speed": 1800.0,
            "torque": 280.0,
            "wear": 75.0,
            "load": 85.0,
        },
    },

    "DEGRADACAO_COMUNICACAO": {
        "description": "Degradação da comunicação Wi-Fi",
        "changes": {
            "signal_strength": -85.0,
            "interference": 75.0,
        },
    },

    "RECUPERACAO_COMUNICACAO": {
        "description": "Recuperação das condições de comunicação",
        "changes": {
            "signal_strength": -55.0,
            "interference": 10.0,
        },
    },

    "CENARIO_COMBINADO": {
        "description": "Anomalias operacionais e de comunicação",
        "changes": {
            "temperature": 95.0,
            "rotation_speed": 800.0,
            "torque": 420.0,
            "wear": 95.0,
            "load": 97.0,
            "signal_strength": -90.0,
            "interference": 85.0,
        },
    },
}


# ============================================================
# UTILITÁRIOS
# ============================================================

def obter_valor(objeto, *atributos):
    """
    Obtém o primeiro atributo disponível em um objeto.
    Também converte enums para seus valores.
    """

    for atributo in atributos:
        if hasattr(objeto, atributo):
            valor = getattr(objeto, atributo)

            if hasattr(valor, "value"):
                return valor.value

            return valor

    raise AttributeError(
        f"Nenhum dos atributos {atributos} existe em "
        f"{type(objeto).__name__}."
    )


def normalizar_status(valor):
    """
    Padroniza os nomes dos estados.
    """

    valor = str(valor).strip().upper()

    equivalencias = {
        "ATTENTION": "ATENÇÃO",
        "ATENCAO": "ATENÇÃO",
        "DEGRADED": "DEGRADADO",
        "CRITICAL": "CRÍTICO",
        "CRITICO": "CRÍTICO",
    }

    return equivalencias.get(valor, valor)


# ============================================================
# SIMULADOR INTEGRADO
# ============================================================

class SecuritySimulation:
    """
    Coordena a execução dos módulos do sistema.
    """

    def __init__(self):
        self.sensor_simulator = SensorSimulator()
        self.device_analyzer = DeviceStateAnalyzer()
        self.communication_monitor = CommunicationMonitor()
        self.operational_monitor = OperationalMonitor()
        self.anomaly_detector = AnomalyDetector()
        self.threat_detector = ThreatDetector()
        self.crypto_manager = CryptoManager()

        self.sample_number = 0

    # --------------------------------------------------------
    # GERAÇÃO DOS DADOS
    # --------------------------------------------------------

    def generate_sample(self, scenario="NORMAL"):
        """
        Gera uma leitura dos sensores e aplica as condições
        controladas do cenário escolhido.
        """

        if scenario not in SCENARIOS:
            raise ValueError(f"Cenário desconhecido: {scenario}")

        sensor_data = self.sensor_simulator.update()
        changes = SCENARIOS[scenario]["changes"]

        if changes:
            sensor_data = replace(sensor_data, **changes)

        return sensor_data

    # --------------------------------------------------------
    # EXECUÇÃO DE UMA AMOSTRA
    # --------------------------------------------------------

    def run_step(self, scenario="NORMAL"):
        """
        Executa as etapas de análise para uma amostra.
        """

        self.sample_number += 1

        # 1. Dados dos sensores
        sensor_data = self.generate_sample(scenario)

        # 2. Estado interno do dispositivo
        device_state = self.device_analyzer.analyze(sensor_data)

        # 3. Condições de comunicação
        communication_state = self.communication_monitor.evaluate(
            sensor_data.signal_strength,
            sensor_data.interference,
        )

        # 4. Condições operacionais
        operational_state = self.operational_monitor.evaluate(
            sensor_data.temperature,
            sensor_data.rotation_speed,
            sensor_data.torque,
            sensor_data.load,
            sensor_data.wear,
        )

        # 5. Identificação de anomalias
        signal_status = obter_valor(
            communication_state,
            "signal_status",
        )

        interference_status = obter_valor(
            communication_state,
            "interference_status",
        )

        anomaly_state = self.anomaly_detector.analyze(
            operational_state,
            signal_status,
            interference_status,
        )

        # 6. Inferência das evidências de ameaça
        threat_state = self.threat_detector.analyze(
            anomaly_state.operational_anomalies,
            anomaly_state.communication_anomalies,
        )

        threat_level = normalizar_status(
            obter_valor(
                threat_state,
                "threat_level",
                "level",
            )
        )

        # 7. Preparação das entradas fuzzy
        operational_level = normalizar_status(
            obter_valor(
                operational_state,
                "status",
                "operational_status",
            )
        )

        communication_level = normalizar_status(
            obter_valor(
                communication_state,
                "communication_status",
                "status",
            )
        )

        # 8. Avaliação fuzzy
        security_score, security_level = calcular_nivel_seguranca(
            threat_level,
            operational_level,
            communication_level,
        )

        # 9. Política criptográfica adaptativa
        self.crypto_manager.select_policy(security_level)
        crypto_policy = self.crypto_manager.get_current_policy()

        # 10. Consolidação dos resultados
        return {
            "sample": self.sample_number,
            "scenario": scenario,
            "description": SCENARIOS[scenario]["description"],
            "sensors": sensor_data,

            "device_status": normalizar_status(
                device_state.status.value
            ),

            "operational_status": operational_level,
            "communication_status": communication_level,

            "operational_anomalies": (
                anomaly_state.operational_anomalies
            ),
            "communication_anomalies": (
                anomaly_state.communication_anomalies
            ),
            "total_anomalies": anomaly_state.total_anomalies,

            "threat_score": obter_valor(
                threat_state,
                "threat_score",
                "score",
            ),
            "threat_level": threat_level,

            "security_score": security_score,
            "security_level": security_level,

            "crypto_policy": crypto_policy,
        }


# ============================================================
# EXPERIMENTO TEMPORAL
# ============================================================

def executar_simulacao():
    simulation = SecuritySimulation()

    # Cada amostra representa 10 segundos simulados.
    intervalo_segundos = 10

    # Início inclusivo e fim exclusivo.
    sequencia = [
        (1, 21, "NORMAL"),
        (21, 36, "DEGRADACAO_OPERACIONAL"),
        (36, 51, "DEGRADACAO_COMUNICACAO"),
        (51, 66, "RECUPERACAO_COMUNICACAO"),
        (66, 81, "CENARIO_COMBINADO"),
        (81, 101, "RECUPERACAO_COMUNICACAO"),
    ]

    resultados = []

    print("=" * 100)
    print("EXPERIMENTO TEMPORAL - SEGURANÇA ADAPTATIVA PARA IoT")
    print(
        "100 amostras | intervalo de 10 segundos | "
        "990 segundos entre a primeira e a última amostra"
    )
    print("=" * 100)

    estado_anterior = None
    politica_anterior = None

    for inicio, fim, nome_cenario in sequencia:
        print(
            f"\n>>> AMOSTRAS {inicio} a {fim - 1}: "
            f"{SCENARIOS[nome_cenario]['description']}"
        )

        for _ in range(inicio, fim):
            resultado = simulation.run_step(nome_cenario)
            resultados.append(resultado)

            tempo_simulado = (
                (resultado["sample"] - 1) * intervalo_segundos
            )

            politica = resultado["crypto_policy"]

            print(
                f"Amostra {resultado['sample']:03d} | "
                f"t={tempo_simulado:04d}s | "
                f"Operação={resultado['operational_status']:<10} | "
                f"Comunicação={resultado['communication_status']:<10} | "
                f"Ameaça={resultado['threat_level']:<10} | "
                f"Segurança={resultado['security_level']:<12} | "
                f"Anomalias={resultado['total_anomalies']} | "
                f"Política={politica}"
            )

            # Transições dos estados analisados
            estado_atual = (
                resultado["operational_status"],
                resultado["communication_status"],
                resultado["threat_level"],
                resultado["security_level"],
            )

            if (
                estado_anterior is not None
                and estado_atual != estado_anterior
            ):
                print(
                    "   [TRANSIÇÃO] "
                    f"Estado anterior={estado_anterior} -> "
                    f"Estado atual={estado_atual}"
                )

            # Mudanças de política criptográfica
            if (
                politica_anterior is not None
                and politica != politica_anterior
            ):
                print(
                    "   [MUDANÇA CRIPTOGRÁFICA] "
                    f"{politica_anterior} -> {politica}"
                )

            estado_anterior = estado_atual
            politica_anterior = politica

    # --------------------------------------------------------
    # EXPORTAÇÃO CSV
    # --------------------------------------------------------

    nome_arquivo = "simulation_results.csv"

    with open(
        nome_arquivo,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:

        campos = [
            "sample",
            "time_seconds",
            "scenario",
            "battery",
            "temperature",
            "load",
            "rotation_speed",
            "torque",
            "wear",
            "signal_strength",
            "interference",
            "device_status",
            "operational_status",
            "communication_status",
            "operational_anomalies",
            "communication_anomalies",
            "total_anomalies",
            "threat_score",
            "threat_level",
            "security_score",
            "security_level",
            "crypto_policy",
        ]

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
        )
        escritor.writeheader()

        for resultado in resultados:
            sensores = resultado["sensors"]

            escritor.writerow({
                "sample": resultado["sample"],
                "time_seconds": (
                    resultado["sample"] - 1
                ) * intervalo_segundos,
                "scenario": resultado["scenario"],
                "battery": sensores.battery,
                "temperature": sensores.temperature,
                "load": sensores.load,
                "rotation_speed": sensores.rotation_speed,
                "torque": sensores.torque,
                "wear": sensores.wear,
                "signal_strength": sensores.signal_strength,
                "interference": sensores.interference,
                "device_status": resultado["device_status"],
                "operational_status": resultado["operational_status"],
                "communication_status": resultado["communication_status"],
                "operational_anomalies": "; ".join(
                    map(str, resultado["operational_anomalies"])
                ),
                "communication_anomalies": "; ".join(
                    map(str, resultado["communication_anomalies"])
                ),
                "total_anomalies": resultado["total_anomalies"],
                "threat_score": resultado["threat_score"],
                "threat_level": resultado["threat_level"],
                "security_score": resultado["security_score"],
                "security_level": resultado["security_level"],
                "crypto_policy": str(resultado["crypto_policy"]),
            })

    # --------------------------------------------------------
    # RESUMO ESTATÍSTICO
    # --------------------------------------------------------

    total_amostras = len(resultados)

    print("\n" + "=" * 100)
    print("RESUMO DO EXPERIMENTO")
    print("=" * 100)

    print(f"Total de amostras: {total_amostras}")

    tempo_decorrido = (
        (total_amostras - 1) * intervalo_segundos
        if total_amostras > 0
        else 0
    )

    print(
        f"Tempo decorrido entre a primeira e a última amostra: "
        f"{tempo_decorrido} segundos"
    )

    print("\nDistribuição dos níveis de segurança:")

    contagem_seguranca = Counter(
        resultado["security_level"]
        for resultado in resultados
    )

    for nivel, quantidade in contagem_seguranca.most_common():
        percentual = quantidade / total_amostras * 100
        print(
            f"  {nivel:<15}: {quantidade:3d} amostras "
            f"({percentual:5.1f}%)"
        )

    # Contagem por algoritmo, reunindo níveis fuzzy
    # que utilizam o mesmo algoritmo AES.
    print("\nDistribuição dos algoritmos criptográficos:")

    contagem_algoritmos = Counter(
        resultado["crypto_policy"]["algorithm"]
        for resultado in resultados
    )

    for algoritmo, quantidade in contagem_algoritmos.most_common():
        percentual = quantidade / total_amostras * 100
        print(
            f"  {algoritmo:<10}: {quantidade:3d} amostras "
            f"({percentual:5.1f}%)"
        )

    print("\nDistribuição dos cenários:")

    contagem_cenarios = Counter(
        resultado["scenario"]
        for resultado in resultados
    )

    for cenario, quantidade in contagem_cenarios.items():
        percentual = quantidade / total_amostras * 100
        print(
            f"  {cenario:<28}: {quantidade:3d} amostras "
            f"({percentual:5.1f}%)"
        )

    print(f"\nArquivo CSV salvo em: {nome_arquivo}")
    print("Experimento concluído.")
    print("=" * 100)


if __name__ == "__main__":
    executar_simulacao()

