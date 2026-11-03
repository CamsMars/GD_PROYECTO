# Corre todos los scripts en orden
#   python armar_lago.py               descarga todo
#   python armar_lago.py --usar-cache  usa lo que ya esta en datos_crudos/

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PASOS = [
    "ingesta/f01_distritos.py",   # primero, porque los demas usan los distritos
    "ingesta/f06_tracts.py",      # antes de f05
    "ingesta/f05_censo.py",
    "ingesta/f02_311.py",
    "ingesta/f03_siniestros.py",
    "ingesta/f04_septa.py",
    "construir_lago.py",
    "verificar_privacidad.py",
]

for paso in PASOS:
    print(f"\n--- {paso} ---", flush=True)
    argumentos = sys.argv[1:] if paso.startswith("ingesta/") else []
    resultado = subprocess.run([sys.executable, str(RAIZ / paso)] + argumentos, cwd=RAIZ)
    if resultado.returncode != 0:
        sys.exit(f"Error en {paso}")

print("\nListo, lago armado")
