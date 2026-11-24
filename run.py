"""Punto de entrada: python run.py"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from prestatec.web import PrestaTecApp

app = PrestaTecApp()

class RequestHandler(BaseHTTPRequestHandler):
    def _respond(self):
        length=int(self.headers.get('Content-Length',0))
        raw=self.rfile.read(length) if length else b''
        try: body=json.loads(raw.decode('utf-8')) if raw else {}
        except (UnicodeDecodeError,json.JSONDecodeError): body={}
        status,content,mime,filename=app.dispatch(self.command,self.path,body)
        self.send_response(status); self.send_header('Content-Type',mime); self.send_header('Content-Length',str(len(content)))
        if filename: self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
        self.end_headers(); self.wfile.write(content)
    do_GET=_respond
    do_POST=_respond
    do_PUT=_respond
    def log_message(self,fmt,*args): print('[PrestaTec] '+fmt%args)

if __name__=='__main__':
    print('\n  PrestaTec está listo: http://127.0.0.1:5080\n  Para detenerlo, presiona Ctrl + C.\n')
    ThreadingHTTPServer(('127.0.0.1',5080),RequestHandler).serve_forever()
