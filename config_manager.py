import json
import os
from os.path import exists, dirname

class ConfigManager:
    def __init__(self):
        # Define the config file path
        self.config_file_name = "config/config.json"
        # Default configuration settings
        self.defaults = {
            "lrToken": None
        }
        self.config = self.defaults

    def initialize(self):
        # Ensure the directory exists
        config_dir = dirname(self.config_file_name)
        if not exists(config_dir):
            os.makedirs(config_dir)  # Create the directory if it doesn't exist

        # Create the config file with default settings if it does not exist
        if not exists(self.config_file_name):
            js = json.dumps(self.config, indent=4)  # Pretty-print JSON
            with open(self.config_file_name, "w") as io_writer:
                io_writer.write(js)

    def read_config(self) -> bool:
        # Read and parse the config file
        if not exists(self.config_file_name):
            print(f"Config file '{self.config_file_name}' does not exist.")
            return False

        with open(self.config_file_name, "r") as io_reader:
            js = io_reader.read()
        try:
            jo = json.loads(js)
        except json.JSONDecodeError as ex:
            print(f"Unable to parse json config file: {ex}")
            return False

        # Update the config with values from the file
        for key in self.config.keys():
            if key not in jo:
                print(f"Unable to locate key '{key}' in config file")
            else:
                self.config[key] = jo[key]

        return True

    def get(self, key: str):
        if key in self.config:
            return self.config[key]
        else:
            print(f"Key '{key}' is not a valid config key")

    def simple_get(self, key: str):
        self.read_config()
        return self.get(key)

    def write_config(self):
        js = json.dumps(self.config, indent=4)  # Pretty-print JSON
        with open(self.config_file_name, "w") as io_writer:
            io_writer.write(js)

    def set(self, key: str, value):
        if key in self.config:
            self.config[key] = value
        else:
            print(f"Key '{key}' is not a valid config key")

    def simple_set(self, key: str, value):
        self.set(key, value)
        self.write_config()


cM = ConfigManager()
cM.initialize()
