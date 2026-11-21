from sensors import SensorSimulator


simulator = SensorSimulator()

for i in range(10):
    data = simulator.update()

    print(
        f"Amostra {i + 1}: "
        f"battery={data.battery:.2f}% | "
        f"signal={data.signal_strength:.2f} dBm | "
        f"interference={data.interference:.2f}% | "
        f"temperature={data.temperature:.2f} °C | "
        f"rotation={data.rotation_speed:.2f} RPM | "
        f"torque={data.torque:.2f} N.m | "
        f"wear={data.wear:.4f}% | "
        f"load={data.load:.2f}%"
    ) 