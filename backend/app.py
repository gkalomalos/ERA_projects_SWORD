"""
Application entrypoint for processing messages and executing scripts.

This module serves as the entrypoint for the application, responsible for processing incoming 
messages, determining the appropriate script to execute based on the message content, and 
executing the corresponding script.

Functions:
- process_message(message): Processes the incoming message, determines the script to execute, and executes the script.
- main(): Main function of the application that continuously listens for incoming messages,
  processes them, and sends back the response.

Author: [SWORD] Georgios Kalomalos
Email: georgios.kalomalos@sword-group.com
Date: 23/4/2024
"""

import json
import sys

from run_check_data_type import RunCheckDataType
from run_scenario import RunScenario
from run_fetch_measures import RunFetchScenario


def process_message(message):
    script_name = message.get("scriptName", "")
    data = message.get("data", None)

    if script_name == "run_scenario.py":
        runner = RunScenario(data)
        result = runner.run_scenario()
        response = {"success": True, "result": result}
    elif script_name == "run_check_data_type.py":
        runner = RunCheckDataType(data)
        result = runner.run_check_data_type()
        response = {"success": True, "result": result}
    elif script_name == "run_fetch_measures.py":
        runner = RunFetchScenario(data)
        result = runner.run_fetch_measures()
        response = {"success": True, "result": result}
    else:
        response = {"success": False, "error": f"Unknown script: {script_name}"}

    return response


def main():
    # Send the 'ready' event to the Node.js process
    ready_event = {"type": "event", "name": "ready"}
    print(json.dumps(ready_event))
    sys.stdout.flush()

    while True:
        raw_message = sys.stdin.readline().strip()

        if raw_message:
            message = json.loads(raw_message)
            response = process_message(message)
            # Send the response back through stdout as a JSON string
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


# Add this condition to ensure the infinite loop is only executed when app.py is run as the main script
if __name__ == "__main__":
    main()
