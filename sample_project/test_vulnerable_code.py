import os
import subprocess
import pickle
import yaml
import sqlite3
import hashlib
import random
import tempfile
import requests
from flask import Flask, request


# -------------------------------
# 1. Hardcoded secrets/passwords
# -------------------------------

password = "admin123"
api_key = "sk_test_123456789"
secret_token = "my_super_secret_token"


# -------------------------------
# 2. Command injection using os.system
# -------------------------------

def ping_host():
    user_input = input("Enter host: ")
    os.system("ping " + user_input)


# -------------------------------
# 3. Shell=True subprocess issue
# -------------------------------

def run_command():
    cmd = input("Enter command: ")
    subprocess.call(cmd, shell=True)


def run_popen():
    user_cmd = input("Enter another command: ")
    subprocess.Popen(user_cmd, shell=True)


# -------------------------------
# 4. Dangerous eval usage
# -------------------------------

def calculate_expression():
    expression = input("Enter expression: ")
    result = eval(expression)
    print(result)


# -------------------------------
# 5. Dangerous exec usage
# -------------------------------

def execute_code():
    user_code = input("Enter Python code: ")
    exec(user_code)


# -------------------------------
# 6. Insecure deserialization using pickle
# -------------------------------

def load_user_data(data):
    user_object = pickle.loads(data)
    return user_object


# -------------------------------
# 7. Unsafe YAML loading
# -------------------------------

def load_yaml_config(config_text):
    config = yaml.load(config_text)
    return config


# -------------------------------
# 8. SQL injection
# -------------------------------

def get_user_details(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)

    data = cursor.fetchall()
    conn.close()

    return data


def get_product_details(product_id):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    query = f"SELECT * FROM products WHERE id = {product_id}"
    cursor.execute(query)

    data = cursor.fetchall()
    conn.close()

    return data


# -------------------------------
# 9. Weak hashing algorithms
# -------------------------------

def hash_password_md5(user_password):
    return hashlib.md5(user_password.encode()).hexdigest()


def hash_password_sha1(user_password):
    return hashlib.sha1(user_password.encode()).hexdigest()


# -------------------------------
# 10. Insecure random for security token
# -------------------------------

def generate_token():
    token = random.randint(100000, 999999)
    return token


# -------------------------------
# 11. Insecure temporary file creation
# -------------------------------

def create_temp_file():
    temp_file = tempfile.mktemp()
    return temp_file


# -------------------------------
# 12. SSL certificate verification disabled
# -------------------------------

def call_api():
    response = requests.get("https://example.com/api/user", verify=False)
    return response.text


# -------------------------------
# 13. Assert used for security check
# -------------------------------

def admin_only(role):
    assert role == "admin"
    return "Access granted"


# -------------------------------
# 14. Flask app with debug enabled
# -------------------------------

app = Flask(__name__)


@app.route("/login")
def login():
    username = request.args.get("username")
    password_input = request.args.get("password")

    query = (
        "SELECT * FROM users WHERE username = '"
        + username
        + "' AND password = '"
        + password_input
        + "'"
    )

    return query


@app.route("/run")
def run_from_url():
    command = request.args.get("cmd")
    output = subprocess.check_output(command, shell=True)
    return output


def start_app():
    app.run(host="0.0.0.0", debug=True)


# -------------------------------
# 15. Hardcoded file path
# -------------------------------

def read_sensitive_file():
    file_path = "/etc/passwd"

    with open(file_path, "r") as file:
        content = file.read()

    return content


# -------------------------------
# 16. Main function
# -------------------------------

if __name__ == "__main__":
    ping_host()
    run_command()