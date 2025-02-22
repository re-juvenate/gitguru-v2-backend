    from flask import Flask, request, jsonify
    import subprocess
    import os
    import json

    app = Flask(__name__)

    def run_semgrep_scan(file_path):
        """
        Run semgrep scan on the specified file and return JSON results
        """
        try:
            # Verify file exists
            if not os.path.exists(file_path):
                return {"error": "File not found"}, 404
                
            # Run semgrep command
            cmd = ["semgrep", "scan", "--json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Check if command was successful
            if result.returncode != 0:
                return {
                    "error": "Semgrep scan failed",
                    "details": result.stderr
                }, 500
                
            # Parse JSON output
            try:
                scan_results = json.loads(result.stdout)
                return scan_results, 200
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse Semgrep output",
                    "raw_output": result.stdout
                }, 500
                
        except Exception as e:
            return {
                "error": "Internal server error",
                "details": str(e)
            }, 500

    @app.route('/scan', methods=['POST'])
    def scan_file():
        """
        Endpoint to scan a file using Semgrep
        
        Expected POST body:
        {
            "file_path": "/path/to/file"
        }
        """
        data = request.get_json()
        
        if not data or 'file_path' not in data:
            return jsonify({
                "error": "Missing required parameter: file_path"
            }), 400
            
        file_path = data['file_path']
        results, status_code = run_semgrep_scan(file_path)
        return jsonify(results), status_code

    if __name__ == '__main__':
        app.run(debug=True)