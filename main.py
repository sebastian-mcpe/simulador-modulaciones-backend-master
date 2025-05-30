# main.py

import threading
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse
from scalar_fastapi import get_scalar_api_reference
from starlette.middleware.cors import CORSMiddleware

# Módulos locales
from models import ModulateRequest, ModulationType, GpioStatusResponse, ModulationListResponse, GpioSendResponse
from config import GPIO_PIN_MIN, GPIO_PIN_MAX
from signal_generation import generate_original_signal, get_modulation_function
from plotting import create_plot_image
from gpio_handler import send_to_gpio, get_gpio_state, ON_RASPBERRY_PI

# --- Crear la Aplicación FastAPI ---
app = FastAPI(
    title="API Modulador de Señales",
    description="Genera gráficas de señales PCM o las envía a pines GPIO de Raspberry Pi.",
    version="1.1.0"
)

# --- Configurar CORS ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Endpoint para Documentación Scalar ---
@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    """Sirve la interfaz de documentación API de Scalar."""
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title + " - Scalar"
    )


# --- Endpoints de la API ---

@app.post(
    "/modulate/plot",
    response_class=StreamingResponse,
    summary="Generar Gráfica de Señal Modulada",
    tags=["Modulación"],
    responses={
        200: {"content": {"image/png": {}}, "description": "Imagen PNG de la gráfica generada."},
        400: {"description": "Tipo de modulación no soportado"},
        422: {"description": "Error de validación en los datos de entrada"},
        500: {"description": "Error interno del servidor al generar la gráfica"}
    }
)
async def get_modulation_plot(request: ModulateRequest):
    """
    Genera una señal modulada según los parámetros y devuelve una imagen PNG de la gráfica.
    """
    print(f"Solicitud de gráfica: {request.modulation_type.value} para '{request.binary_data}'")
    generate_func = get_modulation_function(request.modulation_type)
    if not generate_func:
        raise HTTPException(status_code=400, detail=f"Tipo de modulación '{request.modulation_type}' no soportado.")

    try:
        t_orig, sig_orig = generate_original_signal(request.binary_data)
        t_mod, sig_mod = generate_func(request.binary_data)
        image_buffer = create_plot_image(t_mod, request.binary_data, sig_mod, request.modulation_type.value)
        return StreamingResponse(image_buffer, media_type="image/png")
    except Exception as e:
        print(f"Error generando gráfica: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al generar la gráfica: {e}")


@app.post(
    "/modulate/send_gpio",
    response_model=GpioSendResponse,
    summary="Enviar Señal Modulada a GPIO",
    tags=["GPIO"],
    responses={
        200: {"description": "Envío a GPIO completado con éxito."},
        400: {"description": "Tipo de modulación no soportado."},
        422: {"description": "Error de validación en los datos de entrada."},
        429: {"description": "GPIO ya está en uso."},
        500: {"description": "Error interno durante el envío a GPIO."},
        501: {"description": "Funcionalidad GPIO no disponible en el servidor."}
    }
)
@app.post(
    "/modulate/send_gpio",
    response_model=GpioSendResponse,
    summary="Enviar Señal Modulada a GPIO",
    tags=["GPIO"],
    responses={
        200: {"description": "Envío a GPIO completado con éxito."},
        400: {"description": "Tipo de modulación no soportado."},
        422: {"description": "Error de validación en los datos de entrada."},
        429: {"description": "GPIO ya está en uso."},
        500: {"description": "Error interno durante el envío a GPIO."},
        501: {"description": "Funcionalidad GPIO no disponible en el servidor."}
    }
)
async def send_modulation_to_gpio_endpoint(request: ModulateRequest):
    """
    Genera una señal modulada **PCM** y la envía a los pines GPIO especificados.
    """
    print(
        f"Solicitud de envío a GPIO: {request.modulation_type.value} para '{request.binary_data}' a pines {request.output_pins}")

    if not ON_RASPBERRY_PI:
        raise HTTPException(status_code=501, detail="Funcionalidad GPIO no disponible en este servidor.")

    generate_func = get_modulation_function(request.modulation_type)
    if not generate_func:
        raise HTTPException(status_code=400, detail=f"Tipo de modulación '{request.modulation_type}' no soportado.")

    try:
        # Generar la señal
        t_mod, sig_mod = generate_func(request.binary_data)

        # Función para enviar a un pin individual
        def send_to_single_pin(pin):
            try:
                send_to_gpio(pin, t_mod, sig_mod)
            except ValueError as e:
                # Entregar errores relacionados con GPIO
                if "GPIO ya está en uso" in str(e):
                    raise HTTPException(status_code=429, detail=f"GPIO {pin} ya está en uso.")
                else:
                    raise HTTPException(status_code=500, detail=f"Error al enviar al GPIO {pin}: {str(e)}")

        # Ejecutar la función para todos los pines
        for pin in request.output_pins:
            if pin < GPIO_PIN_MIN or pin > GPIO_PIN_MAX:
                raise HTTPException(status_code=422,
                                    detail=f"El pin GPIO {pin} está fuera del rango permitido ({GPIO_PIN_MIN}-{GPIO_PIN_MAX}).")
            send_to_single_pin(pin)

        return GpioSendResponse(
            status="completed",
            message=f"Señal {request.modulation_type.value} enviada a los GPIO {request.output_pins}.",
        )

    except HTTPException:
        raise  # Re-throw HTTP-specific exceptions
    except Exception as e:
        print(f"Error preparando envío a GPIO: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno preparando el envío a GPIO: {e}")

@app.get(
    "/modulations",
    response_model=ModulationListResponse,
    summary="Listar Modulaciones Soportadas",
    tags=["Información"]
    )
async def list_modulations():
    """Devuelve la lista de tipos de modulación PCM soportados."""
    # Obtener claves del Enum
    supported = [m.value for m in ModulationType]
    return ModulationListResponse(supported_modulations=supported)


@app.get(
    "/gpio_status",
    response_model=GpioStatusResponse,
    summary="Verificar Estado de GPIO",
    tags=["GPIO"]
    )
async def get_gpio_status_endpoint():
     """Verifica si la funcionalidad GPIO está activa y si está ocupada."""
     state = get_gpio_state()
     if not state["functional"]:
         status = "disabled"
         detail = "Librería GPIO no disponible."
     elif state["busy"]:
          status = "busy"
          detail = f"Actualmente enviando una señal (Bloqueo {'activo' if state['locked'] else 'inactivo'})."
     else:
          status = "idle"
          detail = "GPIO disponible."
     return GpioStatusResponse(status=status, detail=detail, gpio_library_functional=state["functional"])


# --- Ejecutar el Servidor ---
if __name__ == "__main__":
    import uvicorn
    print("\nIniciando servidor FastAPI...")
    print(f" - Funcionalidad GPIO: {'ACTIVA' if ON_RASPBERRY_PI else 'DESACTIVADA'}")
    print(" - Documentación interactiva: http://127.0.0.1:8000/scalar")
    print(" - Acceso local: http://127.0.0.1:8000/")
    print("   (Para acceso desde otros dispositivos, usa la IP de tu Raspberry Pi)")

    # Escuchar en 0.0.0.0 para acceso externo
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # reload=True para desarrollo