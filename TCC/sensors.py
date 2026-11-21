# sensors.py

from dataclasses import dataclass
import numpy as np

import config


@dataclass
class SensorData:
    """
    Representa uma leitura bruta dos sensores.
    """

    battery: float
    signal_strength: float
    interference: float
    temperature: float
    rotation_speed: float
    torque: float
    wear: float
    load: float


class SensorSimulator:
    """
    Simulador responsável pela geração das variáveis brutas
    do dispositivo IoT.
    """

    def __init__(self, seed=None):
        if seed is None:
            seed = config.RANDOM_SEED

        self.rng = np.random.default_rng(seed)

        self.battery = config.BATTERY_INITIAL
        self.signal_strength = config.SIGNAL_INITIAL
        self.interference = config.INTERFERENCE_INITIAL
        self.temperature = config.TEMPERATURE_INITIAL
        self.rotation_speed = config.ROTATION_INITIAL
        self.torque = config.TORQUE_INITIAL
        self.wear = config.WEAR_INITIAL
        self.load = config.LOAD_INITIAL

    def _clamp(self, value, minimum, maximum):
        """
        Mantém o valor dentro dos limites definidos.
        """
        return float(np.clip(value, minimum, maximum))

    def update(self):
        """
        Gera uma nova leitura dos sensores.

        As variáveis sofrem pequenas variações aleatórias,
        representando o comportamento normal do dispositivo.
        """

        # ----------------------------------------------------
        # Bateria
        # ----------------------------------------------------

        self.battery -= abs(
            self.rng.normal(0.02, 0.01)
        )

        self.battery = self._clamp(
            self.battery,
            config.BATTERY_MIN,
            config.BATTERY_MAX
        )

        # ----------------------------------------------------
        # Sinal
        # ----------------------------------------------------

        
        self.signal_strength += 0.2 * (
            config.SIGNAL_STRENGTH_NORMAL - self.signal_strength
        ) + self.rng.normal(0, 1.0)

        self.signal_strength = self._clamp(
            self.signal_strength,
            config.SIGNAL_MIN,
            config.SIGNAL_MAX
        )


        # ----------------------------------------------------
        # Interferência
        # ----------------------------------------------------

        self.interference += self.rng.normal(0, 2)

        self.interference = self._clamp(
            self.interference,
            config.INTERFERENCE_MIN,
            config.INTERFERENCE_MAX
        )

        # ----------------------------------------------------
        # Temperatura
        # ----------------------------------------------------

        self.temperature += self.rng.normal(0, 0.5)

        self.temperature = self._clamp(
            self.temperature,
            config.TEMPERATURE_MIN,
            config.TEMPERATURE_MAX
        )

        # ----------------------------------------------------
        # Velocidade de rotação
        # ----------------------------------------------------

        self.rotation_speed += self.rng.normal(0, 100)

        self.rotation_speed = self._clamp(
            self.rotation_speed,
            config.ROTATION_MIN,
            config.ROTATION_MAX
        )

        # ----------------------------------------------------
        # Torque
        # ----------------------------------------------------

        self.torque += self.rng.normal(0, 5)

        self.torque = self._clamp(
            self.torque,
            config.TORQUE_MIN,
            config.TORQUE_MAX
        )

        # ----------------------------------------------------
        # Desgaste
        # ----------------------------------------------------

        self.wear += abs(
            self.rng.normal(0.005, 0.002)
        )

        self.wear = self._clamp(
            self.wear,
            config.WEAR_MIN,
            config.WEAR_MAX
        )

        # ----------------------------------------------------
        # Carga
        # ----------------------------------------------------

        self.load += self.rng.normal(0, 3)

        self.load = self._clamp(
            self.load,
            config.LOAD_MIN,
            config.LOAD_MAX
        )

        return SensorData(
            battery=self.battery,
            signal_strength=self.signal_strength,
            interference=self.interference,
            temperature=self.temperature,
            rotation_speed=self.rotation_speed,
            torque=self.torque,
            wear=self.wear,
            load=self.load
        )