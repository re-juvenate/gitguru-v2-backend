import subprocess
import os
import json

class SemgrepScanner:
    """
    Class to handle Semgrep scanning functionality.
    """
    
    def __init__(self, file_path):
        self.file_path = file_path
    
    def run_scan(self):
        """
        Run semgrep scan on the specified file and return JSON results
        """
        try:
            if not os.path.exists(self.file_path):
                return {"error": "File not found"}, 404
            
            cmd = ["semgrep", "scan", "--json", self.file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"error": "Semgrep scan failed", "details": result.stderr}, 500
            
            try:
                scan_results = json.loads(result.stdout)
                semgrep_results = {}
                for result in scan_results["results"]:
                    message, file = result["extra"]["message"], result["path"]
                    semgrep_results[file] = message
                return semgrep_results
            except json.JSONDecodeError:
                return {"error": "Failed to parse Semgrep output", "raw_output": result.stdout}, 500
                
        except Exception as e:
            return {"error": "Internal server error", "details": str(e)}, 500
