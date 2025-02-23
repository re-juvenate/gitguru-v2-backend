from pathlib import Path
from magika import Magika

class Identifier:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.m = Magika()
        return cls._instance

    def identify_file(self, file_path: str) -> str:
        path_obj = Path(file_path)
        result = self.m.identify_path(path_obj)
        
        if result.status.ok():
            return result.prediction.output.label
        else:
            return f"Error identifying file: {result.status.message}"

    def identify_text(self, text: str) -> str:
        result = self.m.identify_bytes(text.encode('utf-8'))
        
        # Check if identification was successful
        if result.status.ok():
            return result.prediction.output.label
        else:
            return f"Error identifying text: {result.status.message}"

