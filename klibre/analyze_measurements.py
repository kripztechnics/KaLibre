import json
import numpy as np
from pathlib import Path

# Load all 5 measurements
files = [
    'measurements/measurement_Sub_#2_20260714_142535.json',
    'measurements/measurement_Top_#2_20260714_142852.json',
    'measurements/measurement_Top_#3_20260714_142945.json',
    'measurements/measurement_Top_#4_20260714_143423.json',
    'measurements/measurement_FULL_#2_20260714_143204.json',
]

measurements = {}
for f in files:
    with open(f) as fp:
        data = json.load(fp)
        name = Path(f).stem.split('measurement_')[1]
        measurements[name] = data
        print(f'\n=== {name} ===')
        print(f'  Delay: {data["absolute_delay_ms"]:.2f} ms')
        print(f'  Coherence (mean): {np.mean(data["coherence"]):.3f}')
        print(f'  Coherence (min): {np.min(data["coherence"]):.3f}')
        print(f'  Magnitude range: [{np.min(data["magnitude_db_rel"]):.1f}, {np.max(data["magnitude_db_rel"]):.1f}] dB')
        print(f'  Phase range: [{np.min(data["phase_deg"]):.1f}, {np.max(data["phase_deg"]):.1f}]°')
        print(f'  Freq range: [{data["freqs"][0]:.1f}, {data["freqs"][-1]:.1f}] Hz')

# Analyze SUB measurements
print("\n\n=== ANALYSE SUB ===")
sub = measurements['Sub_#2_20260714_142535']
print(f"Sub delay: {sub['absolute_delay_ms']:.2f} ms")
print(f"Sub coherence (mean): {np.mean(sub['coherence']):.3f}")

# Analyze TOP measurements
print("\n=== ANALYSE TOP (sans délai vs avec délai) ===")
top_no_delay = measurements['Top_#2_20260714_142852']
top_delay_109 = measurements['Top_#3_20260714_142945']
top_delay_112 = measurements['Top_#4_20260714_143423']

print(f"\nTop (no delay):")
print(f"  Delay: {top_no_delay['absolute_delay_ms']:.2f} ms")
print(f"  Coherence (mean): {np.mean(top_no_delay['coherence']):.3f}")

print(f"\nTop (10.9ms delay):")
print(f"  Delay: {top_delay_109['absolute_delay_ms']:.2f} ms")
print(f"  Coherence (mean): {np.mean(top_delay_109['coherence']):.3f}")

print(f"\nTop (11.2ms delay):")
print(f"  Delay: {top_delay_112['absolute_delay_ms']:.2f} ms")
print(f"  Coherence (mean): {np.mean(top_delay_112['coherence']):.3f}")

# Analyze FULL (Sub + Top combined)
print("\n=== ANALYSE FULL (Sub + Top@11.2ms) ===")
full = measurements['FULL_#2_20260714_143204']
print(f"Full delay: {full['absolute_delay_ms']:.2f} ms")
print(f"Full coherence (mean): {np.mean(full['coherence']):.3f}")
print(f"Full coherence (min): {np.min(full['coherence']):.3f}")

# Check delay alignment
print(f"\n=== DÉLAI ALIGNMENT CHECK ===")
print(f"Sub delay: {sub['absolute_delay_ms']:.2f} ms")
print(f"Top delay (aligned): {top_delay_112['absolute_delay_ms']:.2f} ms")
delay_diff = top_delay_112['absolute_delay_ms'] - sub['absolute_delay_ms']
print(f"Delay difference (Top - Sub): {delay_diff:.2f} ms")
print(f"Distance apart: 20cm → expected time delay ≈ 0.58ms @ 343 m/s")

# Check summation quality at crossover (101 Hz)
print(f"\n=== SOMMATION @ CROSSOVER (101 Hz) ===")
freqs = np.array(sub['freqs'])
idx_101 = np.argmin(np.abs(freqs - 101))
crossover_freq = freqs[idx_101]

sub_mag = np.array(sub['magnitude_db_rel'])
top_mag_112 = np.array(top_delay_112['magnitude_db_rel'])
full_mag = np.array(full['magnitude_db_rel'])

print(f"Crossover frequency found: {crossover_freq:.1f} Hz")
print(f"\nAt {crossover_freq:.1f} Hz:")
print(f"  Sub magnitude: {sub_mag[idx_101]:.2f} dB")
print(f"  Top magnitude: {top_mag_112[idx_101]:.2f} dB")
print(f"  Full magnitude: {full_mag[idx_101]:.2f} dB")

# Expected sum (linear addition)
sub_lin = 10 ** (sub_mag[idx_101] / 20)
top_lin = 10 ** (top_mag_112[idx_101] / 20)
expected_sum_db = 20 * np.log10(sub_lin + top_lin)
print(f"  Expected sum (linear): {expected_sum_db:.2f} dB")
print(f"  Actual sum: {full_mag[idx_101]:.2f} dB")
print(f"  Difference: {full_mag[idx_101] - expected_sum_db:.2f} dB")

# Check coherence around crossover
print(f"\n=== COHERENCE AROUND CROSSOVER ===")
idx_range = np.where((freqs >= 80) & (freqs <= 150))[0]
if len(idx_range) > 0:
    full_coherence = np.array(full['coherence'])
    coh_at_crossover = full_coherence[idx_101]
    print(f"Coherence @ {crossover_freq:.1f} Hz: {coh_at_crossover:.3f}")
    print(f"Mean coherence [80-150 Hz]: {np.mean(full_coherence[idx_range]):.3f}")
    print(f"Min coherence [80-150 Hz]: {np.min(full_coherence[idx_range]):.3f}")
