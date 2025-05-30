from typing import List

from pydantic import BaseModel, Field, validator, field_validator
from enum import Enum
from config import DEFAULT_OUTPUT_PIN, GPIO_PIN_MIN, GPIO_PIN_MAX

class ModulationType(str, Enum):
    """Tipos de modulación PCM soportados."""
    NRZ_M = "NRZ-M"
    MANCHESTER = "Manchester (Bi-phase L)"
    UNIPOLAR_RZ = "Unipolar RZ"
    BIPOLAR_AMI = "Bipolar AMI"

class ModulateRequest(BaseModel):
    """Modelo para la solicitud de modulación/envío."""
    binary_data: str = Field(
        ...,
        pattern=r"^[01]{5}$",
        title="Mensaje Binario",
        description="Cadena binaria de exactamente 5 dígitos (0 o 1)."
    )
    modulation_type: ModulationType = Field(
        ...,
        title="Tipo de Modulación",
        description="Tipo de modulación PCM a aplicar."
    )
    output_pins: List[int] = Field(
        DEFAULT_OUTPUT_PIN,
        title="Pines GPIO",
        description=f"Lista de pines GPIO (BCM) para la salida."
    )

class GpioStatusResponse(BaseModel):
    """Modelo para la respuesta del estado GPIO."""
    status: str
    detail: str
    gpio_library_functional: bool

class ModulationListResponse(BaseModel):
    """Modelo para la respuesta de la lista de modulaciones."""
    supported_modulations: list[str]

class GpioSendResponse(BaseModel):
    """Modelo para la respuesta del envío GPIO."""
    status: str
    message: str