"""Alta explícita de credenciales para el proveedor local (SEC-03, PER-01).

Uso:
    py identificar.py crear <documento> --rol Encargado

Roles permitidos: Consulta, Guarda y Encargado. `Estudiante`/`Docente` se
aceptan como alias de Consulta. La contraseña se pide por consola o, solo para
automatización, se lee de `PRESTATEC_ADMIN_PASSWORD`. Nunca se guarda en texto
plano ni se muestra.
"""
import argparse
import getpass
import json
import os
import sys

from prestatec.errors import BusinessError
from prestatec.identidad import AlmacenCredenciales, normalizar_rol


def main(argv=None):
    analizador = argparse.ArgumentParser(description=__doc__)
    subcomandos = analizador.add_subparsers(dest='accion', required=True)
    crear = subcomandos.add_parser('crear', help='crea una credencial')
    crear.add_argument('documento')
    crear.add_argument(
        '--rol', default='Encargado',
        help='Consulta, Guarda o Encargado (alias: Estudiante, Docente)',
    )
    crear.add_argument('--archivo', default=None)

    args = analizador.parse_args(argv)
    contraseña = os.getenv('PRESTATEC_ADMIN_PASSWORD') or getpass.getpass(
        'Contraseña: '
    )
    almacen = AlmacenCredenciales(args.archivo)
    try:
        almacen.crear(args.documento, contraseña, args.rol)
    except BusinessError as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    print(json.dumps({
        'documento': args.documento.strip(),
        'rol': normalizar_rol(args.rol),
        'archivo': str(almacen.ruta),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
