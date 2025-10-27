# submit_task.py
import requests

# This is our test command. We are pretending to be the AI.
# Goal: Open Notepad and write a message.
#COMMAND_JSON = '[{"tool": "open_application", "parameters": {"app_name": "notepad.exe"}}, {"tool": "write_text", "parameters": {"text_to_write": "Phase 1 is working!"}}]'
# The new command to open Chrome and type
COMMAND_JSON = '[{"tool": "open_application", "parameters": {"app_name": "firefox.exe"}}, {"tool": "write_text", "parameters": {"text_to_write": "youtube.com\\n"}}]'
payload = {"commands": COMMAND_JSON}
MCP_SERVER_URL = "http://127.0.0.1:5000/add_task"

try:
    response = requests.post(MCP_SERVER_URL, json=payload)
    print(f"Server response: {response.json()}")
except requests.ConnectionError:
    print("Could not connect to MCP Server. Is it running?")