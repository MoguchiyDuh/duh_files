# Crypt Script (`crypt.sh`) Guide

A lightweight Bash wrapper around OpenSSL 3.0+ for AES-256 file encryption. It simplifies the syntax for encrypting and decrypting sensitive files.

---

## Usage

```bash
./crypt.sh [COMMAND] [FILE]
```

## Commands

### `encrypt` (Alias: `e`)

Encrypts a file using AES-256-CBC with PBKDF2 key derivation and a random salt.

**Workflow:**

1.  Checks if the input file exists.
2.  Prompts the user for a password (interactive input).
3.  Generates an output file with the `.enc` extension (e.g., `data.txt` -> `data.txt.enc`).
4.  If successful, prompts the user to securely delete the original unencrypted file.

### `decrypt` (Alias: `d`)

Decrypts a previously encrypted file.

**Workflow:**

1.  Checks input file existence.
2.  Determines output filename:
    - If input ends in `.enc`, removes the extension.
    - Otherwise, appends `.dec`.
3.  Prompts for the password.
4.  If successful, prompts the user to delete the encrypted source file.

## Technical Details

- **Cipher**: `aes-256-cbc`
- **Key Derivation**: `pbkdf2` (Password-Based Key Derivation Function 2)
- **Salt**: Enabled (ensures identical passwords produce different ciphertext)
- **Iteration Count**: OpenSSL default (high enough to resist brute-force)

