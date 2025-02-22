from fastapi import FastAPI, HTTPException
import docker
import tempfile
import shutil
import os

linter = FastAPI()

@linter.post("/lint")
async def clone_and_lint(repo_url: str):
    # Create a temporary directory to clone the repo
    temp_dir = tempfile.mkdtemp()
    lint_errors_file = os.path.join(temp_dir, 'lint_errors.txt')
    mega_linter_config_path = './.mega-linter.yml'

    try:
        # Clone the repository
        clone_cmd = ["git", "clone", repo_url, temp_dir]
        clone_process = os.system(' '.join(clone_cmd))
        
        if clone_process != 0:
            raise HTTPException(status_code=400, detail="Error cloning repository")
        
        # Copy .mega-linter.yml file into the cloned repository
        shutil.copy(mega_linter_config_path, temp_dir)
        
        # Initialize Docker client
        client = docker.from_env()
        
        # Run MegaLinter container
        container = client.containers.run(
            "oxsecurity/megalinter:v8",
            volumes={
                temp_dir: {'bind': '/tmp/lint', 'mode': 'rw'},
                '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}
            },
            environment={
                "MEGALINTER_CLI_LINTERS_FILE": "/tmp/lint/.mega-linter.yml"
            },
            detach=True
        )
        
        # Wait for the container to finish and get the logs
        container.wait()
        logs = container.logs().decode("utf-8")
        
        # Remove the container
        container.remove()
        
        # Write the linting output to a file
        with open(lint_errors_file, 'w') as file:
            file.write(logs)
        
        # Return the path to the linting errors file
        return {"linting_errors_file": lint_errors_file}
    
    except docker.errors.ContainerError as e:
        raise HTTPException(status_code=400, detail=f"Error running MegaLinter: {str(e)}")
    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir)

# Run the app with: uvicorn myapp:app --reload
