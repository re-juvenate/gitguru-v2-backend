FROM python:3.11-slim

RUN apt-get update && apt-get install -y git curl build-essential cmake npm
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get autoremove -y && apt-get clean -y

RUN npm install pnpm -g
RUN npm install mega-linter-runner -g --save-dev

RUN pip install --no-cache-dir llama-cpp-python semgrep

WORKDIR /app

# Verify installations
RUN semgrep --version && \
    python -c "import llama_cpp; print(llama_cpp.__version__)" && \
    mega-linter-runner --version

CMD ["bash"]