from cryptography.fernet import Fernet
import base64

with open("key.bin", "rb") as f:
    key_data = f.read()
    salt = key_data[:16]
    encoded_key = key_data[16:]

# Use the encoded key directly with Fernet
cipher = Fernet(encoded_key)

with open("credentials.json", "rb") as f:
    plaintext = f.read()

ciphertext = cipher.encrypt(plaintext)

with open("credentials.encrypted", "wb") as f:
    f.write(salt + ciphertext)