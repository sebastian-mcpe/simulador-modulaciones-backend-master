import numpy as np
from config import SAMPLES_PER_BIT, VOLTAGE_HIGH, VOLTAGE_LOW_BIPOLAR, VOLTAGE_LOW_UNIPOLAR, BIT_DURATION
from models import ModulationType # Importar Enum para el mapeo

def generate_original_signal(binary_data: str):
    """Genera la representación de la señal binaria original (niveles 0 y 1)."""
    samples_per_bit_eff = max(1, SAMPLES_PER_BIT)
    total_samples = len(binary_data) * samples_per_bit_eff
    t = np.linspace(0, len(binary_data) * BIT_DURATION, total_samples, endpoint=False)
    signal = np.array([int(bit) for bit in binary_data])
    original_signal = np.repeat(signal, samples_per_bit_eff)
    original_signal = np.resize(original_signal, t.shape)
    return t, original_signal

def generate_nrzm(binary_data: str):
    """Genera la señal modulada NRZ-M."""
    t, _ = generate_original_signal(binary_data)
    modulated_signal = np.zeros_like(t)
    current_level = VOLTAGE_LOW_BIPOLAR
    samples_per_bit_eff = max(1, SAMPLES_PER_BIT)
    for i, bit in enumerate(binary_data):
        start_index = i * samples_per_bit_eff
        end_index = min((i + 1) * samples_per_bit_eff, len(modulated_signal))
        if bit == '1':
            current_level *= -1
        modulated_signal[start_index:end_index] = current_level
    return t, modulated_signal

def generate_manchester(binary_data: str):
    """Genera la señal modulada Manchester (Bi-phase L)."""
    t, _ = generate_original_signal(binary_data)
    modulated_signal = np.zeros_like(t)
    samples_per_bit_eff = max(1, SAMPLES_PER_BIT)
    for i, bit in enumerate(binary_data):
        start_index = i * samples_per_bit_eff
        mid_index = min(start_index + samples_per_bit_eff // 2, len(modulated_signal))
        end_index = min((i + 1) * samples_per_bit_eff, len(modulated_signal))
        if bit == '0':
            modulated_signal[start_index:mid_index] = VOLTAGE_HIGH
            modulated_signal[mid_index:end_index] = VOLTAGE_LOW_BIPOLAR
        else:
            modulated_signal[start_index:mid_index] = VOLTAGE_LOW_BIPOLAR
            modulated_signal[mid_index:end_index] = VOLTAGE_HIGH
    return t, modulated_signal

def generate_unipolar_rz(binary_data: str):
    """Genera la señal modulada Unipolar RZ."""
    t, _ = generate_original_signal(binary_data)
    modulated_signal = np.zeros_like(t)
    samples_per_bit_eff = max(1, SAMPLES_PER_BIT)
    for i, bit in enumerate(binary_data):
        start_index = i * samples_per_bit_eff
        mid_index = min(start_index + samples_per_bit_eff // 2, len(modulated_signal))
        end_index = min((i + 1) * samples_per_bit_eff, len(modulated_signal))
        if bit == '1':
            modulated_signal[start_index:mid_index] = VOLTAGE_HIGH
            modulated_signal[mid_index:end_index] = VOLTAGE_LOW_UNIPOLAR
        else:
            modulated_signal[start_index:end_index] = VOLTAGE_LOW_UNIPOLAR
    return t, modulated_signal

def generate_bipolar_ami(binary_data: str):
    """Genera la señal modulada Bipolar AMI."""
    t, _ = generate_original_signal(binary_data)
    modulated_signal = np.zeros_like(t)
    last_pulse_polarity = VOLTAGE_LOW_BIPOLAR
    samples_per_bit_eff = max(1, SAMPLES_PER_BIT)
    for i, bit in enumerate(binary_data):
        start_index = i * samples_per_bit_eff
        end_index = min((i + 1) * samples_per_bit_eff, len(modulated_signal))
        if bit == '1':
            current_pulse_polarity = -last_pulse_polarity
            modulated_signal[start_index:end_index] = current_pulse_polarity
            last_pulse_polarity = current_pulse_polarity
        else:
            modulated_signal[start_index:end_index] = VOLTAGE_LOW_UNIPOLAR
    return t, modulated_signal

# --- Mapeo de nombres a funciones ---
# Usar el Enum importado de models.py
modulation_functions = {
    ModulationType.NRZ_M: generate_nrzm,
    ModulationType.MANCHESTER: generate_manchester,
    ModulationType.UNIPOLAR_RZ: generate_unipolar_rz,
    ModulationType.BIPOLAR_AMI: generate_bipolar_ami,
    # Añade aquí otras funciones de generación si las creas
}

def get_modulation_function(mod_type: ModulationType):
    """Devuelve la función de generación correspondiente al tipo."""
    return modulation_functions.get(mod_type)