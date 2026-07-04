"""
Scanner Test File 3: Unsafe Deserialization + eval/exec + File Issues

Upload this file into your Secure Code Scanner Dashboard.
Do NOT run this file. It is intentionally vulnerable for scanner testing.
"""

import pickle
import yaml
import tempfile


def load_pickle_data(user_data):
    # ISSUE: Unsafe deserialization with pickle.loads().
    # Why it is risky: Malicious pickle data can execute code.
    # Better fix: Use JSON for untrusted data.
    obj = pickle.loads(user_data)
    return obj


def load_yaml_config(config_text):
    # ISSUE: Unsafe YAML loading.
    # Why it is risky: yaml.load can construct unsafe Python objects.
    # Better fix: Use yaml.safe_load(config_text).
    config = yaml.load(config_text)
    return config


def calculate_expression():
    expression = input("Enter expression: ")

    # ISSUE: eval() on user input.
    # Why it is risky: User can execute Python code.
    # Better fix: Parse safely or use limited math parser.
    result = eval(expression)
    return result


def run_user_code():
    code = input("Enter Python code: ")

    # ISSUE: exec() on user input.
    # Why it is risky: User can execute arbitrary Python code.
    # Better fix: Never execute untrusted code directly.
    exec(code)


def create_temp_file():
    # ISSUE: Insecure temporary file creation.
    # Why it is risky: tempfile.mktemp() can lead to race condition vulnerabilities.
    # Better fix: Use tempfile.NamedTemporaryFile() or tempfile.mkstemp().
    path = tempfile.mktemp()
    return path


def admin_check(role):
    # ISSUE: assert used for security check.
    # Why it is risky: Python can remove assert checks when optimized mode is used.
    # Better fix: Use explicit if condition and raise exception.
    assert role == "admin"
    return "Access granted"


def read_system_file():
    # ISSUE: Hardcoded sensitive file path.
    # Why it is risky: Reading system files like /etc/passwd can expose sensitive data.
    # Better fix: Avoid hardcoded sensitive paths and validate file access.
    file_path = "/etc/passwd"

    with open(file_path, "r") as file:
        return file.read()
