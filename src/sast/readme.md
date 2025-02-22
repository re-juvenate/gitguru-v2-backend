pip install flask semgrep

python __init__.py

curl -X POST http://localhost:5000/scan \
     -H "Content-Type: application/json" \
     -d '{"file_path": "./jsonnet.js"}'