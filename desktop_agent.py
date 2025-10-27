# desktop_agent.py
import os # Make sure os is imported!
import requests
import time
import json
import subprocess
import pyautogui


def open_application(app_name):
    print(f"ACTION: Opening '{app_name}'")
    try:
        # It should use os.startfile
        os.startfile(app_name) 
    except Exception as e:
        print(f"An error occurred: {e}")
# --- Tool and Executor Functions (The 'Hands') ---

def write_text(text_to_write):
    print(f"ACTION: Typing '{text_to_write}'")
    pyautogui.sleep(1)
    pyautogui.write(text_to_write, interval=0.05)

TOOL_REGISTRY = {
    "open_application": open_application,
    "write_text": write_text,
}

def execute_commands(commands_json_string):
    commands = json.loads(commands_json_string)
    for command in commands:
        tool_name = command.get("tool")
        parameters = command.get("parameters")
        if tool_name in TOOL_REGISTRY:
            TOOL_REGISTRY[tool_name](**parameters)

# --- Main Agent Loop ---
def main_loop():
    MCP_SERVER_URL = "http://127.0.0.1:5000"
    print("Desktop Agent activated. Polling for tasks...")
    while True:
        try:
            response = requests.get(f"{MCP_SERVER_URL}/get_task")
            data = response.json()
            if data.get("status") == "new_task":
                print(f"\n[+] New task received: {data.get('commands')}")
                execute_commands(data.get('commands'))
            time.sleep(3) # Wait 3 seconds before polling again
        except requests.ConnectionError:
            print("MCP Server offline. Retrying...")
            time.sleep(5)

if __name__ == '__main__':
    main_loop()