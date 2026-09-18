# Password Manager

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security Tool](https://img.shields.io/badge/security-tool-green.svg)]()

A secure password manager CLI with encryption and password generator.

## ✨ Features

- **Secure Storage** - Encryption at rest (AES/Fernet)
- **Master Password** - Single master password to unlock
- **Password Generator** - Generate strong random passwords
- **Categories** - Organize by category
- **Password Strength** - Check password strength
- **Search** - Find passwords quickly
- **Auto-lock** - Automatic locking after timeout
- **Rich UI** - Beautiful colored terminal output

## 📦 Installation

```bash
git clone https://github.com/Master-626/password-manager.git
cd password-manager
pip install .
```

## 🚀 Quick Start

```bash
# Add a password
passman add github -u Master-626

# Get a password
passman get github

# Generate a strong password
passman generate -l 20
```

## 🔒 Security

All passwords are encrypted at rest using industry-standard cryptography. Your data never leaves your computer.

## 📄 License

MIT License
