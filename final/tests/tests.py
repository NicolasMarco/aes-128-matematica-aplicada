# tests.py -- Validacion del nucleo AES-128 y modos ECB/CBC contra vectores
# oficiales del NIST (FIPS-197 y SP 800-38A).
#
# Ejecutar desde la raíz del proyecto:  python -m tests.tests

from aes.core import encrypt_block, decrypt_block
from aes.modes import ecb_encrypt, ecb_decrypt, cbc_encrypt, cbc_decrypt


def check(descripcion, obtenido, esperado):
    ok = obtenido == esperado
    estado = "[PASS]" if ok else "[FAIL]"
    print(f"  {estado}  {descripcion}")
    if not ok:
        print(f"         esperado: {esperado.hex()}")
        print(f"         obtenido: {obtenido.hex()}")
    return ok


# ---------------------------------------------------------------------------
# FIPS-197 Apendice B -- vector de referencia para el bloque unico
# ---------------------------------------------------------------------------

def test_fips197_apendice_b():
    print("\n[FIPS-197 Apendice B - bloque unico]")
    key   = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    plain = bytes.fromhex("3243f6a8885a308d313198a2e0370734")
    expected_ct = bytes.fromhex("3925841d02dc09fbdc118597196a0b32")

    ct = encrypt_block(plain, key)
    check("encrypt_block -> ciphertext correcto", ct, expected_ct)
    check("decrypt_block -> plaintext recuperado", decrypt_block(ct, key), plain)


# ---------------------------------------------------------------------------
# FIPS-197 Apendice C.1 -- AES-128
# ---------------------------------------------------------------------------

def test_fips197_apendice_c1():
    print("\n[FIPS-197 Apendice C.1 - AES-128]")
    key   = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    plain = bytes.fromhex("00112233445566778899aabbccddeeff")
    expected_ct = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")

    ct = encrypt_block(plain, key)
    check("encrypt_block -> ciphertext correcto", ct, expected_ct)
    check("decrypt_block -> plaintext recuperado", decrypt_block(ct, key), plain)


# ---------------------------------------------------------------------------
# NIST SP 800-38A -- ECB-AES128 (4 bloques)
# ---------------------------------------------------------------------------

def test_ecb_sp80038a():
    print("\n[NIST SP 800-38A - ECB-AES128, 4 bloques]")
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")

    plaintexts = [
        bytes.fromhex("6bc1bee22e409f96e93d7e117393172a"),
        bytes.fromhex("ae2d8a571e03ac9c9eb76fac45af8e51"),
        bytes.fromhex("30c81c46a35ce411e5fbc1191a0a52ef"),
        bytes.fromhex("f69f2445df4f9b17ad2b417be66c3710"),
    ]
    ciphertexts = [
        bytes.fromhex("3ad77bb40d7a3660a89ecaf32466ef97"),
        bytes.fromhex("f5d3d58503b9699de785895a96fdbaaf"),
        bytes.fromhex("43b1cd7f598ece23881b00e3ed030688"),
        bytes.fromhex("7b0c785e27e8ad3f8223207104725dd4"),
    ]

    for i, (pt, ct_exp) in enumerate(zip(plaintexts, ciphertexts)):
        ct = encrypt_block(pt, key)
        check(f"bloque {i + 1} encrypt", ct, ct_exp)
        check(f"bloque {i + 1} decrypt", decrypt_block(ct, key), pt)

    plain_concat = b"".join(plaintexts)
    ct_concat_exp = b"".join(ciphertexts)
    ct_mode = ecb_encrypt(plain_concat, key)
    check("ecb_encrypt -> primeros 64 bytes correctos", ct_mode[:64], ct_concat_exp)
    check("ecb_decrypt -> plaintext recuperado", ecb_decrypt(ct_mode, key), plain_concat)


# ---------------------------------------------------------------------------
# NIST SP 800-38A -- CBC-AES128 (4 bloques)
# ---------------------------------------------------------------------------

def test_cbc_sp80038a():
    print("\n[NIST SP 800-38A - CBC-AES128, 4 bloques]")
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    iv  = bytes.fromhex("000102030405060708090a0b0c0d0e0f")

    plaintexts = [
        bytes.fromhex("6bc1bee22e409f96e93d7e117393172a"),
        bytes.fromhex("ae2d8a571e03ac9c9eb76fac45af8e51"),
        bytes.fromhex("30c81c46a35ce411e5fbc1191a0a52ef"),
        bytes.fromhex("f69f2445df4f9b17ad2b417be66c3710"),
    ]
    ciphertexts = [
        bytes.fromhex("7649abac8119b246cee98e9b12e9197d"),
        bytes.fromhex("5086cb9b507219ee95db113a917678b2"),
        bytes.fromhex("73bed6b8e3c1743b7116e69e22229516"),
        bytes.fromhex("3ff1caa1681fac09120eca307586e1a7"),
    ]

    plain_concat = b"".join(plaintexts)
    ct_concat_exp = b"".join(ciphertexts)

    ct_mode = cbc_encrypt(plain_concat, key, iv)
    check("cbc_encrypt -> primeros 64 bytes correctos", ct_mode[:64], ct_concat_exp)
    check("cbc_decrypt -> plaintext recuperado", cbc_decrypt(ct_mode, key, iv), plain_concat)


# ---------------------------------------------------------------------------
# Prueba de ida y vuelta con texto arbitrario
# ---------------------------------------------------------------------------

def test_roundtrip():
    print("\n[Prueba de ida y vuelta - texto con padding]")
    key = bytes.fromhex("deadbeefcafebabe0123456789abcdef")
    iv  = bytes.fromhex("0f0e0d0c0b0a09080706050403020100")
    msg = b"Hola AES! Este mensaje no es multiplo de 16 bytes."

    ct = ecb_encrypt(msg, key)
    check("ECB roundtrip -> mensaje recuperado", ecb_decrypt(ct, key), msg)

    ct = cbc_encrypt(msg, key, iv)
    check("CBC roundtrip -> mensaje recuperado", cbc_decrypt(ct, key, iv), msg)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 55)
    print("  Tests AES-128  (FIPS-197 + SP 800-38A)")
    print("=" * 55)

    for t in [
        test_fips197_apendice_b,
        test_fips197_apendice_c1,
        test_ecb_sp80038a,
        test_cbc_sp80038a,
        test_roundtrip,
    ]:
        t()

    print("\n" + "=" * 55)
    print("  Ejecutar con:  python -m tests.tests")
    print("=" * 55)
