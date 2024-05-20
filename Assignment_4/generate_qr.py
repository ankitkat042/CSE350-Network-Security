import json
import qrcode
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

# Function to generate RSA keys and save them
def generate_and_save_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    
    # Save the private key
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save the public key
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    return private_key

# Sign the data using the private key
def sign_data(private_key, data):
    return private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

# Function to generate QR code from JSON data
def create_qr_code(json_data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(json_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(filename)


def tamper(data):
    data['driving_license']['license_number'] = '42'
    return data

def main():
    # Load JSON data from a file
    with open('data.json', 'r') as file:
        data = json.load(file)
    
    # Generate and save keys
    private_key = generate_and_save_keys()
    
    # Sign data
    json_data = json.dumps(data, sort_keys=True)
    signature = sign_data(private_key, json_data)
    data['driving_license']['data_signature'] = signature.hex()
    full_name = data['driving_license']['full_name']

    data = tamper(data)
    full_name = data['driving_license']['full_name']+'_tampered'
    
    # Create QR code
    full_json = json.dumps(data)
    create_qr_code(full_json, f'{full_name}.png')
    print("QR code has been generated.")

if __name__ == "__main__":
    main()
