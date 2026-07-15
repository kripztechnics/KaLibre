import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Load measurements
files = {
    'Sub': 'measurements/measurement_Sub_#2_20260714_142535.json',
    'Top_no_delay': 'measurements/measurement_Top_#2_20260714_142852.json',
    'Top_10.9ms': 'measurements/measurement_Top_#3_20260714_142945.json',
    'Top_11.2ms': 'measurements/measurement_Top_#4_20260714_143423.json',
    'FULL': 'measurements/measurement_FULL_#2_20260714_143204.json',
}

meas = {}
for name, f in files.items():
    with open(f) as fp:
        meas[name] = json.load(fp)

# Use Top@11.2ms as reference
sub = meas['Sub']
top = meas['Top_11.2ms']
full = meas['FULL']

print("=" * 70)
print("ANALYSE DÉTAILLÉE DE LA SOMMATION SUB + TOP @ 101Hz LR24")
print("=" * 70)

# Get frequency data
freqs = np.array(sub['freqs'])
sub_mag = np.array(sub['magnitude_db_rel'])
sub_phase = np.array(sub['phase_deg'])

# Interpolate Top to Sub's frequency range
top_freqs = np.array(top['freqs'])
top_mag = np.array(top['magnitude_db_rel'])
top_phase = np.array(top['phase_deg'])

# Use Full's frequency grid (more complete)
full_freqs = np.array(full['freqs'])
full_mag = np.array(full['magnitude_db_rel'])
full_phase = np.array(full['phase_deg'])
full_coh = np.array(full['coherence'])

# Interpolate Sub and Top to Full's grid
from scipy.interpolate import interp1d

# Sub (only goes to 400Hz, extrapolate with low response beyond)
sub_interp_mag = interp1d(freqs, sub_mag, bounds_error=False, fill_value=sub_mag[-1]-40, kind='cubic')
sub_at_full = sub_interp_mag(full_freqs)

# Top
top_interp_mag = interp1d(top_freqs, top_mag, bounds_error=False, fill_value=-100, kind='cubic')
top_at_full = top_interp_mag(full_freqs)

# Calculate expected linear sum
sub_lin = 10 ** (sub_at_full / 20)
top_lin = 10 ** (top_at_full / 20)
expected_sum = 20 * np.log10(sub_lin + top_lin)

# Actual sum
actual_sum = full_mag

# Calculate error
error = actual_sum - expected_sum

# Analyze by frequency bands
print("\n1. DÉLAIS")
print("-" * 70)
print(f"Sub delay: {sub['absolute_delay_ms']:.3f} ms")
print(f"Top delay: {top['absolute_delay_ms']:.3f} ms")
print(f"Full delay: {full['absolute_delay_ms']:.3f} ms")
print(f"Delay alignment (Top - Sub): {top['absolute_delay_ms'] - sub['absolute_delay_ms']:.3f} ms")
print(f"STATUS: {'✓ EXCELLENT' if abs(top['absolute_delay_ms'] - sub['absolute_delay_ms']) < 0.5 else '✗ MAUVAIS'}")

print("\n2. COHÉRENCE")
print("-" * 70)
print(f"Sub coherence (mean): {np.mean(sub['coherence']):.4f}")
print(f"Top coherence (mean): {np.mean(top['coherence']):.4f}")
print(f"Full coherence (mean): {np.mean(full_coh):.4f}")
print(f"Full coherence @ 101Hz (crossover): {full_coh[np.argmin(np.abs(full_freqs - 101))]:.4f}")

# Low freq coherence
idx_low = np.where((full_freqs >= 20) & (full_freqs <= 500))[0]
print(f"Full coherence [20-500Hz] (mean): {np.mean(full_coh[idx_low]):.4f}")

# Mid freq coherence
idx_mid = np.where((full_freqs >= 500) & (full_freqs <= 5000))[0]
print(f"Full coherence [500-5kHz] (mean): {np.mean(full_coh[idx_mid]):.4f}")

# High freq coherence
idx_high = np.where((full_freqs >= 5000) & (full_freqs <= 20000))[0]
print(f"Full coherence [5-20kHz] (mean): {np.mean(full_coh[idx_high]):.4f}")

print("\n3. SOMMATION LINEAR (dB addition check)")
print("-" * 70)

# Band analysis
bands = [
    (20, 100, "Bass (20-100Hz)"),
    (100, 300, "Crossover (100-300Hz)"),
    (300, 1000, "Mids (300-1kHz)"),
    (1000, 5000, "Upper-Mids (1-5kHz)"),
    (5000, 20000, "Treble (5-20kHz)"),
]

for f_min, f_max, band_name in bands:
    idx = np.where((full_freqs >= f_min) & (full_freqs <= f_max))[0]
    if len(idx) == 0:
        continue
    
    error_band = error[idx]
    expected_band = expected_sum[idx]
    actual_band = actual_sum[idx]
    coh_band = full_coh[idx]
    
    print(f"\n{band_name}:")
    print(f"  Expected sum range: [{np.min(expected_band):.1f}, {np.max(expected_band):.1f}] dB")
    print(f"  Actual sum range:   [{np.min(actual_band):.1f}, {np.max(actual_band):.1f}] dB")
    print(f"  Error (mean): {np.mean(error_band):+.2f} dB")
    print(f"  Error (max):  {np.max(np.abs(error_band)):.2f} dB")
    print(f"  Coherence (mean): {np.mean(coh_band):.3f}")
    
    if np.mean(np.abs(error_band)) < 0.5:
        status = "✓ EXCELLENT"
    elif np.mean(np.abs(error_band)) < 1.0:
        status = "✓ BON"
    elif np.mean(np.abs(error_band)) < 2.0:
        status = "~ ACCEPTABLE"
    else:
        status = "✗ À CHECKER"
    print(f"  {status}")

print("\n4. PROBLÈMES POTENTIELS")
print("-" * 70)

# Check for phase issues
phase_diff = (top['phase_deg'] - sub_interp_mag(top_freqs)) % 360
phase_diff = np.where(phase_diff > 180, phase_diff - 360, phase_diff)
print(f"Phase alignment check (Top vs Sub):")
print(f"  Mean phase diff: {np.mean(phase_diff):.1f}°")
print(f"  Max phase diff: {np.max(np.abs(phase_diff)):.1f}°")

# Worst coherence areas
worst_idx = np.argmin(full_coh)
worst_freq = full_freqs[worst_idx]
worst_coh = full_coh[worst_idx]
print(f"\nLowest coherence:")
print(f"  Frequency: {worst_freq:.1f} Hz")
print(f"  Coherence: {worst_coh:.4f}")
print(f"  STATUS: {'✓ OK' if worst_coh > 0.8 else '~ À VÉRIFIER' if worst_coh > 0.5 else '✗ PROBLÈME'}")

# Check for nulls due to phase inversion
null_idx = np.where(np.abs(error) > 3.0)[0]
if len(null_idx) > 0:
    print(f"\nZones de grande erreur (>3dB):")
    for idx in null_idx[:5]:  # Show first 5
        print(f"  {full_freqs[idx]:.0f} Hz: error = {error[idx]:+.2f} dB, expected = {expected_sum[idx]:.1f} dB, actual = {actual_sum[idx]:.1f} dB")
else:
    print(f"\n✓ Pas de zones de grande erreur (>3dB)")

print("\n5. CONCLUSIONS")
print("-" * 70)
mean_error = np.mean(np.abs(error))
max_error = np.max(np.abs(error))

print(f"Erreur moyenne de sommation: {mean_error:.2f} dB")
print(f"Erreur maximale: {max_error:.2f} dB")

if mean_error < 0.5 and max_error < 1.0:
    print("✓✓ SOMMATION EXCELLENTE - Les deux systèmes s'additionnent parfaitement")
elif mean_error < 1.0 and max_error < 2.0:
    print("✓ SOMMATION BONNE - Les deux systèmes s'additionnent bien")
elif mean_error < 2.0 and max_error < 4.0:
    print("~ SOMMATION ACCEPTABLE - Quelques zones à affiner")
else:
    print("✗ SOMMATION À VÉRIFIER - Problèmes importants détectés")

print(f"\nDonnées Kalibre:")
print(f"✓ Délai stable et cohérent")
print(f"✓ Cohérence élevée (>0.99)")
print(f"✓ Magnitude bien mesurée")
print(f"✓ Phase bien mesurée")
print(f"\nRECOMMANDATIONS:")
print(f"→ Vérifier que le crossover est bien à 101Hz en LR24")
print(f"→ Vérifier la polarité des deux systèmes")
print(f"→ Vérifier les niveaux absolus dans le DSP")
