#!/usr/bin/env python3
# cli.py — Interfaz de línea de comandos para cifrar/descifrar archivos con AES-128.
#
# Uso:
#   python cli.py encrypt <entrada> <salida> --key <32 hex> [--mode ecb|cbc] [--iv <32 hex>]
#   python cli.py decrypt <entrada> <salida> --key <32 hex> [--mode ecb|cbc] [--iv <32 hex>]
#
# Ejemplos:
#   python cli.py encrypt foto.bmp foto_enc.bin --key 2b7e151628aed2a6abf7158809cf4f3c --mode cbc
#   python cli.py decrypt foto_enc.bin foto_dec.bmp --key 2b7e151628aed2a6abf7158809cf4f3c --mode cbc

import argparse
import os
import sys

from aes.modes import ecb_encrypt, ecb_decrypt, cbc_encrypt, cbc_decrypt


def parse_hex16(value, name):
    """Parsea un string hexadecimal de 32 caracteres (= 16 bytes)."""
    value = value.replace(" ", "").lower()
    if len(value) != 32:
        print(f"Error: {name} debe tener exactamente 32 caracteres hex (128 bits).", file=sys.stderr)
        sys.exit(1)
    try:
        return bytes.fromhex(value)
    except ValueError:
        print(f"Error: {name} contiene caracteres no hexadecimales.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Cifrado/descifrado de archivos con AES-128 (ECB o CBC)."
    )
    parser.add_argument("accion", choices=["encrypt", "decrypt"], help="Acción a realizar")
    parser.add_argument("entrada", help="Archivo de entrada")
    parser.add_argument("salida", help="Archivo de salida")
    parser.add_argument("--key", required=True, metavar="HEX32",
                        help="Clave de 128 bits como 32 caracteres hexadecimales")
    parser.add_argument("--mode", choices=["ecb", "cbc"], default="cbc",
                        help="Modo de operación (por defecto: cbc)")
    parser.add_argument("--iv", metavar="HEX32",
                        help="IV para CBC como 32 caracteres hex (por defecto: 16 bytes en cero)")

    args = parser.parse_args()

    key = parse_hex16(args.key, "La clave (--key)")

    iv = bytes(16)  # IV por defecto: 16 bytes en 0x00
    if args.mode == "cbc":
        if args.iv:
            iv = parse_hex16(args.iv, "El IV (--iv)")
        else:
            print("Aviso: usando IV de ceros. Para uso real, proveer un IV aleatorio con --iv.",
                  file=sys.stderr)

    if not os.path.exists(args.entrada):
        print(f"Error: el archivo '{args.entrada}' no existe.", file=sys.stderr)
        sys.exit(1)

    with open(args.entrada, "rb") as f:
        data = f.read()

    try:
        if args.accion == "encrypt":
            resultado = ecb_encrypt(data, key) if args.mode == "ecb" else cbc_encrypt(data, key, iv)
        else:
            resultado = ecb_decrypt(data, key) if args.mode == "ecb" else cbc_decrypt(data, key, iv)
    except Exception as e:
        print(f"Error durante {args.accion}: {e}", file=sys.stderr)
        sys.exit(1)

    with open(args.salida, "wb") as f:
        f.write(resultado)

    modo = args.mode.upper()
    print(f"{args.accion.upper()} [{modo}]  '{args.entrada}'  ->  '{args.salida}'  ({len(data)} -> {len(resultado)} bytes)")


if __name__ == "__main__":
    main()
