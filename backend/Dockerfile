# Start with a base image that has miniconda installed
FROM continuumio/miniconda3 as builder

# Update Conda and install mamba in the base environment
RUN conda update -n base -c defaults conda && \
    conda install mamba -n base -c conda-forge

# Create a new environment for the application
RUN mamba create -n youtube-auto-dub python=3.9 -y

# Activate the created environment
SHELL ["conda", "run", "-n", "youtube-auto-dub", "/bin/bash", "-c"]

# Install PyTorch and other dependencies
RUN mamba install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.7 -c pytorch -c nvidia -y

# Set the working directory
WORKDIR /code

# Copy the project files to the container
COPY . /code/

# Install necessary system packages
RUN apt-get update && apt-get install -y aria2 unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Download and unzip the checkpoints
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://myshell-public-repo-hosting.s3.amazonaws.com/checkpoints_1226.zip -d /code -o checkpoints_1226.zip && \
    unzip /code/checkpoints_1226.zip -d /code/checkpoints && \
    rm /code/checkpoints_1226.zip

COPY requirements.txt /code/

# Install Python dependencies
RUN pip install -r requirements.txt && \
    pip install pytube moviepy fastapi uvicorn loguru youtube-dl youtube-transcript-api librosa googletrans==4.0.0-rc1


# Expose the port the app runs on
EXPOSE 8080

# Set the environment variable
ENV DATA_DIR=/code/data


CMD ["conda", "run", "-n", "youtube-auto-dub", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
