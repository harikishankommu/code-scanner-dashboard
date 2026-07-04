"""
Scanner Test File 2: SQL Injection + Weak Crypto + Flask Debug

Upload this file into your Secure Code Scanner Dashboard.
Do NOT run this file. It is intentionally vulnerable for scanner testing.
"""

import sqlite3
import hashlib
import random
import requests
from flask import Flask, request


app = Flask(__name__)


def get_user_by_name(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ISSUE: SQL injection.
    # Why it is risky: User input is directly inserted into SQL query.
    # Example dangerous input: ' OR '1'='1
    # Better fix: Use parameterized query:
    # cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_product(product_id):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    # ISSUE: SQL injection using f-string.
    # Why it is risky: product_id can modify the query structure.
    # Better fix: cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    query = f"SELECT * FROM products WHERE id = {product_id}"
    cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()
    return rows


def weak_hash_password(password):
    # ISSUE: Weak hashing algorithm MD5.
    # Why it is risky: MD5 is fast and broken for password storage.
    # Better fix: Use bcrypt, argon2, or PBKDF2 with salt.
    return hashlib.md5(password.encode()).hexdigest()


def weak_sha1_token(token):
    # ISSUE: Weak hashing algorithm SHA1.
    # Why it is risky: SHA1 is no longer recommended for security.
    # Better fix: Use SHA-256/HMAC for integrity, bcrypt/argon2 for passwords.
    return hashlib.sha1(token.encode()).hexdigest()


def generate_otp():
    # ISSUE: Insecure random for security-sensitive OTP/token.
    # Why it is risky: random is predictable.
    # Better fix: Use secrets.randbelow() or secrets.token_hex().
    return random.randint(100000, 999999)


def call_payment_api():
    # ISSUE: SSL verification disabled.
    # Why it is risky: It allows man-in-the-middle attacks.
    # Better fix: Keep verify=True.
    response = requests.get("https://example.com/payment", verify=False)
    return response.text


@app.route("/search")
def search():
    username = request.args.get("username")

    # ISSUE: User-controlled input reaches SQL query.
    # Scanner may flag this as injection-related depending on rules.
    return str(get_user_by_name(username))


def start_server():
    # ISSUE: Flask debug mode enabled.
    # Why it is risky: Debug mode can expose sensitive traceback and console.
    # Better fix: debug=False in production.
    app.run(host="0.0.0.0", debug=True)
