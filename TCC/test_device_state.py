# test_device_state.py

from sensors import SensorSimulator
from device_state import DeviceStateAnalyzer


# ============================================================
# INICIALIZAÇÃO
# ============================================================

simulator = SensorSimulator()
analyzer = DeviceStateAnalyzer()


# ============================================================
# TESTE
# ============================================================

for i in range(10):

    sensor_data = simulator.update()

    device_state = analyzer.analyze(sensor_data)

    print()
    print("=" * 60)
    print(f"AMOSTRA {i + 1}")
    print("=" * 60)

    print(f"Bateria:       {sensor_data.battery:.2f}%")
    print(f"Temperatura:   {sensor_data.temperature:.2f} °C")
    print(f"Carga:         {sensor_data.load:.2f}%")

    print()

    print(f"Status bateria:       {device_state.battery_status}")
    print(f"Status temperatura:   {device_state.temperature_status}")
    print(f"Status carga:         {device_state.load_status}")

    print()

    print(
        f"ESTADO DO DISPOSITIVO: "
        f"{device_state.status.value}"
    )