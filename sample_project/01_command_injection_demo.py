"""
Scanner Test File 1: Command Injection + Hardcoded Secrets

Upload this file into your Secure Code Scanner Dashboard.
Do NOT run this file. It is intentionally vulnerable for scanner testing.
"""

import os
import subprocess


# ISSUE: Hardcoded password.
# Why it is risky: Passwords in source code can be leaked through GitHub or logs.
# Better fix: Store secrets in environment variables or a secrets manager.
ADMIN_PASSWORD = "admin123"


# ISSUE: Hardcoded API key.
# Why it is risky: API keys should not be committed to code.
# Better fix: Use os.getenv("API_KEY").
API_KEY = "fake_api_key_12345"


def ping_host():
    user_input = input("Enter host: ")

    # ISSUE: Command injection.
    # Why it is risky: User input is directly joined with a shell command.
    # Example dangerous input: 127.0.0.1 && whoami
    # Better fix: Use subprocess.run(["ping", user_input], shell=False)
    os.system("ping " + user_input)


def run_command():
    command = input("Enter command: ")

    # ISSUE: subprocess with shell=True.
    # Why it is risky: shell=True allows command injection if input is controlled by user.
    # Better fix: Pass command as a list and keep shell=False.
    subprocess.call(command, shell=True)


def list_directory(folder_name):
    # ISSUE: Another command injection pattern.
    # Why it is risky: folder_name can contain extra shell commands.
    # Better fix: Use Python functions like os.listdir(folder_name).
    subprocess.Popen("dir " + folder_name, shell=True)
