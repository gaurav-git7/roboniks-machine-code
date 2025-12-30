import json
import os
from pathlib import Path

class ActivationManager:
    def __init__(self):
        # Activation file path
        self.base_path = Path.home() / "AppData" / "Local" / "IVD"
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.file_path = self.base_path / "activation.json"

    def is_activated(self):
        if not self.file_path.exists():
            return False

        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                return data.get("activated", False)
        except:
            return False

    def save_activation(self, distributor_name, code):
        data = {
            "activated": True,
            "distributor": distributor_name,
            "code": code
        }
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

