# AES-128 — Instrucciones para ejecutar el proyecto

Implementación del algoritmo **AES-128** desde cero en Python puro (sin librerías criptográficas externas), con modos de operación **ECB** y **CBC**.

**Único requisito:** Python 3.8 o superior. No se instala ningún paquete adicional.

---

## Requisito previo — verificar Python

Abrí una terminal (cmd, PowerShell o bash) y ejecutá:

```
python --version
```

Tiene que mostrar `Python 3.8.x` o superior. Si el comando no se reconoce, instalá Python desde https://python.org/downloads.

> Todos los comandos siguientes se ejecutan **desde la carpeta `final/`** (donde está este archivo).

---

## Demo 1 — Verificar la implementación con vectores NIST

Valida que el núcleo AES esté correctamente implementado contra los vectores de prueba oficiales del NIST (FIPS-197 y SP 800-38A).

```
python -m tests.tests
```

**Salida esperada:**

```
[PASS] FIPS-197 Apendice B — cifrado de bloque unico
[PASS] FIPS-197 Apendice C.1 — AES-128 key expansion
[PASS] SP 800-38A — ECB-AES128 Encrypt (4 bloques)
[PASS] SP 800-38A — ECB-AES128 Decrypt (4 bloques)
[PASS] SP 800-38A — CBC-AES128 Encrypt (4 bloques)
[PASS] SP 800-38A — CBC-AES128 Decrypt (4 bloques)
[PASS] Round-trip con padding PKCS7
Todos los tests pasaron.
```

Si algún test falla, la implementación tiene un error. Si todos pasan, el algoritmo está correctamente implementado.

---

## Demo 2 — Comparación visual ECB vs CBC

Cifra una imagen BMP con cada modo y guarda el resultado. Muestra visualmente por qué ECB es inseguro cuando los datos tienen patrones repetidos.

```
python -m demo.demo_ecb_cbc
```

**Salida esperada:**

```
Imagen: 128x128 px, patron de bloques 32x32
Datos de pixeles: 49152 bytes (3072 bloques AES)

Archivos generados:
  ...\demo\original.bmp
  ...\demo\ecb_encrypted.bmp
  ...\demo\cbc_encrypted.bmp

Conclusion: ECB cifra cada bloque de 16 bytes de forma independiente,
por lo que bloques de pixeles identicos producen ciphertext identico.
CBC encadena cada bloque con el anterior, eliminando los patrones.
```

**Abrí los tres archivos BMP** con cualquier visor de imágenes (doble clic en Windows):

| Archivo | Qué se ve |
|---------|-----------|
| `demo/original.bmp` | Imagen con 16 bloques de colores bien definidos |
| `demo/ecb_encrypted.bmp` | Cifrada con ECB: **los bloques de color siguen distinguiéndose** |
| `demo/cbc_encrypted.bmp` | Cifrada con CBC: **parece ruido aleatorio** |

Esto ilustra la debilidad de ECB: bloques de píxeles idénticos producen siempre el mismo ciphertext, preservando los patrones de la imagen original.

---

## Demo 3 — CLI: cifrar y descifrar un archivo

Primero ejecutá la Demo 2 para tener `demo/original.bmp` disponible. Luego:

### Cifrar

```
python cli.py encrypt demo/original.bmp demo/foto_cifrada.bin --key 2b7e151628aed2a6abf7158809cf4f3c
```

**Salida esperada:**

```
Aviso: usando IV de ceros. Para uso real, proveer un IV aleatorio con --iv.
ENCRYPT [CBC]  'demo/original.bmp'  ->  'demo/foto_cifrada.bin'  (49206 -> 49216 bytes)
```

### Descifrar

```
python cli.py decrypt demo/foto_cifrada.bin demo/foto_recuperada.bmp --key 2b7e151628aed2a6abf7158809cf4f3c
```

**Salida esperada:**

```
Aviso: usando IV de ceros. Para uso real, proveer un IV aleatorio con --iv.
DECRYPT [CBC]  'demo/foto_cifrada.bin'  ->  'demo/foto_recuperada.bmp'  (49216 -> 49206 bytes)
```

Abrí `demo/foto_recuperada.bmp` — debe ser idéntica a `demo/original.bmp`.

### Parámetros disponibles

| Parámetro | Descripción |
|-----------|-------------|
| `encrypt` / `decrypt` | Acción |
| `--key` | Clave de 128 bits: exactamente 32 caracteres hexadecimales (obligatorio) |
| `--mode ecb\|cbc` | Modo de operación (por defecto: `cbc`) |
| `--iv` | Vector de inicialización para CBC: 32 chars hex (por defecto: 16 bytes en cero) |

### Cifrar con modo ECB

```
python cli.py encrypt demo/original.bmp demo/foto_ecb.bin --key 2b7e151628aed2a6abf7158809cf4f3c --mode ecb
```

### Usar cualquier otro archivo

El CLI acepta cualquier archivo binario como entrada:

```
python cli.py encrypt docs/Estándar de Cifrado Avanzado.pdf informe_cifrado.bin --key 2b7e151628aed2a6abf7158809cf4f3c
```

---

## Estructura del proyecto

```
final/
├── INSTRUCCIONES.md          <- este archivo
├── aes/
│   ├── core.py               <- núcleo AES-128: SubBytes, ShiftRows, MixColumns, AddRoundKey
│   └── modes.py              <- modos ECB y CBC con padding PKCS#7
├── cli.py                    <- interfaz de línea de comandos
├── demo/
│   └── demo_ecb_cbc.py       <- demo visual ECB vs CBC
├── tests/
│   └── tests.py              <- vectores oficiales NIST (FIPS-197 + SP 800-38A)
└── docs/
    └── Estándar de Cifrado Avanzado.pdf   <- informe del trabajo
```
