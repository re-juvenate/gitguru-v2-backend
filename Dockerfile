FROM python:3.13-slim

RUN apt update && apt install -y git curl build-essential cmake npm
RUN rm -rf /var/lib/apt/lists/*
RUN apt autoremove -y && apt-get clean -y

# RUN npm install pnpm -g
# RUN npm install mega-linter-runner -g --save-dev

RUN pip install --no-cache-dir semgrep
RUN pip install poetry

WORKDIR /app

# Verify installations
RUN semgrep --version && \
    python -c "import llama_cpp; print(llama_cpp.__version__)" && \
    mega-linter-runner --version

COPY . /app/
RUN poetry install

EXPOSE 5555
CMD ["gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:5555"]