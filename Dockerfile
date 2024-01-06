# Usa un'immagine di base ufficiale Python.
FROM python:3.9-slim

# Imposta la directory di lavoro all'interno del container.
WORKDIR /app

# Copia i file necessari per l'applicazione nel container.
COPY requirements.txt ./
COPY app.py ./

# Installa le dipendenze.
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta su cui l'applicazione sarà accessibile.
EXPOSE 8080

# Comando per eseguire l'applicazione.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
