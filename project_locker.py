import os
import sys
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_fernet(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key)

def encrypt_file(file_path, password):
    if file_path.endswith('.enc') or os.path.basename(file_path) in ['project_locker.py', 'pymeet.db']:
        return
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            
        salt = os.urandom(16)
        fernet = get_fernet(password, salt)
        encrypted_data = fernet.encrypt(data)
        
        with open(file_path + '.enc', 'wb') as f:
            f.write(salt + encrypted_data)
            
        os.remove(file_path)
        print(f"Encrypted: {file_path}")
    except Exception as e:
        print(f"Skipped {file_path}: {e}")

def decrypt_file(file_path, password):
    if not file_path.endswith('.enc'):
        return
        
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            
        salt = data[:16]
        encrypted_data = data[16:]
        
        fernet = get_fernet(password, salt)
        decrypted_data = fernet.decrypt(encrypted_data)
        original_path = file_path[:-4]
        
        with open(original_path, 'wb') as f:
            f.write(decrypted_data)
            
        os.remove(file_path)
        print(f"Decrypted: {original_path}")
    except Exception as e:
        print(f"Failed to decrypt {file_path}. Wrong password?")

def process_directory(directory, password, mode='encrypt'):
    exclude_dirs = ['.git', '.venv', 'venv', 'node_modules', '__pycache__', 'dist', '.vscode']
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            file_path = os.path.join(root, file)
            if mode == 'encrypt':
                encrypt_file(file_path, password)
            else:
                decrypt_file(file_path, password)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python project_locker.py [encrypt|decrypt] [password]")
        sys.exit(1)
        
    mode = sys.argv[1]
    password = sys.argv[2]
    
    if mode not in ['encrypt', 'decrypt']:
        print("Mode must be 'encrypt' or 'decrypt'")
        sys.exit(1)
        
    print(f"Starting {mode}ion...")
    # Encrypt frontend and backend folders
    process_directory('backend/app', password, mode)
    process_directory('frontend/src', password, mode)
    process_directory('backend/app/routes', password, mode)
    
    print(f"{mode.capitalize()}ion completed.")
    print("Project Secured by Nishant Panwar.")
