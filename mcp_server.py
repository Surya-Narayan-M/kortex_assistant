# mcp_server.py
from flask import Flask, request, jsonify
from collections import deque
import json

app = Flask(__name__)
task_queue = deque()

@app.route('/')
def index():
    return f"MCP Server is running. Tasks in queue: {len(task_queue)}"

@app.route('/add_task', methods=['POST'])
def add_task():
    if not request.json or 'commands' not in request.json:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    task_json_string = request.json['commands']
    task_queue.append(task_json_string)
    print(f"Task added. Queue size: {len(task_queue)}")
    return jsonify({"status": "success", "message": "Task added."})

@app.route('/get_task', methods=['GET'])
def get_task():
    if not task_queue:
        return jsonify({"status": "no_task"})
    
    task = task_queue.popleft()
    print(f"Task dispatched. Queue size: {len(task_queue)}")
    return jsonify({"status": "new_task", "commands": task})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)