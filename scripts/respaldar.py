"""Operaciones explícitas de respaldo y restauración.

Uso:
    py scripts/respaldar.py crear data.json [--directorio backups]
    py scripts/respaldar.py restaurar <manifiesto.json> <destino> [--confirmar]

La opción `--confirmar` sustituye la confirmación institucional mientras no
exista una interfaz de aprobación; queda registrada en la evidencia del change.
"""
import argparse
import json
import sys
from pathlib import Path

# Al invocar `python scripts/respaldar.py`, sys.path[0] es scripts/, no la raíz.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prestatec.backup import BackupService
from prestatec.errors import BusinessError


def main(argv=None):
    analizador = argparse.ArgumentParser(description=__doc__)
    subcomandos = analizador.add_subparsers(dest='accion', required=True)

    crear = subcomandos.add_parser('crear', help='crea una copia verificable')
    crear.add_argument('origen', nargs='?', default='data.json')
    crear.add_argument('--directorio', default=None)

    restaurar = subcomandos.add_parser('restaurar', help='restaura desde una copia validada')
    restaurar.add_argument('manifiesto')
    restaurar.add_argument('destino')
    restaurar.add_argument('--confirmar', action='store_true')

    args = analizador.parse_args(argv)
    servicio = BackupService()
    try:
        if args.accion == 'crear':
            resultado = servicio.crear(args.origen, directorio=args.directorio)
        else:
            resultado = servicio.restaurar(
                args.manifiesto, args.destino, confirmar=args.confirmar
            )
    except BusinessError as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    print(json.dumps(resultado, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
