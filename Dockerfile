FROM python:3.10

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies for dlib, pyaudio, opencv
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    portaudio19-dev \
    python3-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run app
CMD ["python", "main.py"]
