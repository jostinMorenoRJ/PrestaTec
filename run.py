"""Punto de entrada: python run.py"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prestatec.web import PrestaTecApp


app = PrestaTecApp()


def crear_handler(aplicacion):
    """Construye el handler HTTP para una instancia concreta de la aplicación."""

    class RequestHandler(BaseHTTPRequestHandler):
        def _respond(self):
            longitud = int(self.headers.get('Content-Length', 0))
            crudo = self.rfile.read(longitud) if longitud else b''
            try:
                cuerpo = json.loads(crudo.decode('utf-8')) if crudo else {}
            except (UnicodeDecodeError, json.JSONDecodeError):
                cuerpo = {}

            cabeceras = dict(self.headers.items())
            estado, contenido, mime, nombre_archivo = aplicacion.dispatch(
                self.command, self.path, cuerpo, cabeceras
            )
            self.send_response(estado)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(contenido)))
            for clave, valor in getattr(aplicacion, 'ultimos_headers', {}).items():
                self.send_header(clave, valor)
            if nombre_archivo:
                self.send_header(
                    'Content-Disposition', f'attachment; filename="{nombre_archivo}"'
                )
            self.end_headers()
            self.wfile.write(contenido)

        do_GET = _respond
        do_POST = _respond
        do_PUT = _respond

        def log_message(self, formato, *args):
            print('[PrestaTec] ' + formato % args)

    return RequestHandler


if __name__ == '__main__':
    print(
        '\n  PrestaTec está listo: http://127.0.0.1:5080\n'
        '  Para detenerlo, presiona Ctrl + C.\n'
    )
    ThreadingHTTPServer(('127.0.0.1', 5080), crear_handler(app)).serve_forever()
