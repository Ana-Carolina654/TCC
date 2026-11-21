"""
fuzzy_security.py

Sistema de decisão fuzzy para avaliação adaptativa do nível de segurança.

O módulo recebe informações provenientes das etapas anteriores da arquitetura:

    threat_detection.py
        ↓
    fuzzy_security.py
        ↓
    crypto_manager.py

O objetivo é transformar as condições observadas no dispositivo, na operação
e na comunicação em um índice contínuo de segurança entre 0 e 10.

O módulo NÃO escolhe diretamente o algoritmo criptográfico.
Essa responsabilidade será do crypto_manager.py.
"""


import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from functools import lru_cache


# ============================================================
# CONFIGURAÇÃO
# ============================================================

SECURITY_MIN = 0.0
SECURITY_MAX = 10.0


# ============================================================
# SISTEMA FUZZY
# ============================================================

@lru_cache(maxsize=1)
def criar_sistema_fuzzy():
    """
    Cria o sistema de inferência fuzzy responsável pela avaliação
    do nível de segurança.

    O sistema é criado uma única vez e reutilizado nas avaliações
    seguintes, evitando reconstrução desnecessária das regras.

    Entradas:
        - ameaça
        - condição operacional
        - comunicação

    Saída:
        - nível de segurança
    """

    # --------------------------------------------------------
    # VARIÁVEIS DE ENTRADA
    # --------------------------------------------------------

    ameaca = ctrl.Antecedent(
        np.arange(0, 11, 1),
        "ameaca"
    )

    operacional = ctrl.Antecedent(
        np.arange(0, 11, 1),
        "operacional"
    )

    comunicacao = ctrl.Antecedent(
        np.arange(0, 11, 1),
        "comunicacao"
    )

    # --------------------------------------------------------
    # VARIÁVEL DE SAÍDA
    # --------------------------------------------------------

    seguranca = ctrl.Consequent(
        np.arange(0, 10.1, 0.1),
        "seguranca"
    )

    # ========================================================
    # FUNÇÕES DE PERTINÊNCIA
    # ========================================================

    # --------------------------------------------------------
    # AMEAÇA
    # --------------------------------------------------------

    ameaca["normal"] = fuzz.trimf(
        ameaca.universe,
        [0, 0, 2]
    )

    ameaca["atencao"] = fuzz.trimf(
        ameaca.universe,
        [1, 3, 5]
    )

    ameaca["alto"] = fuzz.trimf(
        ameaca.universe,
        [4, 6, 8]
    )

    ameaca["critico"] = fuzz.trapmf(
        ameaca.universe,
        [7, 8, 10, 10]
    )

    # --------------------------------------------------------
    # CONDIÇÃO OPERACIONAL
    # --------------------------------------------------------

    operacional["normal"] = fuzz.trimf(
        operacional.universe,
        [0, 0, 3]
    )

    operacional["atencao"] = fuzz.trimf(
        operacional.universe,
        [2, 4, 6]
    )

    operacional["degradado"] = fuzz.trimf(
        operacional.universe,
        [5, 7, 9]
    )

    operacional["critico"] = fuzz.trapmf(
        operacional.universe,
        [8, 9, 10, 10]
    )

    # --------------------------------------------------------
    # COMUNICAÇÃO
    # --------------------------------------------------------

    comunicacao["normal"] = fuzz.trimf(
        comunicacao.universe,
        [0, 0, 3]
    )

    comunicacao["atencao"] = fuzz.trimf(
        comunicacao.universe,
        [2, 4, 6]
    )

    comunicacao["degradado"] = fuzz.trimf(
        comunicacao.universe,
        [5, 7, 9]
    )

    comunicacao["critico"] = fuzz.trapmf(
        comunicacao.universe,
        [8, 9, 10, 10]
    )

    # --------------------------------------------------------
    # NÍVEL DE SEGURANÇA
    # --------------------------------------------------------

    seguranca["baixo"] = fuzz.trimf(
        seguranca.universe,
        [0, 0, 3]
    )

    seguranca["moderado"] = fuzz.trimf(
        seguranca.universe,
        [2, 4, 6]
    )

    seguranca["alto"] = fuzz.trimf(
        seguranca.universe,
        [5, 7, 9]
    )

    seguranca["muito_alto"] = fuzz.trapmf(
        seguranca.universe,
        [8, 9, 10, 10]
    )

    # ========================================================
    # REGRAS FUZZY
    # ========================================================

    regras = [

        # ----------------------------------------------------
        # OPERAÇÃO NORMAL
        # ----------------------------------------------------

        ctrl.Rule(
            ameaca["normal"]
            & operacional["normal"]
            & comunicacao["normal"],
            seguranca["baixo"]
        ),

        # ----------------------------------------------------
        # AMEAÇA EM ATENÇÃO
        # ----------------------------------------------------

        ctrl.Rule(
            ameaca["atencao"]
            & operacional["normal"]
            & comunicacao["normal"],
            seguranca["moderado"]
        ),

        # ----------------------------------------------------
        # COMBINAÇÕES INTERMEDIÁRIAS
        # ----------------------------------------------------

        ctrl.Rule(
            ameaca["atencao"]
            & operacional["atencao"]
            & comunicacao["normal"],
            seguranca["moderado"]
        ),

        ctrl.Rule(
            ameaca["atencao"]
            & operacional["normal"]
            & comunicacao["atencao"],
            seguranca["moderado"]
        ),

        ctrl.Rule(
            ameaca["atencao"]
            & operacional["atencao"]
            & comunicacao["atencao"],
            seguranca["alto"]
        ),

        ctrl.Rule(
            ameaca["alto"]
            & operacional["normal"]
            & comunicacao["normal"],
            seguranca["alto"]
        ),

        ctrl.Rule(
            ameaca["alto"]
            & (
                operacional["degradado"]
                | comunicacao["degradado"]
            ),
            seguranca["muito_alto"]
        ),

        # ----------------------------------------------------
        # CONDIÇÕES OPERACIONAIS DESFAVORÁVEIS
        # ----------------------------------------------------

        ctrl.Rule(
            operacional["atencao"]
            & ameaca["normal"],
            seguranca["moderado"]
        ),

        ctrl.Rule(
            operacional["degradado"]
            & ameaca["normal"],
            seguranca["alto"]
        ),

        ctrl.Rule(
            operacional["critico"],
            seguranca["muito_alto"]
        ),

        # ----------------------------------------------------
        # COMUNICAÇÃO DESFAVORÁVEL
        # ----------------------------------------------------

        ctrl.Rule(
            comunicacao["atencao"]
            & ameaca["normal"],
            seguranca["moderado"]
        ),

        ctrl.Rule(
            comunicacao["degradado"]
            & ameaca["normal"],
            seguranca["alto"]
        ),

        ctrl.Rule(
            comunicacao["critico"],
            seguranca["muito_alto"]
        ),

        # ----------------------------------------------------
        # AMEAÇA ALTA
        # ----------------------------------------------------

        ctrl.Rule(
            ameaca["alto"],
            seguranca["alto"]
        ),

        # ----------------------------------------------------
        # AMEAÇA CRÍTICA
        # ----------------------------------------------------

        ctrl.Rule(
            ameaca["critico"],
            seguranca["muito_alto"]
        ),

        # ----------------------------------------------------
        # COMBINAÇÃO DE EVIDÊNCIAS
        # ----------------------------------------------------

        ctrl.Rule(
            ameaca["atencao"]
            & (
                operacional["degradado"]
                | comunicacao["degradado"]
            ),
            seguranca["alto"]
        ),

        ctrl.Rule(
            ameaca["alto"]
            & (
                operacional["atencao"]
                | comunicacao["atencao"]
            ),
            seguranca["muito_alto"]
        ),

        ctrl.Rule(
            ameaca["atencao"]
            & operacional["critico"],
            seguranca["muito_alto"]
        ),

        ctrl.Rule(
            ameaca["atencao"]
            & comunicacao["critico"],
            seguranca["muito_alto"]
        ),
    ]

    sistema = ctrl.ControlSystem(regras)

    return sistema


# ============================================================
# AVALIAÇÃO FUZZY
# ============================================================

def avaliar_seguranca(
    nivel_ameaca,
    nivel_operacional,
    nivel_comunicacao
):
    """
    Avalia o nível de segurança a partir das condições observadas.

    O sistema de regras é reutilizado, mas uma nova simulação
    de inferência é criada para cada avaliação.

    Retorno:
        (pontuação de segurança, classificação)
    """

    sistema = criar_sistema_fuzzy()

    simulador = ctrl.ControlSystemSimulation(sistema)

    # Limita os valores ao intervalo esperado.
    nivel_ameaca = np.clip(nivel_ameaca, 0, 10)
    nivel_operacional = np.clip(nivel_operacional, 0, 10)
    nivel_comunicacao = np.clip(nivel_comunicacao, 0, 10)

    simulador.input["ameaca"] = nivel_ameaca
    simulador.input["operacional"] = nivel_operacional
    simulador.input["comunicacao"] = nivel_comunicacao

    simulador.compute()

    pontuacao = float(simulador.output["seguranca"])

    classificacao = classificar_seguranca(pontuacao)

    return pontuacao, classificacao


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar_seguranca(pontuacao):
    """
    Classifica o índice de segurança produzido pelo sistema fuzzy.
    """

    if pontuacao < 3:
        return "BAIXO"

    if pontuacao < 5:
        return "MODERADO"

    if pontuacao < 7.5:
        return "ALTO"

    return "MUITO ALTO"


# ============================================================
# CONVERSÃO DAS CATEGORIAS
# ============================================================

def converter_ameaca(nivel):
    """
    Converte a classificação de ameaça para uma escala de 0 a 10.
    """

    valores = {
        "NORMAL": 0,
        "ATENÇÃO": 3,
        "ATENCAO": 3,
        "ALTO": 7,
        "CRÍTICO": 10,
        "CRITICO": 10
    }

    nivel = str(nivel).upper()

    if nivel not in valores:
        raise ValueError(
            f"Nível de ameaça inválido: {nivel}"
        )

    return valores[nivel]


def converter_condicao(nivel):
    """
    Converte uma classificação operacional ou de comunicação
    para a escala utilizada pelo sistema fuzzy.
    """

    valores = {
        "NORMAL": 0,
        "ATENÇÃO": 3,
        "ATENCAO": 3,
        "DEGRADADO": 7,
        "CRÍTICO": 10,
        "CRITICO": 10
    }

    nivel = str(nivel).upper()

    if nivel not in valores:
        raise ValueError(
            f"Condição inválida: {nivel}"
        )

    return valores[nivel]


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def calcular_nivel_seguranca(
    nivel_ameaca,
    nivel_operacional,
    nivel_comunicacao
):
    """
    Interface principal do módulo.

    Recebe as classificações produzidas pelos módulos anteriores
    e retorna a decisão fuzzy de segurança.
    """

    ameaca = converter_ameaca(nivel_ameaca)
    operacional = converter_condicao(nivel_operacional)
    comunicacao = converter_condicao(nivel_comunicacao)

    return avaliar_seguranca(
        ameaca,
        operacional,
        comunicacao
    )


# ============================================================
# TESTES
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TESTE DO SISTEMA FUZZY DE SEGURANÇA")
    print("=" * 60)

    casos = [
        (
            "CASO 1: Operação normal",
            "NORMAL",
            "NORMAL",
            "NORMAL"
        ),
        (
            "CASO 2: Atenção operacional",
            "ATENÇÃO",
            "ATENÇÃO",
            "NORMAL"
        ),
        (
            "CASO 3: Comunicação degradada",
            "ALTO",
            "NORMAL",
            "DEGRADADO"
        ),
        (
            "CASO 4: Cenário combinado",
            "CRÍTICO",
            "ATENÇÃO",
            "CRÍTICO"
        )
    ]

    for nome, ameaca, operacional, comunicacao in casos:

        print()
        print(nome)
        print("-" * 60)

        pontuacao, classificacao = calcular_nivel_seguranca(
            ameaca,
            operacional,
            comunicacao
        )

        print(f"Ameaça:                 {ameaca}")
        print(f"Condição operacional:   {operacional}")
        print(f"Comunicação:            {comunicacao}")
        print(f"Pontuação de segurança: {pontuacao:.2f}")
        print(f"Nível de segurança:     {classificacao}")
