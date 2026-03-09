"""test utils"""

import json
import os
from pathlib import Path
import sys


from aussiebb.types import AussieBBConfigFile


def configloader() -> AussieBBConfigFile:
    """loads config"""
    for filename in [os.path.expanduser("~/.config/aussiebb.json"), "aussiebb.json"]:
        filepath = Path(filename).resolve()
        if filepath.exists():
            try:
                contents = filepath.read_text(encoding="utf-8")
                configfile = AussieBBConfigFile.model_validate_json(contents)
                return configfile
            except json.JSONDecodeError as json_error:
                sys.exit(f"Failed to parse config file: {json_error}")
    return AussieBBConfigFile.model_validate({"users": []})
