"""
Module to configure and manage logging in the backend application.

This module provides functionality to configure logging settings based on a JSON configuration 
file. It contains a class to load configuration, set up file and console logging, and log 
messages at different levels.

Classes:

LoggerConfig: 
    Configures and manages logging in the backend application.

Methods:

load_config: 
    Loads logging configuration from a JSON file.
setup_file_logging: 
    Sets up file logging based on the loaded configuration.
setup_console_logging: 
    Sets up console logging based on the loaded configuration.
log: 
    Logs messages at different levels using configured loggers.
"""

import logging
import json

from constants import BACKEND_DIR, LOG_DIR

LOG_DIR.mkdir(parents=True, exist_ok=True)


class LoggerConfig:
    """
    Class for configuring and managing logging in the backend application.

    This class provides functionality to load logging configuration from a JSON file, set up
    file and console logging based on the loaded configuration, and log messages at different
    levels.

    """

    CONFIG_PATH = BACKEND_DIR / "logging_config.json"

    def __init__(self, logger_types):
        try:
            self.load_config()
        except Exception as e:
            raise RuntimeError(f"Error loading logging configuration: {e}") from e

        self.loggers = []
        for logger_type in logger_types:
            if logger_type == "file":
                self.setup_file_logging()
            elif logger_type == "console":
                self.setup_console_logging()
            else:
                raise ValueError(f"Unsupported logger type: {logger_type}")

    def load_config(self):
        """
        Load the configuration from the specified JSON file.

        This method reads the configuration parameters from a JSON file and sets the corresponding
        attributes of the object. If the file is not found or contains invalid JSON, appropriate
        errors are raised.

        :return: None
        :raises FileNotFoundError: If the config file is not found.
        :raises ValueError: If the JSON in the config file is invalid.
        """
        try:
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
                self.filename = config.get("filename")
                self.level = getattr(logging, config.get("level", "INFO"))
                self.format = config.get("format")
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Config file {self.CONFIG_PATH} not found") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON in config file") from exc

    def setup_file_logging(self):
        """
        Set up file logging using the specified configuration.

        This method configures file logging according to the parameters set in the object's
        attributes. It creates a FileHandler, sets its level and format, and adds it to the
        list of loggers. If any error occurs during setup, it raises a RuntimeError.

        :return: None
        :raises RuntimeError: If an error occurs during file logging setup.
        """
        log_file = LOG_DIR / self.filename
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(self.level)
            file_handler.setFormatter(logging.Formatter(self.format))
            self.loggers.append(file_handler)
        except Exception as e:
            raise RuntimeError(f"Error setting up file logging: {e}") from e

    def setup_console_logging(self):
        """
        Set up console logging using the specified configuration.

        This method configures console logging according to the parameters set in the object's
        attributes. It creates a StreamHandler, sets its level and format, and adds it to the
        list of loggers. If any error occurs during setup, it raises a RuntimeError.

        :return: None
        :raises RuntimeError: If an error occurs during console logging setup.
        """
        try:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.level)
            console_handler.setFormatter(logging.Formatter(self.format))
            self.loggers.append(console_handler)
        except Exception as e:
            raise RuntimeError(f"Error setting up console logging: {e}") from e

    def log(self, level, message):
        """
        Log a message with the specified logging level.

        This method logs a message using the specified logging level. It iterates through the
        list of loggers, sets up a logger, adds the handler, logs the message, and then removes
        the handler to prevent duplicate logging. If no loggers are initialized, it raises
        a RuntimeError.

        :param level: The logging level (e.g., INFO, DEBUG, ERROR).
        :type level: str
        :param message: The message to be logged.
        :type message: str
        :return: None
        :raises RuntimeError: If an error occurs during logging or if no loggers are initialized.
        """
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
                raise RuntimeError(f"Error during logging: {e}") from e
