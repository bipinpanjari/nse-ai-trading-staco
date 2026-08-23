import os
import json
from datetime import datetime

class BaseAgent:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.log_file = f"backend/logs/agent_{name.lower().replace(' ', '_')}.log"

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {self.name}: {message}"
        print(log_entry)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Logging error: {e}")

    def analyze(self, data):
        raise NotImplementedError("Subclasses must implement analyze()")
