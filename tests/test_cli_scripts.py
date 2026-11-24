"""Los CLI de scripts/ funcionan tanto importados como invocados por ruta."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]


def _entorno(tmp_path):
    entorno = dict(os.environ)
    # El usuario no define PYTHONPATH: solo ejecuta el script desde la raíz.
    entorno.pop('PYTHONPATH', None)
    entorno['PRESTATEC_DATA_FILE'] = str(tmp_path / 'data.json')
    entorno['PRESTATEC_IDENTITY_FILE'] = str(tmp_path / 'identidades.json')
    return entorno


@pytest.mark.parametrize(
    'script', ['crear_demo.py', 'identificar.py', 'migrar.py', 'respaldar.py']
)
def test_CLI_se_invoca_desde_la_raiz_por_ruta_relativa(tmp_path, script):
    resultado = subprocess.run(
        [sys.executable, f'scripts/{script}', '--help'],
        cwd=RAIZ, env=_entorno(tmp_path), capture_output=True, text=True,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert 'usage:' in resultado.stdout


def test_CLI_crear_demo_crea_cuentas_sin_iniciar_el_servidor(tmp_path):
    datos = tmp_path / 'data.json'
    identidades = tmp_path / 'identidades.json'

    resultado = subprocess.run(
        [sys.executable, 'scripts/crear_demo.py', '--datos', str(datos),
         '--identidades', str(identidades)],
        cwd=RAIZ, env=_entorno(tmp_path), capture_output=True, text=True,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert sorted(json.loads(identidades.read_text(encoding='utf-8'))['credenciales']) == [
        'admin', 'celador', 'estudiante',
    ]
    assert any(
        u['documento'] == 'estudiante'
        for u in json.loads(datos.read_text(encoding='utf-8'))['usuarios']
    )
