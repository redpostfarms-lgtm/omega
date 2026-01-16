#!/usr/bin/env python3
import secrets
import string

def generate_password(length=20):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

if __name__ == "__main__":
    print("Generated secure password:")
    print(generate_password())
