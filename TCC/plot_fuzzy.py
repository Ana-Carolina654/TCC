
import matplotlib.pyplot as plt
from fuzzy_security import criar_sistema_fuzzy

# Recupera o sistema fuzzy já implementado.
sistema = criar_sistema_fuzzy()

# Obtém as variáveis diretamente do sistema.
variaveis = {
    "Ameaça": next(v for v in sistema.antecedents if v.label == "ameaca"),
    "Condição operacional": next(v for v in sistema.antecedents if v.label == "operacional"),
    "Comunicação": next(v for v in sistema.antecedents if v.label == "comunicacao"),
    "Nível de segurança": next(v for v in sistema.consequents if v.label == "seguranca"),
}

# Um gráfico para cada variável.
fig, eixos = plt.subplots(2, 2, figsize=(12, 8))

for eixo, (titulo, variavel) in zip(eixos.flat, variaveis.items()):

    for nome, termo in variavel.terms.items():
        eixo.plot(
            variavel.universe,
            termo.mf,
            linewidth=2,
            label=nome.replace("_", " ").capitalize()
        )

    eixo.set_title(titulo)
    eixo.set_xlabel("Universo de discurso (0 a 10)")
    eixo.set_ylabel("Grau de pertinência")
    eixo.set_xlim(0, 10)
    eixo.set_ylim(0, 1.05)
    eixo.grid(True, alpha=0.3)
    eixo.legend()

plt.tight_layout()

# Salva em alta resolução.
plt.savefig(
    "funcoes_pertinencia_fuzzy.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
