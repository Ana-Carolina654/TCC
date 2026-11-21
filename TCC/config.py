
# ============================================================
# CONFIGURAÇÕES GERAIS DA SIMULAÇÃO
# ============================================================

RANDOM_SEED = 42


# ============================================================
# VARIÁVEIS DOS SENSORES
# ============================================================

# ------------------------------------------------------------
# Bateria (%)
# ------------------------------------------------------------

BATTERY_MIN = 0.0
BATTERY_MAX = 100.0
BATTERY_INITIAL = 100.0


# ------------------------------------------------------------
# Intensidade do sinal de comunicação (dBm)
# Quanto mais próximo de zero, melhor o sinal.
# ------------------------------------------------------------

SIGNAL_MIN = -120.0
SIGNAL_MAX = -30.0
SIGNAL_INITIAL = -60.0


# ------------------------------------------------------------
# Interferência (%)
# ------------------------------------------------------------

INTERFERENCE_MIN = 0.0
INTERFERENCE_MAX = 100.0
INTERFERENCE_INITIAL = 10.0


# ------------------------------------------------------------
# Temperatura (°C)
# ------------------------------------------------------------

TEMPERATURE_MIN = -20.0
TEMPERATURE_MAX = 100.0
TEMPERATURE_INITIAL = 40.0


# ------------------------------------------------------------
# Velocidade de rotação (RPM)
# ------------------------------------------------------------

ROTATION_MIN = 0.0
ROTATION_MAX = 10000.0
ROTATION_INITIAL = 3000.0


# ------------------------------------------------------------
# Torque (N·m)
# ------------------------------------------------------------

TORQUE_MIN = 0.0
TORQUE_MAX = 500.0
TORQUE_INITIAL = 100.0


# ------------------------------------------------------------
# Desgaste (%)
# ------------------------------------------------------------

WEAR_MIN = 0.0
WEAR_MAX = 100.0
WEAR_INITIAL = 0.0


# ------------------------------------------------------------
# Carga operacional (%)
# ------------------------------------------------------------

LOAD_MIN = 0.0
LOAD_MAX = 100.0
LOAD_INITIAL = 30.0


# ============================================================
# SIMULAÇÃO TEMPORAL
# ============================================================

# Número de amostras
NUM_SAMPLES = 100

# Intervalo entre amostras (segundos)
SAMPLE_INTERVAL = 10.0


# ============================================================
# ESTADOS DO DISPOSITIVO
# ============================================================

# ------------------------------------------------------------
# Bateria (%)
#
# NORMAL      >= 60%
# ATENÇÃO     30% - 59.99%
# DEGRADADO   15% - 29.99%
# CRÍTICO     < 15%
# ------------------------------------------------------------

BATTERY_NORMAL_MIN = 60.0
BATTERY_ATTENTION_MIN = 30.0
BATTERY_DEGRADED_MIN = 15.0


# ------------------------------------------------------------
# Temperatura (°C)
#
# NORMAL      < 60°C
# ATENÇÃO     60°C - 74.99°C
# DEGRADADO   75°C - 89.99°C
# CRÍTICO     >= 90°C
# ------------------------------------------------------------

TEMPERATURE_NORMAL_MAX = 60.0
TEMPERATURE_ATTENTION_MAX = 75.0
TEMPERATURE_DEGRADED_MAX = 90.0


# ------------------------------------------------------------
# Carga operacional (%)
#
# NORMAL      < 60%
# ATENÇÃO     60% - 79.99%
# DEGRADADO   80% - 94.99%
# CRÍTICO     >= 95%
# ------------------------------------------------------------

LOAD_NORMAL_MAX = 60.0
LOAD_ATTENTION_MAX = 80.0
LOAD_DEGRADED_MAX = 95.0


# ============================================================
# PARÂMETROS DE COMUNICAÇÃO
# ============================================================

# ------------------------------------------------------------
# Intensidade do sinal Wi-Fi (dBm)
#
# CRÍTICO:
#   Sinal inferior a -80 dBm.
#
# DEGRADADO:
#   Sinal inferior a -63 dBm,
#   desde que não esteja CRÍTICO.
#
# NORMAL:
#   Sinal igual ou superior a -58 dBm.
#
# HISTERESE:
#   Entre -63 e -58 dBm, mantém o estado anterior.
#
# O parâmetro SIGNAL_STRENGTH_NORMAL é preservado
# por compatibilidade com possíveis outros módulos.
# ------------------------------------------------------------

SIGNAL_STRENGTH_NORMAL = -60
SIGNAL_STRENGTH_DEGRADED = -80

SIGNAL_STRENGTH_DEGRADE_THRESHOLD = -63.0
SIGNAL_STRENGTH_RECOVERY_THRESHOLD = -58.0


# ------------------------------------------------------------
# Interferência (%)
#
# NORMAL      <= 20%
# DEGRADADO   > 20% e <= 50%
# CRÍTICO     > 50%
# ------------------------------------------------------------

INTERFERENCE_NORMAL = 20
INTERFERENCE_DEGRADED = 50


# ============================================================
# PARÂMETROS OPERACIONAIS
# ============================================================

# ------------------------------------------------------------
# Velocidade de rotação (RPM)
#
# NORMAL       2500 - 3500 RPM
# ATENÇÃO      2000 - 2499 / 3501 - 4000 RPM
# DEGRADADO    1000 - 1999 / 4001 - 5000 RPM
# CRÍTICO      < 1000 / > 5000 RPM
#
# Valores definidos para o perfil de simulação.
# ------------------------------------------------------------

ROTATION_NORMAL_MIN = 2500.0
ROTATION_NORMAL_MAX = 3500.0

ROTATION_ATTENTION_MIN = 2000.0
ROTATION_ATTENTION_MAX = 4000.0

ROTATION_DEGRADED_MIN = 1000.0
ROTATION_DEGRADED_MAX = 5000.0


# ------------------------------------------------------------
# Torque (N·m)
#
# NORMAL       <= 150 N·m
# ATENÇÃO      > 150 - 250 N·m
# DEGRADADO    > 250 - 400 N·m
# CRÍTICO      > 400 N·m
#
# Valores definidos para o perfil de simulação.
# ------------------------------------------------------------

TORQUE_NORMAL_MAX = 150.0
TORQUE_ATTENTION_MAX = 250.0
TORQUE_DEGRADED_MAX = 400.0


# ------------------------------------------------------------
# Desgaste (%)
#
# NORMAL       < 50%
# ATENÇÃO      50% - 69.99%
# DEGRADADO    70% - 89.99%
# CRÍTICO      >= 90%
#
# Representa desgaste relativo da ferramenta.
# ------------------------------------------------------------

WEAR_NORMAL_MAX = 50.0
WEAR_ATTENTION_MAX = 70.0
WEAR_DEGRADED_MAX = 90.0


# ============================================================
# LIMITES ADICIONAIS PARA device_state.py
# ============================================================

BATTERY_LOW_MIN = BATTERY_DEGRADED_MIN

TEMPERATURE_HIGH_MAX = TEMPERATURE_DEGRADED_MAX

LOAD_HIGH_MAX = LOAD_DEGRADED_MAX
