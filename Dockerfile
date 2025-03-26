# Imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia todo el contenido del repo al contenedor
COPY . /app

# Instala las dependencias
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expone el puerto que usará Flask
EXPOSE 8000

# Comando para iniciar tu bot
CMD ["python", "webhook_server.py"]
