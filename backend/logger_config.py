import logging
import json


class LoggerConfig:
    CONFIG_PATH = "logging_config.json"

    def __init__(self, logger_types):
        try:
            self.load_config()
        except Exception as e:
            raise RuntimeError(f"Error loading logging configuration: {e}")

        self.loggers = []
        for logger_type in logger_types:
            if logger_type == "file":
                self.setup_file_logging()
            elif logger_type == "console":
                self.setup_console_logging()
            else:
                raise ValueError(f"Unsupported logger type: {logger_type}")

    def load_config(self):
        try:
            with open(self.CONFIG_PATH, "r") as config_file:
                config = json.load(config_file)
                self.filename = config.get("filename")
                self.level = getattr(logging, config.get("level", "INFO"))
                self.format = config.get("format")
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {self.CONFIG_PATH} not found")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in config file")

    def setup_file_logging(self):
        try:
            file_handler = logging.FileHandler(self.filename)
            file_handler.setLevel(self.level)
            file_handler.setFormatter(logging.Formatter(self.format))
            self.loggers.append(file_handler)
        except Exception as e:
            raise RuntimeError(f"Error setting up file logging: {e}")

    def setup_console_logging(self):
        try:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.level)
            console_handler.setFormatter(logging.Formatter(self.format))
            self.loggers.append(console_handler)
        except Exception as e:
            raise RuntimeError(f"Error setting up console logging: {e}")

    def log(self, level, message):
        if not self.loggers:
            raise RuntimeError("No loggers initialized")
        for handler in self.loggers:
            try:
                logger = logging.getLogger()
                logger.setLevel(self.level)
                logger.addHandler(handler)
                log_function = getattr(logging, level.lower(), logging.info)
                log_function(message)
                logger.removeHandler(handler)  # Prevent duplicate logging
            except Exception as e:
                raise RuntimeError(f"Error during logging: {e}")
