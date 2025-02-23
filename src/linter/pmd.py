import os
import tempfile
import subprocess
import docker

def clone_repo_to_temp(repo_url):
    temp_dir = tempfile.mkdtemp()
    print(f"Cloning repository into temporary directory: {temp_dir}")
    try:
        subprocess.run(['git', 'clone', repo_url, temp_dir], check=True)
        print(f"Repository cloned successfully.")
    except subprocess.CalledProcessError as e:
        os.rmdir(temp_dir)
        raise RuntimeError(f"Failed to clone repository: {e}")
    return temp_dir

def generate_pmd_ruleset(ruleset_path):
    ruleset_content = """<?xml version="1.0"?>
<ruleset name="Custom Ruleset"
    xmlns="http://pmd.sourceforge.net/ruleset/2.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://pmd.sourceforge.net/ruleset/2.0.0 https://pmd.sourceforge.io/ruleset_2_0_0.xsd">
    <description>Custom PMD ruleset for linting</description>
    <rule ref="category/java/bestpractices.xml"/>
    <rule ref="category/java/codestyle.xml"/>
    <rule ref="category/java/design.xml"/>
    <rule ref="category/java/documentation.xml"/>
    <rule ref="category/java/errorprone.xml"/>
    <rule ref="category/java/multithreading.xml"/>
    <rule ref="category/java/performance.xml"/>
    <rule ref="category/java/security.xml"/>
    <rule ref="category/java/bestpractices.xml/AvoidReassigningParameters"/>
    <rule ref="category/java/codestyle.xml/UseDiamondOperator"/>
</ruleset>
"""
    with open(ruleset_path, 'w') as f:
        f.write(ruleset_content)
    print(f"Ruleset file generated at: {ruleset_path}")

def lint_repo_with_pmd_docker(repo_path, ruleset_path, output_format='text', output_file=None):
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"The repository path '{repo_path}' does not exist.")
    if not os.path.exists(ruleset_path):
        raise FileNotFoundError(f"The ruleset path '{ruleset_path}' does not exist.")
    repo_path = os.path.abspath(repo_path)
    ruleset_path = os.path.abspath(ruleset_path)
    client = docker.from_env()
    volumes = {
        repo_path: {'bind': '/src', 'mode': 'ro'},
        ruleset_path: {'bind': '/ruleset.xml', 'mode': 'ro'}
    }
    pmd_command = [
        'pmd', 'check',
        '-d', '/src',
        '-R', '/ruleset.xml',
        '-f', output_format
    ]
    if output_file:
        output_file = os.path.abspath(output_file)
        volumes[output_file] = {'bind': '/output', 'mode': 'rw'}
        pmd_command.extend(['-r', '/output'])
    try:
        container = client.containers.run(
            image='pmd/pmd:latest',
            command=pmd_command,
            volumes=volumes,
            remove=True,
            detach=False
        )
        if isinstance(container, bytes):
            container = container.decode('utf-8')
        print(container)
        if output_file:
            with open(output_file, 'w') as f:
                f.write(container)
        return container
    except docker.errors.ContainerError as e:
        print(f"Container failed with error: {e.stderr}")
        raise
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
        raise

def main(repo_url, output_format='text', output_file=None):
    temp_dir = clone_repo_to_temp(repo_url)
    try:
        ruleset_path = os.path.join(temp_dir, "custom_ruleset.xml")
        generate_pmd_ruleset(ruleset_path)
        lint_repo_with_pmd_docker(temp_dir, ruleset_path, output_format, output_file)
    finally:
        print(f"Cleaning up temporary directory: {temp_dir}")
        subprocess.run(['rm', '-rf', temp_dir], check=True)

if __name__ == "__main__":
    repo_url = "https://github.com/ankitprasad2005/chess_err_hexa"
    output_format = "text"
    output_file = "lint_output.txt"
    main(repo_url, output_format, output_file)