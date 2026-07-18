FROM python:3.10-slim

# Install Wine (Windows emulation framework) natively
RUN apt-get update && apt-get install -y \
    wine \
    wine64 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Execute Streamlit inside the virtual frame buffer
CMD ["xvfb-run", "--server-args=-screen 0 1024x768x24", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
