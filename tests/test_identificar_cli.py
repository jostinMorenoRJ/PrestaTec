"""SEC-03 / PER-01: alta explícita de credenciales sin texto plano ni sobrescritura."""
import json

from scripts.identificar import main


def test_cli_crea_credencial_hash_y_no_guarda_plano(tmp_path, monkeypatch):
    archivo = tmp_path / 'identidades.json'
    monkeypatch.setenv('PRESTATEC_ADMIN_PASSWORD', 'clave-de-prueba')

    assert main([
        'crear', 'gestor', '--rol', 'Encargado', '--archivo', str(archivo)
    ]) == 0

    texto = archivo.read_text(encoding='utf-8')
    assert 'clave-de-prueba' not in texto
    datos = json.loads(texto)
    credencial = datos['credenciales']['gestor']
    assert credencial['rol'] == 'Encargado'
    assert credencial['iteraciones'] >= 100000
    assert len(credencial['hash']) == 64


def test_cli_no_sobrescribe_credencial_existente(tmp_path, monkeypatch):
    archivo = tmp_path / 'identidades.json'
    args = ['crear', 'gestor', '--rol', 'Encargado', '--archivo', str(archivo)]

    monkeypatch.setenv('PRESTATEC_ADMIN_PASSWORD', 'primera-clave')
    assert main(args) == 0
    original = archivo.read_text(encoding='utf-8')

    monkeypatch.setenv('PRESTATEC_ADMIN_PASSWORD', 'segunda-clave')
    assert main(args) == 1
    assert archivo.read_text(encoding='utf-8') == original
