FROM python:3.11-slim

RUN apt-get update && apt-get install -y git curl build-essential cmake
RUN rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir llama-cpp-python mega-linter-runner semgrep

WORKDIR /app

# Verify installations
RUN semgrep --version && \
    python -c "import llama_cpp; print(llama_cpp.__version__)" && \
    mega-linter-runner --version

CMD ["bash"]