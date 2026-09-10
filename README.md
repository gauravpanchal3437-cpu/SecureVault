# 🔐 SecureVault

### Password-Based File Encryption & Recovery Tool

SecureVault is a Python-based cybersecurity project designed to
demonstrate practical concepts of file encryption, password-based
key derivation, secure file handling, and controlled file recovery.

## Features

- Password-based file encryption
- Password-based file decryption
- PBKDF2-HMAC-SHA256 key derivation
- Random salt generation
- Fernet authenticated encryption
- `.locked` file format
- Recursive file processing
- Safety checks for critical directories
- Windows executable version

## Technologies

- Python
- Cryptography
- PBKDF2-HMAC-SHA256
- Fernet
- Windows
- PyInstaller

## How It Works

Password
↓
Random Salt
↓
PBKDF2-HMAC-SHA256
↓
Derived Key
↓
Fernet Encryption
↓
`.locked` File

## Disclaimer

This project is intended for educational and authorized security
research in controlled environments only.

Do not use this software on files or systems without authorization.