import matplotlib

matplotlib.use('Agg')  # Configurar backend antes de importar pyplot
import matplotlib.pyplot as plt
import numpy as np
import io
from config import VOLTAGE_HIGH, VOLTAGE_LOW_BIPOLAR, VOLTAGE_LOW_UNIPOLAR, BIT_DURATION


def create_plot_image(t, original_signal, modulated_signal, title):
    """Genera la gráfica (solo de la Señal Modulada) y la devuelve como bytes PNG."""
    # Color primario para la señal y color complementario para cuadrícula
    primary_color = '#2563EB'  # Azul primario para la línea de la señal
    grid_color = '#93C5FD'  # Azul más claro para la cuadrícula y líneas verticales

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.suptitle(f'Modulación: {title}', fontsize=16)

    # Graficar señal modulada con el color primario y grosor ajustado
    ax.step(t, modulated_signal, where='post', color=primary_color, linewidth=2)

    # Configurar etiquetas del gráfico
    ax.set_xlabel('Tiempo (segundos)')
    ax.set_ylabel('Amplitud')

    # Calcular límites Y basados en los posibles voltajes y la señal
    min_val = min(VOLTAGE_LOW_BIPOLAR, VOLTAGE_LOW_UNIPOLAR, np.min(modulated_signal)) if len(
        modulated_signal) > 0 else VOLTAGE_LOW_BIPOLAR
    max_val = max(VOLTAGE_HIGH, np.max(modulated_signal)) if len(modulated_signal) > 0 else VOLTAGE_HIGH
    ax.set_ylim(min_val - 0.2, max_val + 0.2)

    # Agregar cuadricula
    ax.grid(True, color=grid_color, linestyle='--', linewidth=0.6, alpha=0.7)

    # Añadir líneas verticales para marcar los límites de los bits con un tono más claro
    num_bits = int(round(t[-1] / BIT_DURATION)) if BIT_DURATION > 0 and len(t) > 0 else 0
    for i in range(num_bits + 1):
        ax.axvline(i * BIT_DURATION, color=grid_color, linestyle='--', lw=0.8)

    # Colocar los bits enviados como etiquetas centradas en el eje X
    tick_positions = []
    tick_labels = []
    for i in range(num_bits):  # Crear etiquetas para cada bit
        # Calcular posición del tick
        tick_positions.append((i + 0.5) * BIT_DURATION)
        # Validar longitud de original_signal antes de usarlo
        if i < len(original_signal):
            # Convertir el valor del bit a entero si es necesario, luego a string
            bit_value = int(original_signal[i])
            tick_labels.append(str(bit_value))
        else:
            # Etiqueta de error si no hay suficientes bits en original_signal
            tick_labels.append('?')

    # Aplicar etiquetas personalizadas en el eje X
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Guardar en buffer de memoria
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)  # Importante para liberar memoria
    buf.seek(0)
    return buf