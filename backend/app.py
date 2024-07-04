"""
Application entrypoint for processing messages and executing scripts.

This module serves as the entrypoint for the application, responsible for processing incoming 
messages, determining the appropriate script to execute based on the message content, and 
executing the corresponding script.

Functions:

- process_message(message): 
    Processes the incoming message, determines the script to execute, and executes the script.
- main(): 
    Main function of the application that continuously listens for incoming messages,
    processes them, and sends back the response.
"""

import json
import sys
import win32pipe, win32file

from logger_config import LoggerConfig
from run_check_data_type import RunCheckDataType
from run_fetch_measures import RunFetchScenario
from run_scenario import RunScenario

pipe_name = r"\\.\pipe\electron-python-pipe"
logger = LoggerConfig(logger_types=["file"])


def process_message(pipe, message):
    """
    Process a message and execute the corresponding script.

    This function processes a message containing information about a script to be executed
    along with optional data. Based on the script name provided in the message, it creates
    an instance of the corresponding runner class and executes the script. It then returns
    a response indicating whether the execution was successful along with any results.

    :param pipe: The pipe handle used for communication.
    :param message: The message containing information about the script and optional data.
    :type message: dict
    :return: A response indicating the success or failure of the script execution and any results.
    :rtype: dict
    """
    script_name = message.get("scriptName", "")
    data = message.get("data", None)

    if script_name == "run_scenario.py":
        runner = RunScenario(data, pipe)
        result = runner.run_scenario()
        response = {"success": True, "result": result}
    elif script_name == "run_check_data_type.py":
        runner = RunCheckDataType(data, pipe)
        result = runner.run_check_data_type()
        response = {"success": True, "result": result}
    elif script_name == "run_fetch_measures.py":
        runner = RunFetchScenario(data, pipe)
        result = runner.run_fetch_measures()
        response = {"success": True, "result": result}
    else:
        response = {"success": False, "error": f"Unknown script: {script_name}"}

    return response


def main():
    """
    Main function for interacting with the Electron process through a named pipe.

    This function sends a 'ready' event to the Electron process upon initialization.
    It then enters a loop where it continuously reads messages from the named pipe, processes
    each message using the process_message function, and sends the response back through
    the named pipe as a JSON string.
    """
    logger.log("info", json.dumps({"type": "event", "name": "ready"}))
    while True:
        pipe = win32pipe.CreateNamedPipe(
            pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            1,
            65536,
            65536,
            300000,  # Increase timeout to 300 seconds
            None,
        )

        win32pipe.ConnectNamedPipe(pipe, None)

        while True:
            try:
                result, data = win32file.ReadFile(pipe, 4096)
                if not data:
                    break
                message = json.loads(data.decode("utf-8"))
                response = process_message(pipe, message)
                response_data = json.dumps(response).encode("utf-8")
                win32file.WriteFile(pipe, response_data)
            except Exception as e:
                logger.log("info", f"Error in named pipe. More info: {e}")
                break

        win32pipe.DisconnectNamedPipe(pipe)
        win32file.CloseHandle(pipe)


# Add this condition to ensure the infinite loop is only executed when app.py
# is run as the main script
if __name__ == "__main__":
    main()
