import ast
import csv
from collections import Counter, defaultdict


# ============================================================
# CONFIGURAÇÃO
# ============================================================

ARQUIVO_CSV = "simulation_results.csv"


# ============================================================
# LEITURA E VALIDAÇÃO DOS DADOS
# ============================================================

def carregar_resultados(nome_arquivo=ARQUIVO_CSV):
    """
    Carrega os resultados da simulação a partir do CSV.

    Não executa a simulação e não modifica o arquivo original.
    """

    campos_obrigatorios = {
        "sample",
        "time_seconds",
        "scenario",
        "security_level",
        "crypto_policy",
    }

    with open(
        nome_arquivo,
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:

        leitor = csv.DictReader(arquivo)

        if leitor.fieldnames is None:
            raise ValueError("O CSV não possui cabeçalho.")

        campos_disponiveis = set(leitor.fieldnames)
        campos_faltantes = (
            campos_obrigatorios - campos_disponiveis
        )

        if campos_faltantes:
            raise ValueError(
                "Colunas obrigatórias ausentes no CSV: "
                + ", ".join(sorted(campos_faltantes))
            )

        resultados = []

        for linha in leitor:
            try:
                politica = ast.literal_eval(
                    linha["crypto_policy"]
                )

                if not isinstance(politica, dict):
                    raise ValueError(
                        "A política criptográfica não é um dicionário."
                    )

                algoritmo = politica["algorithm"]
                tamanho_chave = int(politica["key_size"])

                resultado = {
                    "sample": int(linha["sample"]),
                    "time_seconds": int(linha["time_seconds"]),
                    "scenario": linha["scenario"],
                    "security_level": linha["security_level"],
                    "algorithm": algoritmo,
                    "key_size": tamanho_chave,
                }

                resultados.append(resultado)

            except (ValueError, SyntaxError, KeyError) as erro:
                raise ValueError(
                    f"Erro ao processar a linha "
                    f"{leitor.line_num} do CSV: {erro}"
                ) from erro

    if not resultados:
        raise ValueError(
            "O CSV não contém amostras para analisar."
        )

    resultados.sort(key=lambda resultado: resultado["sample"])

    return resultados


# ============================================================
# CÁLCULO DAS MÉTRICAS
# ============================================================

def calcular_metricas(resultados):
    """
    Calcula indicadores descritivos dos resultados simulados.
    """

    total = len(resultados)

    contagem_seguranca = Counter(
        resultado["security_level"]
        for resultado in resultados
    )

    contagem_algoritmos = Counter(
        resultado["algorithm"]
        for resultado in resultados
    )

    contagem_cenarios = Counter(
        resultado["scenario"]
        for resultado in resultados
    )

    # Distribuição de algoritmos dentro de cada cenário.
    algoritmos_por_cenario = defaultdict(Counter)

    for resultado in resultados:
        algoritmos_por_cenario[
            resultado["scenario"]
        ][resultado["algorithm"]] += 1

    # Mudanças entre amostras consecutivas.
    mudancas_algoritmo = 0
    mudancas_nivel_seguranca = 0

    for anterior, atual in zip(
        resultados,
        resultados[1:],
    ):
        if anterior["algorithm"] != atual["algorithm"]:
            mudancas_algoritmo += 1

        if (
            anterior["security_level"]
            != atual["security_level"]
        ):
            mudancas_nivel_seguranca += 1

    tempo_inicial = resultados[0]["time_seconds"]
    tempo_final = resultados[-1]["time_seconds"]

    return {
        "total": total,
        "tempo_inicial": tempo_inicial,
        "tempo_final": tempo_final,
        "tempo_decorrido": tempo_final - tempo_inicial,
        "contagem_seguranca": contagem_seguranca,
        "contagem_algoritmos": contagem_algoritmos,
        "contagem_cenarios": contagem_cenarios,
        "algoritmos_por_cenario": algoritmos_por_cenario,
        "mudancas_algoritmo": mudancas_algoritmo,
        "mudancas_nivel_seguranca": mudancas_nivel_seguranca,
    }


# ============================================================
# APRESENTAÇÃO DO RELATÓRIO
# ============================================================

def imprimir_distribuicao(titulo, contagem, total):
    print(f"\n{titulo}")
    print("-" * 68)

    for nome, quantidade in contagem.most_common():
        percentual = quantidade / total * 100

        print(
            f"{nome:<30} "
            f"{quantidade:4d} amostras "
            f"({percentual:5.1f}%)"
        )


def imprimir_relatorio(metricas):
    """
    Exibe as métricas calculadas.
    """

    total = metricas["total"]

    print("=" * 68)
    print("RELATÓRIO DE MÉTRICAS DA SEGURANÇA ADAPTATIVA")
    print("=" * 68)

    print(f"Total de amostras analisadas: {total}")
    print(
        "Tempo inicial registrado: "
        f"{metricas['tempo_inicial']} segundos"
    )
    print(
        "Tempo final registrado:   "
        f"{metricas['tempo_final']} segundos"
    )
    print(
        "Tempo decorrido:           "
        f"{metricas['tempo_decorrido']} segundos"
    )

    imprimir_distribuicao(
        "DISTRIBUIÇÃO DOS NÍVEIS DE SEGURANÇA",
        metricas["contagem_seguranca"],
        total,
    )

    imprimir_distribuicao(
        "DISTRIBUIÇÃO DOS ALGORITMOS CRIPTOGRÁFICOS",
        metricas["contagem_algoritmos"],
        total,
    )

    imprimir_distribuicao(
        "DISTRIBUIÇÃO DOS CENÁRIOS",
        metricas["contagem_cenarios"],
        total,
    )

    print("\nMUDANÇAS ENTRE AMOSTRAS CONSECUTIVAS")
    print("-" * 68)
    print(
        "Mudanças de algoritmo criptográfico: "
        f"{metricas['mudancas_algoritmo']}"
    )
    print(
        "Mudanças de nível fuzzy:             "
        f"{metricas['mudancas_nivel_seguranca']}"
    )

    print("\nALGORITMOS POR CENÁRIO")
    print("-" * 68)

    for cenario, contagem in (
        metricas["algoritmos_por_cenario"].items()
    ):
        print(f"\n{cenario}:")

        for algoritmo, quantidade in contagem.most_common():
            print(f"  {algoritmo}: {quantidade} amostras")

    print("\n" + "=" * 68)
    print("Análise concluída.")
    print("=" * 68)


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def executar_analise(nome_arquivo=ARQUIVO_CSV):
    resultados = carregar_resultados(nome_arquivo)
    metricas = calcular_metricas(resultados)
    imprimir_relatorio(metricas)

    return metricas


if __name__ == "__main__":
    try:
        executar_analise()

    except (OSError, ValueError) as erro:
        print(f"\nERRO NA ANÁLISE: {erro}")