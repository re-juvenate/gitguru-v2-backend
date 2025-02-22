from .semgrep import SemgrepScanner

file_path = "src/sast/jsonnet.js"

scanner = SemgrepScanner(file_path)

results, status_code = scanner.run_scan()

print(f"Status Code: {status_code}")
print("Scan Results:", results)
