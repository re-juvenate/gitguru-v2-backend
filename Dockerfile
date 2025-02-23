# FROM python:3.13-alpine3.21
# RUN apk update && \
#     apk add --no-cache wget unzip build-base swig python3-dev py3 && \
#     rm -rf /var/cache/apk/*

FROM python:3.13-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget unzip build-essential python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# pmd
RUN wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.10.0/pmd-dist-7.10.0-bin.zip && \
    unzip pmd-dist-7.10.0-bin.zip && \
    rm pmd-dist-7.10.0-bin.zip
ENV PATH="/app/pmd-bin-7.10.0/bin:${PATH}"
RUN echo 'alias pmd="pmd"' >> ~/.bashrc

# # mega-linter-runner
# RUN npm install pnpm -g
# RUN npm install mega-linter-runner -g --save-dev

# semgrep (installed by poetry)
# RUN pip install --no-cache-dir semgrep

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock README.md /app/
COPY src /app/src
RUN poetry install

WORKDIR /app/src
EXPOSE 5555
# CMD ["gunicorn","-w", "4", "-k", "uvicorn.workers.UvicornWorker main:app", "--bind", "0.0.0.0:5555"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]