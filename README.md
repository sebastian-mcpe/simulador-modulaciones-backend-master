# Simulador de Modulaciones Digitales - Backend

Este proyecto proporciona una API para la simulación y generación de señales digitalizadas, incluyendo la visualización de gráficas, integración con Pines GPIO en Raspberry Pi, y la aplicación de distintos esquemas de modulación PCM (NRZ-M, Manchester, Unipolar RZ, Bipolar AMI). Es el backend para un sistema de simulación de modulaciones digitales.

---

## Instalación

### 1. **Requisitos previos**
   - Python 3.11 o superior.
   - `pip` (administrador de paquetes).
   - Para Pines GPIO: Una Raspberry Pi con el paquete `RPi.GPIO`.

### 2. **Clonar el repositorio**

   ```bash
   git clone https://github.com/usuario/simulador-modulaciones-backend.git
   cd simulador-modulaciones-backend
   ```

### 3. **Crear y activar un entorno virtual (opcional pero recomendado)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   ```

### 4. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

### 5. **Configurar variables de entorno**

   Crear un archivo `.env` en la raíz del proyecto con la siguiente estructura:

   ```env
   APP_ENV=development
   APP_PORT=8000
   ```

   Nota: Modifica según lo requiera tu despliegue.

### 6. **Ejecutar el servidor**

   ```bash
   uvicorn main:app --reload
   ```

### 7. **Acceder a la API**

   Una vez iniciado el servidor, la API estará disponible en:  
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para la documentación de Swagger.

---

## Personalización

### Configuraciones globales

El archivo `config.py` agrupa las configuraciones claves del sistema:

- **Duración del Bit (`BIT_DURATION`)**:
    - Ajusta la duración de un bit en la señal modulada.
    - Valor actual (por defecto): `0.1` segundos.

- **Muestras por Bit (`SAMPLES_PER_BIT`)**:
    - Define la granularidad del muestreo para las señales.
    - Valor actual: `100` muestras por bit.

- **Voltajes (`VOLTAGE_HIGH`, `VOLTAGE_LOW_BIPOLAR`, `VOLTAGE_LOW_UNIPOLAR`)**:
    - Valores de los niveles de voltaje alto y bajo para las distintas modulaciones.
    - Ejemplo:
      - Voltaje alto: `1`.
      - Voltaje bajo (bipolar): `-1`.
      - Voltaje bajo (unipolar): `0`.

- **Configuraciones GPIO**:
    - Pin por defecto (`DEFAULT_OUTPUT_PIN`): `17`.
    - Rango permitido de pines: `2` a `27`.

Para cambiar estas configuraciones, edita el archivo `config.py`.

---

## Estructura Principal de la Aplicación

### **`main.py`**
El archivo principal del proyecto. Configura y ejecuta el servidor FastAPI, incluyendo las rutas, middleware y documentación.

- **Responsabilidades**:
    - Inicia la aplicación FastAPI.
    - Define las rutas principales.
    - Integra Cross-Origin Resource Sharing (CORS) para permitir solicitudes entre dominios (frontend-backend).

#### Rutas principales:
| Ruta             | Método   | Función asociada                          | Descripción                                  |
|-------------------|----------|------------------------------------------|----------------------------------------------|
| `/`              | GET      | `scalar_html`                            | Devuelve la página base estática.            |
| `/api/modulations` | GET    | `list_modulations`                       | Lista los tipos de modulación soportados.    |
| `/api/modulation` | POST    | `send_modulation_to_gpio_endpoint`       | Aplica una modulación y la envía por GPIO.   |
| `/api/graph`      | POST    | `get_modulation_plot`                    | Devuelve una gráfica de la señal modulada.   |
| `/api/gpio/status` | GET    | `get_gpio_status_endpoint`               | Devuelve el estado de la librería GPIO.      |

#### Manejo de errores:
Rutas no definidas devuelven un error HTTP `404` estándar.

---

### **Gestión de datos e interacciones**

1. **Modelos (`models.py`)**

Define los modelos y validaciones de datos con Pydantic:

- **`ModulateRequest`**:
    - Datos requeridos para realizar una modulación:
      - `binary_data`: Cadena de bits (0s y 1s).
      - `modulation_type`: Tipo de modulación PCM a aplicar.
      - `output_pins`: Lista de pines GPIO para la salida.

- **`GpioStatusResponse`**:
    - Respuesta que indica el estado funcional del sistema GPIO.

- **`ModulationListResponse`**:
    - Devuelve los tipos de modulación soportados.

- **`GpioSendResponse`**:
    - Resultado de una operación de envío GPIO (éxito o error).

---

## Flujo de Datos y Navegación del Usuario

1. **Solicitud del cliente** (frontend):
    - El usuario inicia configuraciones usando rutas relevantes para seleccionar tipo de modulación, ingresar mensaje binario, etc.

2. **Procesamiento backend**:
    - La API recibe las configuraciones mediante el modelo `ModulateRequest`.
    - Genera señales usando las funciones especificadas en `signal_generation.py`.
    - Si el hardware GPIO está disponible, la señal es enviada por los pines configurados.

3. **Gráficas y retroalimentación**:
    - Gráficas de la señal modulada se generan con `matplotlib` y son devueltas como imágenes al cliente.

4. **Resultados**:
    - El cliente usa las gráficas y estados GPIO como retroalimentación.

---

## Beneficios de la arquitectura

1. **Separación de responsabilidades**:
    - Cada módulo maneja aspectos específicos (API, señales, GPIO, gráficas).

2. **Escalabilidad**:
    - Es fácil agregar nuevos tipos de modulación o endpoints.

3. **Portabilidad**:
    - A excepción del manejo GPIO, el resto del backend puede ejecutarse en cualquier máquina compatible con Python.

4. **Interactividad mejorada**:
    - Devuelve gráficas generadas dinámicamente para retroalimentación instantánea.

---

## Módulos Detallados

### **1. Módulo: Generación de Señales (`signal_generation.py`)**

#### Funciones principales:
1. **`generate_original_signal`**
    - Crea un vector temporal para representar el mensaje binario original.
   
2. **`generate_nrzm`**
    - Genera una señal *NRZ-M*.
   
3. **`generate_manchester`**
    - Genera una señal *Manchester (Bi-phase L)*.

4. **`generate_unipolar_rz`**
    - Genera una señal *Unipolar RZ*.

5. **`generate_bipolar_ami`**
    - Genera una señal *Bipolar AMI*.

---

### **2. Módulo: Manejo GPIO (`gpio_handler.py`)**

#### Responsabilidades:
1. **Estado GPIO (`get_gpio_state`)**:
    - Verifica si GPIO está ocupado o en uso.

2. **Envío de Señal (`send_to_gpio`)**:
    - Envía la señal modulada a un pin GPIO específico.

---

### **3. Módulo: Gráficas de Modulación (`plotting.py`)**

#### Funciones principales:
1. **`create_plot_image`**:
    - Genera gráficas representativas de la señal modulada con tiempo y amplitud.

---

## Pantallas o Módulos Principales

### 1. Endpoint `/api/modulations` - Listado de modulaciones

- **Propósito**: Devuelve los tipos de modulación soportados por el sistema.
- **Método**: `GET`.
- **Respuesta**:
```json
{
    "supported_modulations": ["NRZ-M", "Manchester", "Unipolar RZ", "Bipolar AMI"]
}
```

---

### 2. Endpoint `/api/modulation` - Generar y Enviar Señal

- **Propósito**: Aplicar modulación y enviar la señal a través de GPIO.
- **Método**: `POST`.
- **Parámetros esperados**:
```json
{
    "binary_data": "11001",
    "modulation_type": "NRZ-M",
    "output_pins": [17]
}
```
- **Respuesta**:
    - En caso de éxito:
    ```json
    {
        "status": "success",
        "message": "Señal enviada correctamente."
    }
    ```
    - En caso de error:
    ```json
    {
        "status": "error",
        "message": "Error en el pin GPIO."
    }
    ```

---

### 3. Endpoint `/api/graph` - Generar gráfica

- **Propósito**: Devuelve la representación gráfica de una señal modulada.
- **Método**: `POST`.
- **Parámetros esperados**:
```json
{
    "binary_data": "11001",
    "modulation_type": "Manchester"
}
```
- **Respuesta**: Imágenes en formato `PNG` generadas dinámicamente.

---

### 4. Endpoint `/api/gpio/status` - Estado GPIO

- **Propósito**: Indica si el sistema GPIO está funcional.
- **Método**: `GET`.
- **Respuesta**:
```json
{
    "status": "ready",
    "detail": "GPIO funcional.",
    "gpio_library_functional": true
}
```

---

## Estado Actual y Futuro del Proyecto

### **Estado Actual**
- Módulos funcionales:
    - Listado de modulaciones.
    - Generación de señales.
    - Uso básico de GPIO.

### **Mejoras Futuras**
- Agregar más tipos de modulaciones digitales.
- Mejorar manejo de errores y logs.
- Soporte para sistemas no Raspberry Pi.

---