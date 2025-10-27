# simple_tester.py
import json
import subprocess
import time
import datetime
import os

# --- Configuration ---
LOG_FILE = "simple_test_log.txt"
TEST_PLAN_FILE = "test_plan.json"
WAIT_TIME = 10  # The time in seconds to wait before closing an app.

# This is a critical safety feature.
# We will NOT attempt to close any process whose name is on this list.
PROCESS_BLACKLIST = [
    "explorer.exe", # The Windows graphical shell. Killing this removes the desktop.
    "svchost.exe",  # A core Windows service host.
    "winlogon.exe", # The Windows logon process.
    "lsass.exe",    # Local Security Authority Subsystem Service.
    "csrss.exe",    # Client Server Runtime Subsystem.
]

def log_message(message):
    """Writes a message to the console and a log file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def run_test(test_config):
    """Runs a simple test for a single application: open, wait, and close."""
    app_name = test_config['app_name']
    process_name = test_config['process_name']
    
    log_message(f"--- Running Test: {test_config['test_name']} ---")
    
    # 1. Open the application using the robust os.startfile method
    log_message(f"  -> Launching '{app_name}'...")
    try:
        os.startfile(app_name)
        log_message(f"  -> Launch command sent successfully.")
    except Exception as e:
        log_message(f"  -> FAILED to send launch command for '{app_name}'. Error: {e}")
        log_message("--- Test Finished ---\n")
        return # Stop this test if the app can't even be launched

    # 2. Wait for the specified time for manual verification
    log_message(f"  -> Waiting for {WAIT_TIME} seconds...")
    time.sleep(WAIT_TIME)
    
    # 3. Check the blacklist before attempting to close the application
    log_message(f"  -> Preparing to close '{process_name}'...")
    
    if process_name.lower() in PROCESS_BLACKLIST:
        log_message(f"  -> SKIPPING CLOSE: '{process_name}' is on the safety blacklist.")
        log_message("--- Test Finished ---\n")
        return # Exit the function early to prevent killing a critical process

    # 4. Forcefully close the application if it's not on the blacklist
    # taskkill is a built-in Windows command.
    # /F means force kill, /IM means "image name" (the process name).
    # The '>/nul 2>&1' part just suppresses the output of the command
    # so our log stays clean.
    subprocess.run(f"taskkill /F /IM {process_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log_message(f"  -> Close command sent for '{process_name}'.")
    
    log_message("--- Test Finished ---\n")


def main():
    """Main function to load the test plan and run all tests sequentially."""
    log_message("======== Starting Simple Automated Test Suite ========")
    try:
        with open(TEST_PLAN_FILE, "r") as f:
            test_plan = json.load(f)
    except FileNotFoundError:
        log_message(f"FATAL ERROR: The test plan file '{TEST_PLAN_FILE}' was not found. Aborting.")
        return

    for test in test_plan:
        run_test(test)
        
    log_message("======== Test Suite Finished ========")

if __name__ == "__main__":
    main()