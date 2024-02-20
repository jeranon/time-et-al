import hashlib
import os
import base64
from getpass import getpass

def generate_key(password, salt, iterations=100000, dklen=32):
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, dklen)
    return key

# Prompt for the password
password = getpass("Enter the password for key generation: ")

salt = os.urandom(16)  # Generate a random salt
key = generate_key(password, salt)

# Encode the key in base64
encoded_key = base64.urlsafe_b64encode(key)

# Save the salt and the encoded key
with open("key.bin", "wb") as f:
    f.write(salt + encoded_key)

print("Key generated and saved successfully.")
