import subprocess
import shutil

code_paths = ['./test/anakin.js', './test/meow.py', './test/student.rs']

def run_lint(code_paths: list):
    print(code_paths)
    npx_path = shutil.which("npx")  
    try:
        result = subprocess.run(
            [npx_path,'mega-linter-runner', '--flavor', 'all', '--release', 'beta', '--filesonly']+code_paths
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    return result
    
run_lint(code_paths)