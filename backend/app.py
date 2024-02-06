import sys
import json

from run_scenario import run_scenario
from run_check_data_type import run_check_data_type


def process_message(message):
    script_name = message.get("scriptName", "")
    data = message.get("data", None)

    if script_name == "run_scenario.py":
        result = run_scenario(data)
        response = {"success": True, "result": result}
    elif script_name == "run_check_data_type.py":
        result = run_check_data_type(data)
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
