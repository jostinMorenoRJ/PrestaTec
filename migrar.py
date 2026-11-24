"""Migración explícita de `data.json` a SQLite.

Uso: `py migrar.py [origen] [destino] [respaldo] [--forzar]`.
Sin argumentos usa `data.json`, `prestatec.db` y `data.json.bak`.
Nunca sobrescribe archivos existentes sin `--forzar`.
"""
import argparse
import json
import sys

from prestatec.errors import BusinessError
from prestatec.migracion import migrar_desde_json


def main(argv=None):
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument('origen', nargs='?', default='data.json')
    analizador.add_argument('destino', nargs='?', default='prestatec.db')
    analizador.add_argument('respaldo', nargs='?', default=None)
    analizador.add_argument(
        '--forzar', action='store_true',
        help='permite reemplazar un destino o respaldo existente',
    )
    args = analizador.parse_args(argv)
    try:
        informe = migrar_desde_json(
            args.origen, args.destino, args.respaldo, sobrescribir=args.forzar
        )
    except BusinessError as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    print(json.dumps(informe, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
