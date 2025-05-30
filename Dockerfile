# Usar una imagen base de Python
FROM python:3.12-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY requirements.txt ./

# Instalar Git
RUN apt-get update && apt-get install -y git && apt-get clean

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación
COPY . .

ENV APP_ENV=development
ENV APP_PORT=8000

# Exponer el puerto en el que corre la aplicación (ajustar si es necesario)
EXPOSE 8000

# Comando para ejecutar la aplicación (ajustar según tu aplicación)
CMD ["python", "main.py"]
