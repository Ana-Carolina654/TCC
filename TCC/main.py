

"""
main.py

Ponto de entrada principal do projeto de TCC.

Responsabilidades:
1. Executar a simulação integrada.
2. Gerar o CSV com os resultados.
3. Calcular as métricas experimentais.
4. Comparar criptografia fixa e adaptativa.
"""

from simulation import executar_simulacao
from metrics import executar_analise
from crypto_comparison import executar_comparacao


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    print("=" * 68)
    print("SISTEMA DE SEGURANÇA ADAPTATIVA PARA DISPOSITIVOS IoT")
    print("Criptografia adaptativa baseada em lógica fuzzy")
    print("=" * 68)

    # 1. Executa a simulação e gera o CSV.
    print("\n[ETAPA 1] Executando a simulação...")
    executar_simulacao()

    # 2. Analisa os resultados da simulação.
    print("\n[ETAPA 2] Calculando as métricas...")
    executar_analise()

    # 3. Compara as políticas criptográficas.
    print("\n[ETAPA 3] Comparando criptografia fixa e adaptativa...")
    executar_comparacao()

    print("\n" + "=" * 68)
    print("EXECUÇÃO COMPLETA DO SISTEMA FINALIZADA")
    print("=" * 68)


if __name__ == "__main__":
    main()
