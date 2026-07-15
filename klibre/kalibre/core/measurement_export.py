"""Export measurements to JSON format for analysis."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np


def serialize_measurement(measurement) -> dict:
    """Convert a ChannelMeasurement to a JSON-serializable dict."""
    return {
        "name": measurement.name,
        "processor_out": measurement.processor_out,
        "absolute_delay_ms": float(measurement.absolute_delay_ms),
        "mic_position": measurement.mic_position,
        "is_reference": measurement.is_reference,
        "ir_time_ms": measurement.ir_time_ms.tolist() if measurement.ir_time_ms is not None else None,
        "ir": measurement.ir.tolist() if measurement.ir is not None else None,
        "freqs": measurement.freqs.tolist() if measurement.freqs is not None else None,
        "magnitude_db_rel": measurement.magnitude_db_rel.tolist() if measurement.magnitude_db_rel is not None else None,
        "coherence": measurement.coherence.tolist() if measurement.coherence is not None else None,
        "phase_deg": measurement.phase_deg.tolist() if measurement.phase_deg is not None else None,
        "curve_color": measurement.curve_color,
        "visible": measurement.visible,
    }


def export_measurement_to_json(measurement, output_dir: str | Path = None) -> str:
    """
    Save a single measurement to a JSON file.
    
    Args:
        measurement: ChannelMeasurement object
        output_dir: Directory to save in. If None, uses ./measurements/
    
    Returns:
        Path to saved file
    """
    if output_dir is None:
        output_dir = Path("./measurements")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = measurement.name.replace(" ", "_").replace("/", "-").replace("\\", "-")
    filename = f"measurement_{safe_name}_{timestamp}.json"
    filepath = output_dir / filename
    
    # Serialize and save
    data = serialize_measurement(measurement)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def export_all_measurements_to_json(measurements: list, output_dir: str | Path = None) -> str:
    """
    Save all measurements to a single JSON file.
    
    Args:
        measurements: List of ChannelMeasurement objects
        output_dir: Directory to save in. If None, uses ./measurements/
    
    Returns:
        Path to saved file
    """
    if output_dir is None:
        output_dir = Path("./measurements")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"measurements_export_{timestamp}.json"
    filepath = output_dir / filename
    
    # Serialize all
    data = {
        "export_timestamp": datetime.now().isoformat(),
        "total_measurements": len(measurements),
        "measurements": [serialize_measurement(m) for m in measurements],
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)
