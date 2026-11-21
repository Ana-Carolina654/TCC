
import ast
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURACAO
# ============================================================

st.set_page_config(
    page_title="Seguranca Adaptativa IoT",
    page_icon="🔐",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "simulation_results.csv"
COMPARISON_CSV_PATH = BASE_DIR / "crypto_comparison_results.csv"


# ============================================================
# FUNCOES AUXILIARES
# ============================================================

def numero_seguro(valor, casas=1, sufixo=""):
    """Formata valores numericos sem falhar diante de NaN."""
    if pd.isna(valor):
        return "N/D"

    try:
        return f"{float(valor):.{casas}f}{sufixo}"
    except (ValueError, TypeError):
        return "N/D"


def inteiro_seguro(valor):
    """Converte valores numericos em texto inteiro com seguranca."""
    if pd.isna(valor):
        return "N/D"

    try:
        return str(int(float(valor)))
    except (ValueError, TypeError, OverflowError):
        return "N/D"


def texto_seguro(valor):
    """Evita exibir NaN como texto."""
    if pd.isna(valor):
        return "N/D"
    return str(valor)


def interpretar_politica(valor):
    """Interpreta o dicionario criptografico armazenado no CSV."""
    try:
        resultado = ast.literal_eval(str(valor))
        return resultado if isinstance(resultado, dict) else {}
    except (ValueError, SyntaxError, TypeError):
        return {}


# ============================================================
# LEITURA DOS DADOS
# ============================================================

@st.cache_data
def carregar_dados(caminho, modificacao):
    df = pd.read_csv(caminho)

    colunas_obrigatorias = [
        "sample",
        "time_seconds",
        "scenario",
        "temperature",
        "load",
        "rotation_speed",
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

    faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            "Colunas ausentes no CSV: " + ", ".join(faltantes)
        )

    df["crypto_policy_dict"] = df["crypto_policy"].apply(
        interpretar_politica
    )

    df["crypto_algorithm"] = df["crypto_policy_dict"].apply(
        lambda politica: politica.get(
            "algorithm", "Nao informado"
        )
    )

    # Converte os campos numericos, exceto as listas de anomalias.
    colunas_numericas = [
        "sample",
        "time_seconds",
        "battery",
        "temperature",
        "load",
        "rotation_speed",
        "torque",
        "wear",
        "signal_strength",
        "interference",
        "total_anomalies",
        "threat_score",
        "security_score",
    ]

    for coluna in colunas_numericas:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="coerce"
            )

    # Conta as anomalias sem perder os textos originais.
    for coluna in [
        "operational_anomalies",
        "communication_anomalies"
    ]:
        df[coluna] = (
            df[coluna]
            .fillna("")
            .astype(str)
            .str.strip()
            .apply(
                lambda valor: 0
                if not valor
                else len(valor.split(";"))
            )
        )

    return df


# ============================================================
# CABECALHO
# ============================================================

st.title("🔐 Segurança Adaptativa para Dispositivos IoT")

st.caption(
    "Protótipo acadêmico de monitoramento industrial simulado "
    "com lógica fuzzy e seleção adaptativa de política criptográfica."
)


# ============================================================
# VERIFICACAO DO ARQUIVO
# ============================================================

if not CSV_PATH.exists():
    st.warning(
        "O arquivo simulation_results.csv não foi encontrado. "
        "Execute primeiro python main.py no CMD para gerar os dados."
    )
    st.stop()

try:
    df = carregar_dados(
        str(CSV_PATH),
        CSV_PATH.stat().st_mtime
    )
except Exception as erro:
    st.error(f"Não foi possível carregar os resultados: {erro}")
    st.stop()

if df.empty:
    st.warning("O CSV não contém amostras para exibir.")
    st.stop()


# ============================================================
# BARRA LATERAL E FILTROS
# ============================================================

st.sidebar.header("Controles")

if st.sidebar.button("Recarregar resultados"):
    carregar_dados.clear()
    st.rerun()

cenarios = ["Todos"] + sorted(
    df["scenario"].dropna().astype(str).unique().tolist()
)

cenario_selecionado = st.sidebar.selectbox(
    "Filtrar cenário",
    cenarios
)

if cenario_selecionado == "Todos":
    dados = df.copy()
else:
    dados = df[
        df["scenario"].astype(str) == cenario_selecionado
    ].copy()

if dados.empty:
    st.warning("Não há amostras para o filtro selecionado.")
    st.stop()


# ============================================================
# VISAO GERAL
# ============================================================

st.header("Visão geral")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Amostras", len(dados))
col2.metric("Cenários", dados["scenario"].nunique())
col3.metric("Níveis de segurança", dados["security_level"].nunique())
col4.metric("Algoritmos utilizados", dados["crypto_algorithm"].nunique())

st.divider()


# ============================================================
# GRAFICOS DE DISTRIBUICAO
# ============================================================

col_esquerda, col_direita = st.columns(2)

with col_esquerda:
    st.subheader("Níveis fuzzy de segurança")

    distribuicao = (
        dados["security_level"]
        .fillna("N/D")
        .value_counts()
        .rename_axis("Nível")
        .to_frame("Amostras")
    )

    st.bar_chart(distribuicao)

with col_direita:
    st.subheader("Políticas criptográficas")

    distribuicao_crypto = (
        dados["crypto_algorithm"]
        .fillna("N/D")
        .value_counts()
        .rename_axis("Algoritmo")
        .to_frame("Amostras")
    )

    st.bar_chart(distribuicao_crypto)


# ============================================================
# EVOLUCAO DA SEGURANCA
# ============================================================

st.subheader("Evolução da pontuação de segurança")

grafico = dados.sort_values("time_seconds").copy()

grafico["security_score"] = pd.to_numeric(
    grafico["security_score"],
    errors="coerce"
)

grafico_temporal = grafico.dropna(
    subset=["time_seconds", "security_score"]
)

if not grafico_temporal.empty:
    st.line_chart(
        grafico_temporal.set_index("time_seconds")[
            ["security_score"]
        ]
    )
else:
    st.info("Não há pontuações válidas para exibir o gráfico.")

st.caption(
    "A linha representa a pontuação fuzzy de segurança "
    "ao longo do tempo simulado."
)

st.divider()


# ============================================================
# EXPLORACAO DE UMA AMOSTRA
# ============================================================

st.header("Explorar uma amostra")

indices = dados.index.tolist()

indice_selecionado = st.select_slider(
    "Selecione uma amostra do experimento",
    options=indices,
    format_func=lambda indice: (
        f"Amostra {inteiro_seguro(dados.loc[indice, 'sample'])} "
        f"— {texto_seguro(dados.loc[indice, 'scenario'])}"
    )
)

amostra = dados.loc[indice_selecionado]


# ============================================================
# INDICADORES DE SEGURANCA
# ============================================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Nível de segurança",
    texto_seguro(amostra["security_level"])
)

col2.metric(
    "Pontuação fuzzy",
    numero_seguro(amostra["security_score"], casas=2)
)

col3.metric(
    "Nível de ameaça estimado",
    texto_seguro(amostra["threat_level"])
)


# ============================================================
# ESTADO DO DISPOSITIVO - INDICADORES AGRUPADOS
# ============================================================

st.subheader("Condições operacionais")

col1, col2, col3 = st.columns(3)
col1.metric("Temperatura", numero_seguro(amostra["temperature"], 1, " °C"))
col2.metric("Carga operacional", numero_seguro(amostra["load"], 1, "%"))
col3.metric("Rotação", numero_seguro(amostra["rotation_speed"], 0, " RPM"))

col1, col2, col3 = st.columns(3)
col1.metric("Torque", numero_seguro(amostra.get("torque"), 1, " N·m"))
col2.metric("Desgaste", numero_seguro(amostra.get("wear"), 1, "%"))
col3.metric("Anomalias operacionais", inteiro_seguro(amostra["operational_anomalies"]))

st.subheader("Condições de comunicação")

col1, col2, col3 = st.columns(3)
col1.metric("Sinal Wi-Fi", numero_seguro(amostra["signal_strength"], 1, " dBm"))
col2.metric("Interferência", numero_seguro(amostra["interference"], 1, "%"))
col3.metric("Anomalias de comunicação", inteiro_seguro(amostra["communication_anomalies"]))

st.write("**Cenário:**", texto_seguro(amostra["scenario"]))
st.write("**Estado do dispositivo:**", texto_seguro(amostra["device_status"]))
st.write("**Estado operacional:**", texto_seguro(amostra["operational_status"]))
st.write("**Estado da comunicação:**", texto_seguro(amostra["communication_status"]))

st.divider()


# ============================================================
# POLITICA CRIPTOGRAFICA
# ============================================================

st.header("Decisão criptográfica")

politica = amostra["crypto_policy_dict"]
algoritmo = politica.get("algorithm", "Não informado")
nivel = texto_seguro(amostra["security_level"])
pontuacao = numero_seguro(amostra["security_score"], 2)

col1, col2 = st.columns(2)

col1.metric("Nível de segurança fuzzy", nivel)
col2.metric("Pontuação fuzzy", pontuacao)

st.success(f"Política criptográfica selecionada: {algoritmo}")

st.caption(
    "A lógica fuzzy avalia as condições observadas e calcula "
    "o nível de segurança. O gerenciador criptográfico associa "
    "esse nível à política criptográfica correspondente."
)

with st.expander("Ver detalhes da política"):
    if politica:
        st.json(politica)
    else:
        st.info("Detalhes da política não disponíveis.")

st.divider()


# ============================================================
# MINI-RELATORIO EXPLICATIVO
# ============================================================

st.header("Mini-relatório da amostra")

anomalias_operacionais = inteiro_seguro(
    amostra["operational_anomalies"]
)
anomalias_comunicacao = inteiro_seguro(
    amostra["communication_anomalies"]
)

st.markdown(
    f"**Amostra:** {inteiro_seguro(amostra['sample'])}  \n"
    f"**Cenário:** {texto_seguro(amostra['scenario'])}"
)

st.markdown("#### 1. Condições observadas")

st.write(
    f"- Estado operacional: **{texto_seguro(amostra['operational_status'])}**\n"
    f"- Estado da comunicação: **{texto_seguro(amostra['communication_status'])}**\n"
    f"- Anomalias operacionais registradas: **{anomalias_operacionais}**\n"
    f"- Anomalias de comunicação registradas: **{anomalias_comunicacao}**"
)

st.markdown("#### 2. Avaliação de segurança")

st.write(
    f"O detector estimou o nível de ameaça como "
    f"**{texto_seguro(amostra['threat_level'])}**, com pontuação "
    f"{numero_seguro(amostra['threat_score'], 2)}."
)

st.write(
    f"A lógica fuzzy calculou a pontuação "
    f"{numero_seguro(amostra['security_score'], 2)}, "
    f"classificada como **{texto_seguro(amostra['security_level'])}**."
)

st.markdown("#### 3. Decisão criptográfica")

st.success(
    f"Política selecionada: {algoritmo}"
)

st.caption(
    "O relatório apresenta evidências e decisões produzidas "
    "pelo modelo. Anomalias e níveis estimados não confirmam, "
    "isoladamente, a ocorrência ou a causa de um ataque."
)

st.divider()


# ============================================================
# TABELA DE AMOSTRAS
# ============================================================

with st.expander("Consultar tabela de amostras"):
    colunas_tabela = [
        "sample",
        "time_seconds",
        "scenario",
        "device_status",
        "operational_status",
        "communication_status",
        "threat_level",
        "security_score",
        "security_level",
        "crypto_algorithm",
    ]

    st.dataframe(
        dados[colunas_tabela],
        use_container_width=True,
        hide_index=True
    )

with st.expander("Como interpretar os níveis de segurança"):
    st.markdown("""
    - **BAIXO:** menor nível de segurança calculado pelo modelo.
    - **MODERADO:** nível intermediário de segurança.
    - **ALTO:** maior exigência de segurança.
    - **MUITO ALTO:** nível mais elevado de segurança calculado.

    A política criptográfica é selecionada conforme o mapeamento
    definido no gerenciador criptográfico:

    - **BAIXO / MODERADO:** AES-128
    - **ALTO:** AES-192
    - **MUITO ALTO:** AES-256

    Os resultados são provenientes de uma simulação com dados
    sintéticos. As classificações representam decisões do modelo,
    não a confirmação de ataques reais.
    """)



# ============================================================
# COMPARACAO CRIPTOGRAFICA EXPERIMENTAL
# ============================================================

st.header("Comparação de desempenho criptográfico")

st.caption(
    "Comparação experimental de AES-256-GCM fixo com a política "
    "adaptativa AES-128/192/256-GCM. Tempos medidos no processo Python, "
    "não em hardware ESP32. A comparação criptográfica isolada não "
    "inclui a inferência fuzzy nem a seleção de política."
)


@st.cache_data
def carregar_comparacao(caminho, modificacao):
    comparacao = pd.read_csv(caminho)

    obrigatorias = [
        "sample",
        "scenario",
        "fixed_algorithm",
        "adaptive_algorithm",
        "fixed_total_us",
        "adaptive_total_us",
        "integrity_ok"
    ]

    faltantes = [
        coluna for coluna in obrigatorias
        if coluna not in comparacao.columns
    ]

    if faltantes:
        raise ValueError(
            "Colunas ausentes no CSV de comparação: "
            + ", ".join(faltantes)
        )

    colunas_numericas = [
        "sample",
        "fixed_total_us",
        "adaptive_total_us",
        "adaptive_full_total_us",
        "fuzzy_wall_us",
        "fuzzy_total_us",
        "fuzzy_time_us",
        "fuzzy_us",
        "fuzzy_mean_us",
        "policy_wall_us",
        "policy_selection_us",
        "policy_select_us",
        "policy_time_us",
        "selection_wall_us",
        "selection_time_us",
    ]

    for coluna in colunas_numericas:
        if coluna in comparacao.columns:
            comparacao[coluna] = pd.to_numeric(
                comparacao[coluna],
                errors="coerce"
            )

    return comparacao


def primeira_coluna_existente(tabela, candidatas):
    """
    Identifica a primeira coluna disponível entre as candidatas.
    """
    return next(
        (coluna for coluna in candidatas if coluna in tabela.columns),
        None
    )


if COMPARISON_CSV_PATH.exists():

    try:
        comparacao = carregar_comparacao(
            str(COMPARISON_CSV_PATH),
            COMPARISON_CSV_PATH.stat().st_mtime
        )

        # Aplica o filtro de cenário também à comparação.
        if cenario_selecionado != "Todos":
            comparacao = comparacao[
                comparacao["scenario"].astype(str)
                == cenario_selecionado
            ].copy()

        comparacao_valida = comparacao.dropna(
            subset=["fixed_total_us", "adaptive_total_us"]
        ).copy()

        if comparacao_valida.empty:
            st.info(
                "Não há medições válidas para o cenário selecionado."
            )

        else:

            # ====================================================
            # CRIPTOGRAFIA ISOLADA
            # ====================================================

            media_fixa = comparacao_valida[
                "fixed_total_us"
            ].mean()

            media_adaptativa = comparacao_valida[
                "adaptive_total_us"
            ].mean()

            diferenca = (
                (media_fixa - media_adaptativa)
                / media_fixa * 100
                if media_fixa > 0
                else float("nan")
            )

            st.subheader("Operação criptográfica isolada")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "AES-256 fixo",
                numero_seguro(media_fixa, 3, " µs")
            )

            col2.metric(
                "AES adaptativo",
                numero_seguro(media_adaptativa, 3, " µs")
            )

            col3.metric(
                "Diferença no tempo criptográfico",
                numero_seguro(diferenca, 2, "%")
            )

            st.caption(
                "Diferença positiva indica menor tempo do AES "
                "adaptativo somente na operação criptográfica. "
                "Não representa ganho de desempenho do sistema completo."
            )

            tempos = pd.DataFrame(
                {
                    "Tempo médio (µs)": [
                        media_fixa,
                        media_adaptativa
                    ]
                },
                index=[
                    "Fixa (AES-256)",
                    "Adaptativa (somente AES)"
                ]
            )

            st.bar_chart(tempos)

            # ====================================================
            # CUSTO TOTAL DA ADAPTACAO
            # ====================================================

            st.subheader("Custo total da adaptação")

            coluna_total = primeira_coluna_existente(
                comparacao_valida,
                ["adaptive_full_total_us"]
            )

            coluna_fuzzy = primeira_coluna_existente(
                comparacao_valida,
                [
                    "fuzzy_wall_us",
                    "fuzzy_total_us",
                    "fuzzy_time_us",
                    "fuzzy_us",
                    "fuzzy_mean_us"
                ]
            )

            coluna_politica = primeira_coluna_existente(
                comparacao_valida,
                [
                    "policy_wall_us",
                    "policy_selection_us",
                    "policy_select_us",
                    "policy_time_us",
                    "selection_wall_us",
                    "selection_time_us"
                ]
            )

            media_total = (
                comparacao_valida[coluna_total].mean()
                if coluna_total
                else float("nan")
            )

            media_fuzzy = (
                comparacao_valida[coluna_fuzzy].mean()
                if coluna_fuzzy
                else float("nan")
            )

            media_politica = (
                comparacao_valida[coluna_politica].mean()
                if coluna_politica
                else float("nan")
            )

            # Recupera uma etapa ausente quando o total
            # e as demais parcelas estão disponíveis.
            if (
                pd.notna(media_total)
                and pd.notna(media_politica)
                and pd.isna(media_fuzzy)
            ):
                media_fuzzy = (
                    media_total
                    - media_adaptativa
                    - media_politica
                )

            if (
                pd.notna(media_total)
                and pd.notna(media_fuzzy)
                and pd.isna(media_politica)
            ):
                media_politica = (
                    media_total
                    - media_adaptativa
                    - media_fuzzy
                )

            if pd.notna(media_total):

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Inferência fuzzy",
                    numero_seguro(media_fuzzy, 3, " µs")
                )

                col2.metric(
                    "Seleção da política",
                    numero_seguro(media_politica, 3, " µs")
                )

                col3.metric(
                    "Adaptativo completo",
                    numero_seguro(media_total, 3, " µs")
                )

                tabela_custos = pd.DataFrame(
                    {
                        "Etapa": [
                            "AES-256 fixo (somente criptografia)",
                            "AES adaptativo (somente criptografia)",
                            "Inferência fuzzy",
                            "Seleção da política",
                            "Sistema adaptativo completo"
                        ],
                        "Tempo médio (µs)": [
                            media_fixa,
                            media_adaptativa,
                            media_fuzzy,
                            media_politica,
                            media_total
                        ]
                    }
                )

                st.dataframe(
                    tabela_custos,
                    hide_index=True,
                    use_container_width=True
                )

                st.caption(
                    "O tempo adaptativo completo inclui inferência "
                    "fuzzy, seleção de política e criptografia. "
                    "É uma soma de médias de etapas medidas "
                    "separadamente, não uma medição contínua de "
                    "ponta a ponta. O AES-256 fixo não inclui "
                    "monitoramento equivalente."
                )

            else:
                st.info(
                    "O CSV de comparação ainda não contém a coluna "
                    "adaptive_full_total_us. Execute python main.py "
                    "com a versão atualizada de crypto_comparison.py "
                    "para exibir o custo total da adaptação."
                )

            # ====================================================
            # DISTRIBUICAO DOS ALGORITMOS
            # ====================================================

            st.subheader(
                "Distribuição dos algoritmos adaptativos"
            )

            distribuicao_comparacao = (
                comparacao_valida["adaptive_algorithm"]
                .value_counts()
                .rename_axis("Algoritmo")
                .to_frame("Amostras")
            )

            st.bar_chart(distribuicao_comparacao)

            # ====================================================
            # VERIFICACAO DE INTEGRIDADE
            # ====================================================

            integridade = (
                comparacao_valida["integrity_ok"]
                .astype(str)
                .str.strip()
                .str.lower()
                .eq("true")
            )

            st.write(
                "**Integridade verificada:** "
                f"{int(integridade.sum())} "
                f"de {len(integridade)} amostras."
            )

            st.caption(
                "Os resultados podem variar entre execuções. "
                "Não representam medição de consumo energético "
                "nem comprovam desempenho em hardware ESP32."
            )

            # ====================================================
            # TABELA DE MEDICOES
            # ====================================================

            with st.expander(
                "Consultar medições da comparação"
            ):
                st.dataframe(
                    comparacao_valida,
                    use_container_width=True,
                    hide_index=True
                )

    except Exception as erro:
        st.error(
            f"Não foi possível carregar a comparação: {erro}"
        )

else:
    st.info(
        "Arquivo crypto_comparison_results.csv não encontrado. "
        "Execute python main.py para gerar a comparação."
    )

st.divider()


# ============================================================
# EXPORTACAO
# ============================================================

csv_exportacao = dados.drop(
    columns=["crypto_policy_dict"],
    errors="ignore"
).to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Exportar dados filtrados em CSV",
    data=csv_exportacao,
    file_name="resultados_iot_filtrados.csv",
    mime="text/csv"
)

st.caption(
    "Dados sintéticos gerados para experimentação acadêmica. "
    "Esta interface não representa, por si só, monitoramento "
    "de hardware físico em tempo real."
)
