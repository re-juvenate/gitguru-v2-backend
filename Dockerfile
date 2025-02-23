FROM python:3.13-alpine3.21

RUN apk update && \
    apk add --no-cache wget unzip && \
    rm -rf /var/cache/apk/*


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
WORKDIR /app
COPY . /app/
RUN poetry install

# Verify installations
RUN semgrep --version
    # python -c "import llama_cpp; print(llama_cpp.__version__)" && \
    # mega-linter-runner --version

EXPOSE 5555
CMD ["gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:5555"]