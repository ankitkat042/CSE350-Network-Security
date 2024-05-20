import json
from pyzbar.pyzbar import decode
from PIL import Image
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

# Load public key from file
def load_public_key():
    with open('public_key.pem', 'rb') as key_file:
        public_key = serialization.load_pem_public_key(key_file.read())
    return public_key

# Verify the signature
def verify_signature(public_key, data, signature):
    try:
        public_key.verify(
            signature,
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        return False

def main():
    # Decode the QR code
    image = Image.open('Ankit Kumar_tampered.png')
    decoded_data = decode(image)[0].data.decode()
    
    # Extract signature and verify
    decoded_json = json.loads(decoded_data)
    received_signature = bytes.fromhex(decoded_json['driving_license'].pop('data_signature'))
    
    # Load public key
    public_key = load_public_key()
    
    # Check if data is correct and hasn't been tampered with
    if verify_signature(public_key, json.dumps(decoded_json, sort_keys=True), received_signature):
        print("The data is intact and authentic.")
    else:
        print("Data integrity check failed.")

if __name__ == "__main__":
    main()
