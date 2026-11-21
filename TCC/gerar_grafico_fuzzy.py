from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

pasta = Path(__file__).resolve().parent
dados = pd.read_csv(pasta / "simulation_results.csv").sort_values("sample")

fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
ax.plot(dados["sample"], dados["security_score"], color="#154d7b", linewidth=1.8)

for limite in (3, 5, 7.5):
    ax.axhline(limite, color="#65788b", linestyle="--", linewidth=0.9)

ax.set(
    xlabel="Amostra da simulação",
    ylabel="Índice de segurança requerida",
    ylim=(0, 10),
)
ax.set_yticks([0, 3, 5, 7.5, 10], labels=["0", "3", "5", "7,5", "10"])

saida = pasta / "indice_fuzzy_por_amostra.png"
fig.savefig(saida, dpi=300, facecolor="white")
plt.close(fig)
print(f"Gráfico salvo em: {saida}")