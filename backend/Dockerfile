# Usa l'immagine di base di Ubuntu
FROM ubuntu:latest

# Aggiorna il sistema e installa le dipendenze necessarie
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    sudo \
    python3.9 \
    python3-distutils \
    python3-pip \
    ffmpeg \
    git

# Aggiorna pip
RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /code

# Copy all content into the working directory
COPY . /code/


RUN pip install gradio==3.50.2 langid faster-whisper whisper-timestamped unidecode eng-to-ipa pypinyin cn2an
RUN pip install -r requirements.txt
RUN pip install soundfile librosa inflect jieba silero
RUN pip install fastapi uvicorn

RUN apt -y install -qq aria2 unzip
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/OpenVoice/resolve/main/checkpoints_1226.zip -d /code -o checkpoints_1226.zip
RUN unzip /code/checkpoints_1226.zip

# Expose port 8000
EXPOSE 8000

# Set the environment variable DATA_DIR
ENV DATA_DIR=/code/data

# Default command to start the application
CMD ["uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]
