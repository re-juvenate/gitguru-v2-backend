import docker
import shutil
import os

def clone_and_lint(repo_url: str, linter_config_path: str = './src/linter/.mega-linter.yml'):
    # Use a 'temp' directory in the same directory as the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(current_dir, 'temp')
    lint_errors_file = os.path.join(temp_dir, 'lint_errors.txt')

    try:
        # Ensure the temp directory exists
        os.makedirs(temp_dir, exist_ok=True)

        # Clone the repository
        clone_cmd = ["git", "clone", repo_url, temp_dir]
        clone_process = os.system(' '.join(clone_cmd))
        
        if clone_process != 0:
            raise Exception("Error cloning repository")
        
        # Copy .mega-linter.yml file into the cloned repository
        shutil.copy(linter_config_path, temp_dir)
        
        # Initialize Docker client
        client = docker.from_env()
        
        # Run MegaLinter container
        container = client.containers.run(
            "oxsecurity/megalinter/flavors/formatters:v8",
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
        # return lint_errors_file
        return logs
    
    except docker.errors.ContainerError as e:
        raise Exception(f"Error running MegaLinter: {str(e)}")
    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir)


# Example usage
repo_url = "https://github.com/ankitprasad2005/chess_err_hexa"
lint_errors_file_path = clone_and_lint(repo_url)
print(f"Linting errors saved to: {lint_errors_file_path}")
