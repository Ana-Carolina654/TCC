"""Compara AES-256-GCM fixo com a política AES-GCM adaptativa registrada na simulação.

Execute após simulation.py gerar simulation_results.csv.
Os tempos medidos são do ambiente Python, não de um ESP32 físico.
"""


"""Compara AES-256-GCM fixo com fuzzy + AES-GCM adaptativo.

Executar depois de gerar simulation_results.csv.
Tempos e CPU referem-se ao processo Python no computador, não ao ESP32.
"""
import csv
import json
import statistics
from collections import Counter
from pathlib import Path
from time import perf_counter_ns, process_time_ns

from crypto_manager import CryptoManager
from fuzzy_security import calcular_nivel_seguranca

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / 'simulation_results.csv'
OUTPUT_FILE = BASE_DIR / 'crypto_comparison_results.csv'
REPETITIONS = 200
FUZZY_REPETITIONS = 3  # A inferência reconstrói as regras a cada chamada.


def build_message(row):
    """Usa exatamente a mesma telemetria nas duas políticas."""
    fields = (
        'sample', 'time_seconds', 'scenario', 'battery',
        'temperature', 'load', 'rotation_speed', 'torque',
        'wear', 'signal_strength', 'interference'
    )
    return json.dumps(
        {key: row[key] for key in fields},
        ensure_ascii=False,
        separators=(',', ':')
    ).encode('utf-8')


def measure_crypto(manager, message, repetitions):
    """Mede encrypt/decrypt e tempo de CPU, sem seleção de política."""
    encryption_times = []
    decryption_times = []
    cpu_start = process_time_ns()

    for _ in range(repetitions):
        start = perf_counter_ns()
        encrypted = manager.encrypt(message)
        encryption_times.append(perf_counter_ns() - start)

        start = perf_counter_ns()
        decrypted = manager.decrypt(encrypted)
        decryption_times.append(perf_counter_ns() - start)

        if decrypted != message:
            raise AssertionError(
                'Falha na integridade dos dados descriptografados.'
            )

    cpu_us = (
        (process_time_ns() - cpu_start) / 1000 / repetitions
    )

    return (
        statistics.mean(encryption_times) / 1000,
        statistics.mean(decryption_times) / 1000,
        cpu_us
    )


def measure_fuzzy(row, repetitions):
    """Mede a função fuzzy real, incluindo a construção do sistema."""
    times = []
    cpu_start = process_time_ns()
    decision = None

    for _ in range(repetitions):
        start = perf_counter_ns()

        decision = calcular_nivel_seguranca(
            row['threat_level'],
            row['operational_status'],
            row['communication_status']
        )

        times.append(perf_counter_ns() - start)

    cpu_us = (
        (process_time_ns() - cpu_start) / 1000 / repetitions
    )

    return (
        decision,
        statistics.mean(times) / 1000,
        cpu_us
    )


def executar_comparacao(
    input_file=INPUT_FILE,
    output_file=OUTPUT_FILE,
    repetitions=REPETITIONS,
    fuzzy_repetitions=FUZZY_REPETITIONS
):
    if repetitions < 1 or fuzzy_repetitions < 1:
        raise ValueError(
            'As quantidades de repetições devem ser maiores que zero.'
        )

    input_file = Path(input_file)
    output_file = Path(output_file)

    if not input_file.is_file():
        raise FileNotFoundError(
            f'Arquivo {input_file} não encontrado. '
            'Execute main.py primeiro.'
        )

    with input_file.open(
        'r', newline='', encoding='utf-8-sig'
    ) as f:
        reader = csv.DictReader(f)

        required = {
            'security_level', 'threat_level',
            'operational_status', 'communication_status',
            'sample', 'time_seconds', 'scenario',
            'battery', 'temperature', 'load',
            'rotation_speed', 'torque', 'wear',
            'signal_strength', 'interference'
        }

        missing = required - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                f'Colunas ausentes no CSV: {sorted(missing)}'
            )

        rows = list(reader)

    if not rows:
        raise ValueError('O CSV não contém amostras.')

    fixed = CryptoManager()
    adaptive = CryptoManager()

    # Política fixa definida antes do benchmark.
    fixed.select_policy('MUITO ALTO')

    results = []

    for index, row in enumerate(rows):
        print(
            f'Processando amostra {index + 1}/{len(rows)}...',
            flush=True
        )

        message = build_message(row)

        # Mede a decisão fuzzy real.
        (
            (fuzzy_score, fuzzy_level),
            fuzzy_us,
            fuzzy_cpu_us
        ) = measure_fuzzy(row, fuzzy_repetitions)

        expected_level = row['security_level'].strip().upper()
        matches = fuzzy_level == expected_level

        if not matches:
            print(
                f"  AVISO: amostra {row['sample']}: "
                f"fuzzy={fuzzy_level}, CSV={expected_level}."
            )

        # Mede a seleção da política criptográfica.
        select_start_cpu = process_time_ns()
        select_start = perf_counter_ns()

        policy = adaptive.select_policy(fuzzy_level)

        selection_us = (
            perf_counter_ns() - select_start
        ) / 1000

        selection_cpu_us = (
            process_time_ns() - select_start_cpu
        ) / 1000

        # Alterna a ordem para reduzir viés sistemático.
        if index % 2 == 0:
            fixed_enc, fixed_dec, fixed_cpu = measure_crypto(
                fixed, message, repetitions
            )

            adaptive_enc, adaptive_dec, adaptive_cpu = measure_crypto(
                adaptive, message, repetitions
            )
        else:
            adaptive_enc, adaptive_dec, adaptive_cpu = measure_crypto(
                adaptive, message, repetitions
            )

            fixed_enc, fixed_dec, fixed_cpu = measure_crypto(
                fixed, message, repetitions
            )

        fixed_total = fixed_enc + fixed_dec
        adaptive_crypto_total = adaptive_enc + adaptive_dec

        adaptive_full = (
            fuzzy_us
            + selection_us
            + adaptive_crypto_total
        )

        adaptive_cpu_full = (
            fuzzy_cpu_us
            + selection_cpu_us
            + adaptive_cpu
        )

        results.append({
            'sample': row['sample'],
            'scenario': row['scenario'],
            'security_level': expected_level,
            'message_bytes': len(message),
            'repetitions': repetitions,
            'fixed_algorithm': 'AES-256',
            'adaptive_algorithm': policy['algorithm'],

            # Medições criptográficas anteriores.
            'fixed_encrypt_us': round(fixed_enc, 4),
            'fixed_decrypt_us': round(fixed_dec, 4),
            'fixed_total_us': round(fixed_total, 4),
            'adaptive_encrypt_us': round(adaptive_enc, 4),
            'adaptive_decrypt_us': round(adaptive_dec, 4),
            'adaptive_total_us': round(
                adaptive_crypto_total, 4
            ),
            'integrity_ok': True,

            # Novas medições.
            'fuzzy_repetitions': fuzzy_repetitions,
            'fuzzy_score_recomputed': round(
                fuzzy_score, 4
            ),
            'fuzzy_level_recomputed': fuzzy_level,
            'fuzzy_matches_simulation': matches,
            'fuzzy_time_us': round(fuzzy_us, 4),
            'policy_selection_us': round(
                selection_us, 4
            ),
            'adaptive_full_total_us': round(
                adaptive_full, 4
            ),

            # Tempos de CPU.
            'fixed_cpu_us': round(fixed_cpu, 4),
            'adaptive_crypto_cpu_us': round(
                adaptive_cpu, 4
            ),
            'fuzzy_cpu_us': round(fuzzy_cpu_us, 4),
            'policy_selection_cpu_us': round(
                selection_cpu_us, 4
            ),
            'adaptive_full_cpu_us': round(
                adaptive_cpu_full, 4
            ),
        })

    # Exporta os resultados.
    with output_file.open(
        'w', newline='', encoding='utf-8-sig'
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    def avg(column):
        return statistics.mean(
            row[column] for row in results
        )

    fixed_avg = avg('fixed_total_us')
    crypto_avg = avg('adaptive_total_us')
    full_avg = avg('adaptive_full_total_us')

    counts = Counter(
        r['adaptive_algorithm'] for r in results
    )

    difference_crypto = (
        100 * (fixed_avg - crypto_avg) / fixed_avg
        if fixed_avg else 0
    )

    difference_full = (
        100 * (fixed_avg - full_avg) / fixed_avg
        if fixed_avg else 0
    )

    mismatch_count = sum(
        not r['fuzzy_matches_simulation']
        for r in results
    )

    print('=' * 65)
    print('COMPARAÇÃO: CRIPTOGRAFIA FIXA VS. FUZZY + CRIPTOGRAFIA')
    print('=' * 65)

    print(f'Amostras analisadas: {len(results)}')
    print(
        f'Repetições AES: {repetitions}; '
        f'repetições fuzzy: {fuzzy_repetitions}'
    )
    print(f'Algoritmos adaptativos: {dict(counts)}')
    print(
        f'Decisões fuzzy divergentes do CSV: {mismatch_count}'
    )

    print(
        f'Fixo - tempo criptográfico: '
        f'{fixed_avg:.3f} µs'
    )
    print(
        f'Adaptativo - tempo criptográfico: '
        f'{crypto_avg:.3f} µs'
    )
    print(
        f'Adaptativo - tempo fuzzy: '
        f'{avg("fuzzy_time_us"):.3f} µs'
    )
    print(
        f'Adaptativo - seleção de política: '
        f'{avg("policy_selection_us"):.3f} µs'
    )
    print(
        f'Adaptativo - tempo TOTAL: '
        f'{full_avg:.3f} µs'
    )

    print(
        'Diferença somente AES '
        '(positiva = adaptativo mais rápido): '
        f'{difference_crypto:.2f}%'
    )
    print(
        'Diferença TOTAL '
        '(positiva = adaptativo mais rápido): '
        f'{difference_full:.2f}%'
    )

    print(
        f'CPU média fixa: '
        f'{avg("fixed_cpu_us"):.3f} µs/amostra'
    )
    print(
        f'CPU média adaptativa total: '
        f'{avg("adaptive_full_cpu_us"):.3f} µs/amostra'
    )

    print('Integridade: todas as verificações passaram.')
    print(f'Resultados salvos em: {output_file}')
    print(
        'Observação: medições no processo Python; '
        'não são medições no ESP32.'
    )

    return results


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == '__main__':
    executar_comparacao()


