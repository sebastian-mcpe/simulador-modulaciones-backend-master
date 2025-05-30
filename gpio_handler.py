import time
import threading
import contextlib
import numpy as np
from config import SAMPLES_PER_BIT, BIT_DURATION  # Necesitamos SAMPLES_PER_BIT

# --- Intentar importar la librería GPIO ---
try:
    import RPi.GPIO as GPIO
    ON_RASPBERRY_PI = True
    print("INFO: Librería RPi.GPIO cargada.")
    # No hacer setmode global aquí, hacerlo por request/función
except (ImportError, RuntimeError, Exception) as e:
    print(f"ADVERTENCIA: Librería RPi.GPIO no disponible o error: {e}")
    ON_RASPBERRY_PI = False
    GPIO = None

# --- Estado Global y Bloqueo para GPIO ---
gpio_lock = threading.Lock()
is_gpio_sending = False

def get_gpio_state():
    """Devuelve el estado actual del handler GPIO."""
    return {
        "functional": ON_RASPBERRY_PI,
        "busy": is_gpio_sending,
        "locked": gpio_lock.locked()
    }

def send_to_gpio(output_pin: int, t: np.ndarray, modulated_signal: np.ndarray):
    """
    Envía la señal modulada DIGITAL a un pin GPIO específico.
    Esta función es BLOQUEANTE mientras dura el envío.
    Utiliza RPi.GPIO. Lanza ValueError en caso de error o si GPIO no está disponible/ocupado.
    """
    global is_gpio_sending # Necesitamos modificar el estado global

    if not ON_RASPBERRY_PI or GPIO is None:
        print("ERROR Interno: Intento de enviar a GPIO sin librería disponible.")
        raise ValueError("Funcionalidad GPIO no disponible en el servidor.")

    # Adquirir bloqueo (no bloqueante, falla rápido si está ocupado)
    if not gpio_lock.acquire(blocking=False):
        raise ValueError("GPIO ya está en uso enviando otra señal.")

    # Marcar como ocupado DESPUÉS de adquirir el bloqueo
    is_gpio_sending = True
    print(f"--- [GPIO TASK] Bloqueo adquirido. Iniciando envío a GPIO Pin {output_pin} ---")

    error_occurred = None
    try:
        # Configurar GPIO DENTRO de la función
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False) # Podría estar fuera si se hace una sola vez al inicio
        GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.LOW)
        print(f"GPIO {output_pin} configurado como salida.")

        samples_per_bit_eff = max(1, SAMPLES_PER_BIT)
        sample_duration = BIT_DURATION / samples_per_bit_eff
        print(f"Duración por muestra: {sample_duration:.6f}s")

        start_time = time.perf_counter()
        for i in range(len(modulated_signal)):
            level = modulated_signal[i]
            gpio_state = GPIO.HIGH if level > 0 else GPIO.LOW
            GPIO.output(output_pin, gpio_state)
            wait_until = start_time + (i + 1) * sample_duration
            while time.perf_counter() < wait_until:
                 if wait_until - time.perf_counter() > 0.0001:
                    time.sleep(0.00005)
                 pass # Espera activa

        GPIO.output(output_pin, GPIO.LOW)
        print(f"--- [GPIO TASK] Envío a GPIO Pin {output_pin} completado ---")

    except Exception as e:
        print(f"Error durante el envío a GPIO {output_pin}: {e}")
        error_occurred = e # Guardar error
    finally:
        print(f"Limpiando GPIO Pin {output_pin}...")
        with contextlib.suppress(Exception):
             GPIO.cleanup(output_pin) # Limpiar solo el pin usado
        is_gpio_sending = False # Marcar como no ocupado ANTES de liberar bloqueo
        gpio_lock.release()     # SIEMPRE liberar el bloqueo
        print(f"Bloqueo GPIO liberado para pin {output_pin}.")
        # Si ocurrió un error, lanzarlo
        if error_occurred:
            # Usar un tipo de error genérico o específico si se prefiere
            raise ValueError(f"Error de GPIO en pin {output_pin}: {error_occurred}")