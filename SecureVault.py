import os
import sys
import time
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ==================== CONFIGURATION ====================
LOCKED_EXTENSION = ".locked"
SALT_FILENAME = ".vault_salt"
# =======================================================

def clear_screen():
    """Clears the terminal screen for a clean UI."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_directory():
    """Returns the directory path where the .exe or script is currently located."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def is_safe_directory(target_dir):
    """Safety rail to prevent encrypting the operating system."""
    target_lower = target_dir.lower()
    unsafe_paths = ['c:\\', 'c:\\windows', 'c:\\program files', 'c:\\program files (x86)']
    
    for unsafe in unsafe_paths:
        if target_lower == unsafe or target_lower.startswith(unsafe + '\\'):
            return False
    return True

def secure_delete(file_path):
    """Overwrites a file with random data before deleting it so it cannot be recovered."""
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, "r+b") as f:
            # Overwrite with random bytes
            f.write(os.urandom(file_size))
        os.remove(file_path)
    except Exception:
        # Fallback to standard delete if overwrite fails (e.g., permission issues)
        try:
            os.remove(file_path)
        except:
            pass

def get_or_create_salt(current_dir):
    """Retrieves an existing random salt for this folder, or creates a new hidden one."""
    salt_path = os.path.join(current_dir, SALT_FILENAME)
    
    if os.path.exists(salt_path):
        with open(salt_path, "rb") as f:
            return f.read()
    else:
        new_salt = os.urandom(16)
        with open(salt_path, "wb") as f:
            f.write(new_salt)
        
        # Attempt to hide the salt file on Windows so it doesn't clutter the folder
        if os.name == 'nt':
            os.system(f'attrib +h "{salt_path}"')
        return new_salt

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a deterministic 32-byte Fernet key from the password and random salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def process_vault(mode: str):
    clear_screen()
    current_dir = get_current_directory()
    
    if not is_safe_directory(current_dir):
        print("\n[!] CRITICAL ERROR: Safety System Activated!")
        print("    You are trying to run this in a critical system folder.")
        print("    This script refuses to run here to prevent destroying your OS.")
        input("\nPress Enter to return to menu...")
        return
    
    # UI Header
    print("========================================================")
    print(f"            ███████╗ ██████╗██╗   ██╗██████╗ ███████╗")
    print(f"            ██╔════╝██╔════╝██║   ██║██╔══██╗██╔════╝")
    print(f"            ███████╗██║     ██║   ██║██████╔╝█████╗  ")
    print(f"            ╚════██║██║     ██║   ██║██╔══██╗██╔══╝  ")
    print(f"            ███████║╚██████╗╚██████╔╝██║  ██║███████╗")
    print(f"            ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝")
    print("========================================================")
    print(f" MODE   : {mode.upper()}")
    print(f" TARGET : {current_dir}")
    print("========================================================\n")
    
    # Replaced getpass with standard input so the password is visible
    password = input(" Enter Master Password:\n > ").strip()
    
    if not password:
        print("\n[!] Error: Password cannot be empty.")
        input("\nPress Enter to return to menu...")
        return

    print("\n [*] Processing... Please wait.")
    
    try:
        salt = get_or_create_salt(current_dir)
        key = derive_key(password, salt)
        fernet = Fernet(key)
    except Exception as e:
        print(f"\n[!] System Error: {e}")
        input("\nPress Enter to return to menu...")
        return

    success_count = 0
    error_count = 0
    
    running_file = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__).lower()

    for root, dirs, files in os.walk(current_dir):
        for filename in files:
            # Skip the script itself, salt file, and builder files
            if filename.lower() == running_file or filename == SALT_FILENAME or filename.endswith(".spec"):
                continue

            file_path = os.path.join(root, filename)

            if mode == "encrypt":
                if filename.endswith(LOCKED_EXTENSION):
                    continue
                try:
                    with open(file_path, "rb") as f:
                        data = f.read()
                    
                    encrypted_data = fernet.encrypt(data)
                    
                    with open(file_path + LOCKED_EXTENSION, "wb") as f:
                        f.write(encrypted_data)
                    
                    # Securely shred the original file
                    secure_delete(file_path)
                    success_count += 1
                except Exception:
                    error_count += 1

            elif mode == "decrypt":
                if not filename.endswith(LOCKED_EXTENSION):
                    continue
                try:
                    with open(file_path, "rb") as f:
                        data = f.read()
                    
                    decrypted_data = fernet.decrypt(data)
                    
                    original_path = file_path[:-len(LOCKED_EXTENSION)]
                    with open(original_path, "wb") as f:
                        f.write(decrypted_data)
                    
                    # Securely shred the locked file
                    secure_delete(file_path)
                    success_count += 1
                except InvalidToken:
                    error_count += 1
                except Exception:
                    error_count += 1

    print("\n========================================================")
    print("                   OPERATION COMPLETE                   ")
    print("========================================================")
    print(f" [+] Files Successfully Processed : {success_count}")
    
    if error_count > 0:
        print(f" [!] Errors / Skipped Files       : {error_count}")
        if mode == "decrypt":
            print("     (Errors are usually caused by an incorrect password!)")
    print("========================================================")
    
    input("\nPress Enter to return to the main menu...")

def main_menu():
    while True:
        clear_screen()
        print("========================================================")
        print("                 🔒 SECURE FILE MANAGER 🔒             ")
        print("========================================================")
        print(f" Location: {get_current_directory()}")
        print("--------------------------------------------------------")
        print("  [ 1 ] 🔒 Lock All Files in This Folder")
        print("  [ 2 ] 🔓 Unlock All Files in This Folder")
        print("  [ 3 ] ❌ Exit Program")
        print("--------------------------------------------------------")
        
        choice = input(" Select an option (1, 2, or 3) > ").strip()

        if choice == '1':
            process_vault("encrypt")
        elif choice == '2':
            process_vault("decrypt")
        elif choice == '3':
            print("\nExiting... Keep your password safe. Goodbye!")
            time.sleep(1.5)
            sys.exit(0)
        else:
            print("\n[!] Invalid selection. Please type 1, 2, or 3.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()