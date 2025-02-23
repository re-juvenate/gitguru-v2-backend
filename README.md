# GitGuru V2 Backend

GitGuru V2 Backend is a FastAPI-based backend service designed to provide various functionalities such as repository analysis, issue summarization, and chat interactions. The service integrates with GitHub and other tools to offer a comprehensive solution for managing and analyzing repositories.

## Features

- **Repository Analysis**: Analyze the structure, README, languages, and documentation of a GitHub repository.
- **Issue Summarization**: Summarize issues and their comments from a GitHub repository.
- **Chat Interactions**: Provide chat-based interactions for various tasks.
- **Instructions and Fixes**: Generate instructions and fixes based on repository data and conversations.

## Architecture

The architecture of GitGuru V2 Backend is modular, with different components handling specific tasks. The main components are:

- **FastAPI**: The web framework used to build the API.
- **Docker**: Used to containerize the application.
- **GitHub Integration**: Fetches data from GitHub repositories.
- **PMD**: Linter for analyzing Java code.
- **SearxNG**: Search engine integration.
- **Ollama**: Language model integration.

## Workflow

1. **Repository Analysis**:
    - Fetch repository data from GitHub.
    - Analyze the structure, README, languages, and documentation.
    - Generate a summary of the repository.

2. **Issue Summarization**:
    - Fetch issue data and comments from GitHub.
    - Summarize the issue and its comments.

3. **Chat Interactions**:
    - Provide chat-based interactions for various tasks.
    - Use language models to generate responses.

4. **Instructions and Fixes**:
    - Generate instructions and fixes based on repository data and conversations.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- GitHub Personal Access Token (PAT) with `write:packages`, `read:packages`, and `delete:packages` scopes.

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/re-juvenate/gitguru-v2-backend.git
    cd gitguru-v2-backend
    ```

2. Create a [.env](http://_vscodecontentref_/1) file based on the [.env.example](http://_vscodecontentref_/2) file and fill in the required values:

    ```sh
    cp .env.example .env
    ```

3. Build and run the Docker containers:

    ```sh
    docker-compose up --build
    ```

### Usage

The API will be available at `.`http://localhost:5555 You can interact with the API using tools like `curl`, Postman, or any other HTTP client.

### Endpoints

- **POST /sum-repo**: Summarize a repository.
- **POST /sum-issue**: Summarize an issue.
- **POST /fixes**: Generate fixes for a repository.
- **POST /instructions**: Generate instructions for a repository.
- **POST /chat**: Chat-based interactions.

### Example Request

```sh
curl -X POST "http://localhost:5555/sum-repo" -H "Content-Type: application/json" -d '{
  "url": "https://github.com/owner/repo",
  "type": "repo",
  "conversations": [
    {
      "message": "Please summarize this repository.",
      "timestamp": "2025-02-23T12:34:56",
      "role": "user"
    }
  ]
}'
```

## Development

### Running Locally

1. Install dependencies:

    ```sh
    poetry install
    ```

2. Run the application:

    ```sh
    uvicorn src.main:app --reload
    ```

