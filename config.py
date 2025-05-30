# --- Parámetros Comunes ---
BIT_DURATION: float = 0.1  # Duración de bit por defecto en segundos
SAMPLES_PER_BIT: int = 100
VOLTAGE_HIGH: int = 1  # Nivel lógico/voltaje para '1' en algunas modulaciones
VOLTAGE_LOW_BIPOLAR: int = -1  # Nivel bajo para señales bipolares
VOLTAGE_LOW_UNIPOLAR: int = 0  # Nivel bajo/cero para señales unipolares

# --- Pin GPIO de Salida ---
DEFAULT_OUTPUT_PIN: int = 17
GPIO_PIN_MIN: int = 2
GPIO_PIN_MAX: int = 27

GPIO_CONSUMER_NAME: str = "ModuladorFastAPI"