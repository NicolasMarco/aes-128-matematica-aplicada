# AES-128 — Implementación desde cero en Python

Implementación del algoritmo de cifrado **AES-128** (Advanced Encryption Standard) escrita completamente en Python puro, sin librerías criptográficas externas. Sigue la especificación oficial **FIPS-197** e incluye los modos de operación **ECB** y **CBC**.

Desarrollado como trabajo práctico de la materia Matemática Aplicada.

---

## ¿Qué es AES?

AES es un algoritmo de cifrado simétrico por bloques adoptado como estándar por el NIST en 2001. Trabaja con bloques de **16 bytes (128 bits)** y admite claves de 128, 192 o 256 bits. Esta implementación usa claves de **128 bits**.

Cada bloque pasa por **10 rondas** de cuatro transformaciones:
- **SubBytes** — sustitución no lineal con la S-Box
- **ShiftRows** — rotación de filas del estado
- **MixColumns** — mezcla de columnas en GF(2⁸)
- **AddRoundKey** — XOR con la subclave de ronda

---

## Estructura del proyecto

```
AES - Criptografia/
├── aes/
│   ├── core.py        # Núcleo AES-128: transformaciones y key expansion (FIPS-197)
│   └── modes.py       # Modos ECB y CBC con padding PKCS#7
├── demo/
│   └── demo_ecb_cbc.py  # Demo visual: cifra una imagen BMP y compara ECB vs CBC
├── docs/              # Informe y presentación
├── tests/
│   └── tests.py       # Vectores de prueba oficiales NIST (FIPS-197 + SP 800-38A)
├── explicacion_interactiva.ipynb  # Notebook paso a paso del algoritmo
├── cli.py             # Interfaz de línea de comandos para cifrar/descifrar archivos
└── .gitignore
```

---

## Requisitos

Solo Python 3.8 o superior. No requiere instalar ninguna dependencia.

---

## Uso

> Todos los comandos se ejecutan desde la **raíz del proyecto**.

### CLI — Cifrar y descifrar archivos

```bash
# Cifrar (modo CBC por defecto)
python cli.py encrypt <archivo_entrada> <archivo_salida> --key <32 chars hex>

# Cifrar en modo ECB
python cli.py encrypt <archivo_entrada> <archivo_salida> --key <32 chars hex> --mode ecb

# Descifrar
python cli.py decrypt <archivo_cifrado> <archivo_salida> --key <32 chars hex>

# Cifrar con IV personalizado (CBC)
python cli.py encrypt entrada.bin salida.bin --key 2b7e151628aed2a6abf7158809cf4f3c --mode cbc --iv 000102030405060708090a0b0c0d0e0f
```

**Parámetros:**

| Parámetro | Descripción |
|-----------|-------------|
| `encrypt` / `decrypt` | Acción a realizar |
| `--key` | Clave de 128 bits como 32 caracteres hexadecimales (obligatorio) |
| `--mode ecb\|cbc` | Modo de operación (por defecto: `cbc`) |
| `--iv` | Vector de inicialización de 32 chars hex para CBC (por defecto: 16 bytes en cero) |

**Ejemplo rápido:**

```bash
python cli.py encrypt demo/original.bmp foto_cifrada.bin --key 2b7e151628aed2a6abf7158809cf4f3c
python cli.py decrypt foto_cifrada.bin foto_recuperada.bmp --key 2b7e151628aed2a6abf7158809cf4f3c
```

---

### Demo visual — ECB vs CBC

Genera tres imágenes BMP para comparar visualmente la debilidad de ECB frente a CBC:

```bash
python -m demo.demo_ecb_cbc
```

Produce en `demo/`:
- `original.bmp` — imagen con patrón de bloques de color
- `ecb_encrypted.bmp` — cifrada con ECB: **los patrones siguen visibles**
- `cbc_encrypted.bmp` — cifrada con CBC: **parece ruido aleatorio**

Esto ilustra por qué ECB no es seguro para datos con patrones repetidos.

---

### Tests

Valida la implementación contra los vectores oficiales del NIST:

```bash
python -m tests.tests
```

Cubre:
- FIPS-197 Apéndice B y C.1 (bloque único)
- NIST SP 800-38A (ECB y CBC con 4 bloques)
- Prueba de ida y vuelta con padding PKCS#7

---

### Notebook interactivo

Para explorar el algoritmo paso a paso:

```bash
jupyter notebook explicacion_interactiva.ipynb
```

---

## ECB vs CBC

| | ECB | CBC |
|---|---|---|
| Cada bloque | Se cifra de forma independiente | Depende del bloque anterior (XOR con ciphertext previo) |
| Bloques iguales | Producen el mismo ciphertext | Producen ciphertext distinto |
| IV necesario | No | Sí |
| Seguro para datos con patrones | No | Sí |

---

## Modos de padding

Se usa **PKCS#7**: si el mensaje no es múltiplo de 16 bytes, se agregan N bytes de valor N hasta completar el bloque. Al descifrar, el padding se verifica y se elimina.
