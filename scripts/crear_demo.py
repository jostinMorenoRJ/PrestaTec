"""Prepara las cuentas de demostración sin iniciar el servidor (DEMO-01..04).

Uso:
    python scripts/crear_demo.py

Es una acción explícita: `python run.py` no crea credenciales por su cuenta.
Las contraseñas son solo de demostración y nunca se imprimen.
"""
import argparse
import json
import sys
from pathlib import Path

# Al invocar `python scripts/crear_demo.py`, sys.path[0] es scripts/, no la raíz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prestatec.demo import preparar_demo
from prestatec.identidad import AlmacenCredenciales
from prestatec.service import InventoryService


def main(argv=None):
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument('--datos', default=None, help='ruta a data.json')
    analizador.add_argument(
        '--identidades', default=None, help='ruta a identidades.json'
    )
    args = analizador.parse_args(argv)

    resultado = preparar_demo(
        servicio=InventoryService(args.datos),
        almacen=AlmacenCredenciales(args.identidades),
    )
    print(json.dumps({
        'credenciales_creadas': resultado['credenciales'],
        'usuarios_creados': resultado['usuarios'],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
