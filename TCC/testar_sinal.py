
from sensors import SensorSimulator
import config

simulador = SensorSimulator()

print("Referência normal:", config.SIGNAL_STRENGTH_NORMAL, "dBm")
print("-" * 45)

for i in range(20):
    simulador.update()
    print(
        f"Amostra {i + 1:02d}: "
        f"{simulador.signal_strength:.2f} dBm"
    )
