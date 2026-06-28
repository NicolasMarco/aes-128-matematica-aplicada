# modes.py — Modos de operación ECB y CBC sobre el núcleo AES-128.
# Incluye padding/unpadding PKCS#7.

from aes.core import encrypt_block, decrypt_block


# ---------------------------------------------------------------------------
# PKCS#7 padding
# ---------------------------------------------------------------------------

def pkcs7_pad(data, block_size=16):
    """Agrega N bytes de valor N hasta completar el siguiente múltiplo de block_size."""
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data):
    """Remueve el padding PKCS#7. Lanza ValueError si el padding es inválido."""
    if not data:
        raise ValueError("Datos vacíos")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError(f"Padding inválido: valor {pad_len}")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Padding PKCS#7 inconsistente")
    return data[:-pad_len]


# ---------------------------------------------------------------------------
# ECB — Electronic Codebook
# ---------------------------------------------------------------------------

def ecb_encrypt(plaintext, key):
    """Cifra plaintext (bytes) con AES-128 en modo ECB."""
    padded = pkcs7_pad(plaintext)
    ciphertext = b""
    for i in range(0, len(padded), 16):
        ciphertext += encrypt_block(padded[i:i + 16], key)
    return ciphertext


def ecb_decrypt(ciphertext, key):
    """Descifra ciphertext (bytes) con AES-128 en modo ECB."""
    if len(ciphertext) % 16 != 0:
        raise ValueError("El texto cifrado debe ser múltiplo de 16 bytes")
    plaintext = b""
    for i in range(0, len(ciphertext), 16):
        plaintext += decrypt_block(ciphertext[i:i + 16], key)
    return pkcs7_unpad(plaintext)


# ---------------------------------------------------------------------------
# CBC — Cipher Block Chaining
# ---------------------------------------------------------------------------

def cbc_encrypt(plaintext, key, iv):
    """Cifra plaintext (bytes) con AES-128 en modo CBC.
    iv debe ser exactamente 16 bytes."""
    if len(iv) != 16:
        raise ValueError("El IV debe ser de 16 bytes")
    padded = pkcs7_pad(plaintext)
    ciphertext = b""
    prev = iv
    for i in range(0, len(padded), 16):
        block = bytes(a ^ b for a, b in zip(padded[i:i + 16], prev))
        encrypted = encrypt_block(block, key)
        ciphertext += encrypted
        prev = encrypted
    return ciphertext


def cbc_decrypt(ciphertext, key, iv):
    """Descifra ciphertext (bytes) con AES-128 en modo CBC.
    iv debe ser exactamente 16 bytes."""
    if len(iv) != 16:
        raise ValueError("El IV debe ser de 16 bytes")
    if len(ciphertext) % 16 != 0:
        raise ValueError("El texto cifrado debe ser múltiplo de 16 bytes")
    plaintext = b""
    prev = iv
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i + 16]
        decrypted = decrypt_block(block, key)
        plaintext += bytes(a ^ b for a, b in zip(decrypted, prev))
        prev = block
    return pkcs7_unpad(plaintext)
