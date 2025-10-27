# controller.py
import ollama
import chromadb
import requests
import json
import time

# --- Pillar 1: The Model Context Protocol (MCP) ---

# This component manages the agent's memory using ChromaDB.
class Memory:
    def __init__(self, db_path="./memory_db"):
        # Set up a persistent database in a folder.
        client = chromadb.PersistentClient(path=db_path)
        
        # The 'collection' is like a table. We'll create it if it doesn't exist.
        self.collection = client.get_or_create_collection(name="conversation_history")

    def save(self, user_input, agent_action_json):
        """Saves a single turn of conversation to the vector database."""
        unique_id = str(int(time.time()))
        self.collection.add(
            ids=[unique_id],
            documents=[f"User asked: '{user_input}'. Agent plan was: {agent_action_json}"],
            metadatas=[{"user_input": user_input, "agent_action": agent_action_json}]
        )
        print(f"🧠 MCP: Saved to memory.")

    def retrieve(self, user_input, num_results=2):
        """Retrieves the most relevant memories to provide context."""
        if self.collection.count() == 0:
            return []
        results = self.collection.query(
            query_texts=[user_input],
            n_results=num_results
        )
        print(f"🧠 MCP: Retrieved {len(results['documents'][0])} relevant memories.")
        return results['documents'][0]

# --- Pillar 2: The Planner (The AI Brain) ---

class Planner:
    SYSTEM_PROMPT = """
    You are a helpful desktop assistant. Your job is to translate a user's natural language command into a structured JSON format. You have access to a specific set of tools. You must respond ONLY with a JSON list of commands.

    Available Tools:
    1. "open_application": Use this to open any application. The app_name should be the executable name (e.g., "notepad.exe", "chrome.exe").
    2. "write_text": Use this to type text. Use "\\n" for the enter key.
    
    If you cannot determine an action, or if the user is just chatting, respond with an empty list [].
    """

    def get_plan(self, user_input, context_docs):
        """Asks the LLM to create a plan based on user input and memory context."""
        context_str = "\n".join(context_docs)
        prompt = f"Here is some relevant context from our past conversation:\n{context_str}\n\nBased on this context, please create a JSON plan for the following user request:\n'{user_input}'"

        print(f"\n🤔 Planner: Briefing AI with context...")
        
        try:
            response = ollama.chat(
                model='gemma:7b',
                messages=[
                    {'role': 'system', 'content': self.SYSTEM_PROMPT},
                    {'role': 'user', 'content': prompt}
                ],
                stream=False
            )
            ai_response_str = response['message']['content'].strip()
            print(f"💡 Planner: AI responded with plan: {ai_response_str}")
            return ai_response_str
        except Exception as e:
            print(f"❌ Planner: Error communicating with Ollama: {e}")
            return "[]" # Return an empty plan on error

# --- Pillar 3: The Dispatcher Client ---

def dispatch_plan(command_json):
    """Sends the final JSON plan to the Dispatcher server."""
    payload = {"commands": command_json}
    DISPATCHER_URL = "http://127.0.0.1:5000/add_task"
    try:
        response = requests.post(DISPATCHER_URL, json=payload)
        if response.status_code == 200:
            print(f"📡 Dispatcher: Plan sent successfully.")
            return True
    except requests.ConnectionError:
        print("❌ Dispatcher: Could not connect to the server.")
    return False

# --- Main Application Loop ---
if __name__ == "__main__":
    # Initialize the core components
    memory = Memory()
    planner = Planner()
    
    print("🤖 Cortex Controller is active. Type 'exit' to quit.")
    
    while True:
        user_input = input("\n> ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # 1. RETRIEVE context using the Model Context Protocol
        relevant_memories = memory.retrieve(user_input)
        
        # 2. ASSEMBLE and BRIEF the AI to get a plan
        ai_plan_json = planner.get_plan(user_input, relevant_memories)
        
        # 3. Validate and Dispatch the plan
        try:
            # Check if the plan is valid JSON and not empty
            plan = json.loads(ai_plan_json)
            if isinstance(plan, list) and len(plan) > 0:
                if dispatch_plan(ai_plan_json):
                    # 4. Save the successful interaction to memory
                    memory.save(user_input, ai_plan_json)
            else:
                print("✅ AI decided no action was needed.")
        except json.JSONDecodeError:
            print("❌ AI returned an invalid plan (not valid JSON). Discarding.")