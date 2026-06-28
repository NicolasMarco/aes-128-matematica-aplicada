# demo_ecb_cbc.py — Cifra una imagen BMP en modos ECB y CBC para comparación visual.
#
# Genera tres archivos en la carpeta demo/:
#   original.bmp       — imagen original con patrón de bloques de color
#   ecb_encrypted.bmp  — cifrada con ECB: los patrones originales siguen visibles
#   cbc_encrypted.bmp  — cifrada con CBC: parece ruido aleatorio
#
# Ejecutar desde la raíz del proyecto:  python -m demo.demo_ecb_cbc

import os
import struct

from aes.modes import ecb_encrypt, cbc_encrypt

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Generación de BMP (24 bits, sin librerías externas)
# ---------------------------------------------------------------------------

def make_bmp(width, height, get_pixel):
    """Crea un BMP 24-bit en memoria.
    get_pixel(x, y) debe retornar (R, G, B) con valores 0-255.
    BMP almacena filas de abajo hacia arriba y canales en orden BGR."""
    row_stride = (width * 3 + 3) & ~3          # cada fila se padea a múltiplo de 4
    pixel_data_size = row_stride * height
    file_size = 54 + pixel_data_size

    # Encabezado de archivo (14 bytes)
    header  = b"BM"
    header += struct.pack("<I", file_size)       # tamaño del archivo
    header += struct.pack("<HH", 0, 0)           # reservado
    header += struct.pack("<I", 54)              # offset al inicio de los píxeles

    # Encabezado DIB BITMAPINFOHEADER (40 bytes)
    dib  = struct.pack("<I", 40)                 # tamaño del encabezado
    dib += struct.pack("<ii", width, height)     # dimensiones (height > 0 → bottom-up)
    dib += struct.pack("<HH", 1, 24)             # planos de color, bits por píxel
    dib += struct.pack("<I", 0)                  # compresión: BI_RGB (sin compresión)
    dib += struct.pack("<I", 0)                  # tamaño imagen (0 válido para BI_RGB)
    dib += struct.pack("<ii", 0, 0)              # resolución x/y (no importa)
    dib += struct.pack("<II", 0, 0)              # colores en tabla, colores importantes

    # Datos de píxeles (de abajo hacia arriba, BGR)
    pixel_data = bytearray()
    for y in range(height - 1, -1, -1):
        row = bytearray()
        for x in range(width):
            r, g, b = get_pixel(x, y)
            row += bytes([b & 0xFF, g & 0xFF, r & 0xFF])
        # Pad de fila a múltiplo de 4 bytes
        row += b"\x00" * ((-len(row)) % 4)
        pixel_data += row

    return header + dib + bytes(pixel_data)


def split_bmp(bmp_data):
    """Separa un BMP en (encabezado, datos de píxeles) leyendo el offset del encabezado."""
    offset = struct.unpack_from("<I", bmp_data, 10)[0]
    return bmp_data[:offset], bmp_data[offset:]


# ---------------------------------------------------------------------------
# Imagen de prueba: patrón de bloques de colores (4×4 bloques de 32×32 px)
# ---------------------------------------------------------------------------

COLORES = [
    (220,  50,  50),   # rojo
    ( 50, 200,  50),   # verde
    ( 50,  50, 220),   # azul
    (220, 220,  50),   # amarillo
    ( 50, 200, 200),   # cian
    (200,  50, 200),   # magenta
    (200, 100,  40),   # naranja
    (100,  40, 200),   # violeta
    (220, 220, 220),   # gris claro
    ( 30,  30,  30),   # gris oscuro
    (  0, 128, 255),   # celeste
    (255, 128,   0),   # naranja brillante
    (128,   0,   0),   # rojo oscuro
    (  0, 128,   0),   # verde oscuro
    (  0,   0, 128),   # azul oscuro
    (128, 128,   0),   # oliva
]


def patron_bloques(x, y, block_px=32, cols=4):
    bx = x // block_px
    by = y // block_px
    return COLORES[(by * cols + bx) % len(COLORES)]


# ---------------------------------------------------------------------------
# Demo principal
# ---------------------------------------------------------------------------

def demo():
    WIDTH, HEIGHT = 128, 128
    BLOCK_PX = 32

    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    iv  = bytes.fromhex("000102030405060708090a0b0c0d0e0f")

    print(f"Imagen: {WIDTH}x{HEIGHT} px, patrón de bloques {BLOCK_PX}x{BLOCK_PX}")

    # --- Imagen original ---
    original_bmp = make_bmp(WIDTH, HEIGHT, lambda x, y: patron_bloques(x, y, BLOCK_PX))
    encabezado, pixel_data = split_bmp(original_bmp)
    print(f"Datos de píxeles: {len(pixel_data)} bytes ({len(pixel_data) // 16} bloques AES)")

    # --- ECB: mismos bloques de píxeles → mismo ciphertext → patrón visible ---
    ecb_pixels = ecb_encrypt(pixel_data, key)
    ecb_bmp = encabezado + ecb_pixels[:len(pixel_data)]

    # --- CBC: cada bloque depende del anterior → parece ruido ---
    cbc_pixels = cbc_encrypt(pixel_data, key, iv)
    cbc_bmp = encabezado + cbc_pixels[:len(pixel_data)]

    # --- Guardar archivos en la carpeta demo/ ---
    def save(filename, data):
        path = os.path.join(DEMO_DIR, filename)
        with open(path, "wb") as f:
            f.write(data)
        print(f"  {path}")

    print("\nArchivos generados:")
    save("original.bmp", original_bmp)
    save("ecb_encrypted.bmp", ecb_bmp)
    save("cbc_encrypted.bmp", cbc_bmp)

    print()
    print("Conclusión: ECB cifra cada bloque de 16 bytes de forma independiente,")
    print("por lo que bloques de píxeles idénticos producen ciphertext idéntico.")
    print("CBC encadena cada bloque con el anterior, eliminando los patrones.")


if __name__ == "__main__":
    demo()
