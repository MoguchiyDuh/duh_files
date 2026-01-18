#!/bin/bash
# Simple file encryption/decryption using OpenSSL

set -e

show_help() {
    echo "Usage: $0 [encrypt|decrypt] <file>"
    echo
    echo "Commands:"
    echo "  encrypt <file>    Encrypt file (creates file.enc)"
    echo "  decrypt <file>    Decrypt file (removes .enc extension)"
    echo
    echo "Examples:"
    echo "  $0 encrypt secrets.txt"
    echo "  $0 decrypt secrets.txt.enc"
}

if [ $# -lt 2 ]; then
    show_help
    exit 1
fi

COMMAND=$1
FILE=$2

case $COMMAND in
    encrypt|e)
        if [ ! -f "$FILE" ]; then
            echo "Error: File '$FILE' not found"
            exit 1
        fi

        OUTPUT="${FILE}.enc"

        if [ -f "$OUTPUT" ]; then
            echo "Warning: $OUTPUT already exists"
            read -p "Overwrite? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Cancelled"
                exit 0
            fi
        fi

        echo "Encrypting $FILE..."
        openssl enc -aes-256-cbc -salt -pbkdf2 -in "$FILE" -out "$OUTPUT"

        if [ $? -eq 0 ]; then
            echo "✓ Encrypted: $OUTPUT"
            read -p "Delete original file? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm "$FILE"
                echo "✓ Deleted: $FILE"
            fi
        else
            echo "✗ Encryption failed"
            exit 1
        fi
        ;;

    decrypt|d)
        if [ ! -f "$FILE" ]; then
            echo "Error: File '$FILE' not found"
            exit 1
        fi

        # Remove .enc extension
        if [[ "$FILE" == *.enc ]]; then
            OUTPUT="${FILE%.enc}"
        else
            OUTPUT="${FILE}.dec"
        fi

        if [ -f "$OUTPUT" ]; then
            echo "Warning: $OUTPUT already exists"
            read -p "Overwrite? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Cancelled"
                exit 0
            fi
        fi

        echo "Decrypting $FILE..."
        openssl enc -aes-256-cbc -d -pbkdf2 -in "$FILE" -out "$OUTPUT"

        if [ $? -eq 0 ]; then
            echo "✓ Decrypted: $OUTPUT"
            read -p "Delete encrypted file? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm "$FILE"
                echo "✓ Deleted: $FILE"
            fi
        else
            echo "✗ Decryption failed"
            # Remove failed output file if it exists
            [ -f "$OUTPUT" ] && rm "$OUTPUT"
            exit 1
        fi
        ;;

    *)
        echo "Error: Unknown command '$COMMAND'"
        echo
        show_help
        exit 1
        ;;
esac
