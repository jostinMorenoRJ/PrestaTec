"""Reglas de negocio de PrestaTec y persistencia sencilla en JSON."""
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

class BusinessError(Exception):
    """Error de validación o regla de negocio."""

class InventoryService:
    def __init__(self, data_file, seed=True):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()
        if seed and not self.data['equipos'] and not self.data['usuarios']:
            self._seed(); self._save()

    def _load(self):
        if self.data_file.exists():
            try:
                data = json.loads(self.data_file.read_text(encoding='utf-8'))
                # Compatibilidad con el JSON PascalCase del proyecto C# original.
                if 'Equipos' in data:
                    data = {
                        'equipos': [{'id':x.get('Id',''),'tipo':x.get('Tipo','Portátil'),'nombre':x.get('Nombre',''),'ubicacion':x.get('Ubicacion',''),'estado':x.get('Estado','Disponible')} for x in data.get('Equipos',[])],
                        'usuarios': [{'id':x.get('Id',''),'nombre':x.get('Nombre',''),'documento':x.get('Documento',''),'rol':x.get('Rol','Estudiante')} for x in data.get('Usuarios',[])],
                        'prestamos': [{'id':x.get('Id',''),'equipoId':x.get('EquipoId',''),'usuarioId':x.get('UsuarioId',''),'inicio':x.get('Inicio'),'fin':x.get('Fin'),'estado':x.get('Estado','Confirmada'),'entregadoEn':x.get('EntregadoEn'),'devueltoEn':x.get('DevueltoEn'),'responsable':x.get('Responsable'),'nota':x.get('Nota') or ''} for x in data.get('Reservas',[])],
                        'eventos': [{'fecha':x.get('Fecha'),'equipoId':x.get('EquipoId',''),'texto':x.get('Texto','')} for x in data.get('Eventos',[])]
                    }
                return {**{'equipos': [], 'usuarios': [], 'prestamos': [], 'eventos': []}, **data}
            except (OSError, json.JSONDecodeError): raise BusinessError('No fue posible leer datos.json.')
        return {'equipos': [], 'usuarios': [], 'prestamos': [], 'eventos': []}

    def _save(self): self.data_file.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding='utf-8')
    def _id(self): return uuid4().hex[:8]
    def _log(self, equipo_id, texto): self.data['eventos'].append({'fecha': datetime.now().isoformat(), 'equipoId': equipo_id, 'texto': texto})

    def _seed(self):
        for tipo, nombre in [('Portátil','Lenovo ThinkPad E14'),('Portátil','Dell Latitude 3420'),('Portátil','HP ProBook 440'),('Portátil','Acer Aspire 5'),('Proyector','Epson X49'),('Proyector','BenQ MS550')]: self.registrar_equipo(tipo,nombre,'Biblioteca')
        for nombre, doc, rol in [('Ana Torres','1001234567','Estudiante'),('Brayan Ruiz','79876543','Docente'),('Omar Díaz','80123456','Docente'),('Laura Gómez','52111222','Encargado')]: self.registrar_usuario(nombre,doc,rol)

    def registrar_usuario(self, nombre, documento, rol='Estudiante'):
        nombre, documento = (nombre or '').strip(), (documento or '').strip()
        if not nombre or not documento: raise BusinessError('Nombre y documento son obligatorios.')
        if any(u['documento']==documento for u in self.data['usuarios']): raise BusinessError('Ya existe un usuario con ese documento.')
        if rol not in ('Estudiante','Docente','Encargado','Guarda'): raise BusinessError('Rol no válido.')
        u={'id':self._id(),'nombre':nombre,'documento':documento,'rol':rol}; self.data['usuarios'].append(u); self._save(); return u

    def registrar_equipo(self, tipo, nombre, ubicacion='Biblioteca'):
        nombre=(nombre or '').strip()
        if tipo not in ('Portátil','Proyector') or not nombre: raise BusinessError('Seleccione un tipo válido e indique el nombre del equipo.')
        prefijo='PR' if tipo=='Proyector' else 'PT'
        nums=[int(e['id'].split('-')[1]) for e in self.data['equipos'] if e['id'].startswith(prefijo+'-') and e['id'].split('-')[1].isdigit()]
        e={'id':f'{prefijo}-{max(nums,default=0)+1:03d}','tipo':tipo,'nombre':nombre,'ubicacion':(ubicacion or '').strip(),'estado':'Disponible'}
        self.data['equipos'].append(e); self._log(e['id'],'Equipo registrado en el inventario.'); self._save(); return e

    def _prestamo_activo(self, equipo_id): return next((p for p in self.data['prestamos'] if p['equipoId']==equipo_id and p['estado']=='Entregada'),None)
    def _choque(self, equipo_id, inicio, fin):
        for p in self.data['prestamos']:
            if p['equipoId']!=equipo_id or p['estado'] not in ('Confirmada','Entregada'): continue
            pi,pf=datetime.fromisoformat(p['inicio']),datetime.fromisoformat(p['fin'])
            if p['estado']=='Entregada' and pf<datetime.now(): pf=datetime.max
            if pi<fin and inicio<pf: return True
        return False

    def crear_prestamo(self, equipo_id, documento, inicio, fin):
        if isinstance(inicio,str): inicio=datetime.fromisoformat(inicio)
        if isinstance(fin,str): fin=datetime.fromisoformat(fin)
        if fin<=inicio: raise BusinessError('La fecha de fin debe ser posterior al inicio.')
        e=next((x for x in self.data['equipos'] if x['id']==equipo_id),None)
        if not e: raise BusinessError('Equipo no encontrado.')
        if e['estado']!='Disponible': raise BusinessError(f"El equipo está en '{e['estado']}' y no se puede reservar.")
        u=next((x for x in self.data['usuarios'] if x['documento']==str(documento).strip()),None)
        if not u: raise BusinessError('Solo usuarios autorizados por la universidad pueden pedir préstamos.')
        if self._choque(equipo_id,inicio,fin): raise BusinessError('El equipo ya está ocupado por una reserva o préstamo en ese horario.')
        p={'id':self._id(),'equipoId':equipo_id,'usuarioId':u['id'],'inicio':inicio.isoformat(),'fin':fin.isoformat(),'estado':'Confirmada','entregadoEn':None,'devueltoEn':None,'responsable':None,'nota':''}
        self.data['prestamos'].append(p); self._log(equipo_id,f"Reservado por {u['nombre']}."); self._save(); return p

    def _find_prestamo(self, pid):
        p=next((x for x in self.data['prestamos'] if x['id']==pid),None)
        if not p: raise BusinessError('Préstamo no encontrado.')
        return p
    def obtener_equipo(self, eid):
        e=next((x for x in self.data['equipos'] if x['id']==eid),None)
        if not e: raise BusinessError('Equipo no encontrado.')
        return e

    def entregar(self, pid, responsable, estado_entrega='Bueno'):
        p=self._find_prestamo(pid)
        if p['estado']!='Confirmada': raise BusinessError('Solo se puede entregar una reserva confirmada.')
        if not (responsable or '').strip(): raise BusinessError('Indique el responsable de la entrega.')
        e=self.obtener_equipo(p['equipoId'])
        if e['estado']!='Disponible' or self._prestamo_activo(e['id']): raise BusinessError('El equipo no está disponible para entrega.')
        p.update(estado='Entregada',entregadoEn=datetime.now().isoformat(),responsable=responsable.strip())
        u=next(x for x in self.data['usuarios'] if x['id']==p['usuarioId'])
        self._log(e['id'],f"Entregado a {u['nombre']} por {responsable}. Estado: {estado_entrega or 'Bueno'}."); self._save(); return p

    def devolver(self, pid, danio=False, nota=''):
        p=self._find_prestamo(pid)
        if p['estado']!='Entregada': raise BusinessError('Esta reserva no tiene un equipo entregado.')
        e=self.obtener_equipo(p['equipoId']); tarde=datetime.now()>datetime.fromisoformat(p['fin'])
        p.update(estado='Devuelta',devueltoEn=datetime.now().isoformat(),nota=nota or '')
        if danio: e['estado']='Mantenimiento'
        self._log(e['id'],f"Devuelto{' con retraso' if tarde else ''}. {'Daño reportado: '+(nota or 'Sin detalle') if danio else 'Sin novedad.'}"); self._save(); return p

    def cambiar_estado(self,equipo_id,estado,nota=''):
        e=self.obtener_equipo(equipo_id)
        if estado not in ('Disponible','Mantenimiento','Fuera de servicio'): raise BusinessError('Estado no válido.')
        if estado=='Disponible' and self._prestamo_activo(equipo_id): raise BusinessError('No se puede habilitar un equipo que todavía está prestado.')
        e['estado']=estado; self._log(equipo_id,f'Estado cambiado a {estado}. {nota}'.strip()); self._save(); return e

    def cancelar(self,pid,estado='Cancelada'):
        p=self._find_prestamo(pid)
        if p['estado']!='Confirmada': raise BusinessError('Solo se puede modificar una reserva confirmada.')
        p['estado']=estado; self._log(p['equipoId'],'Reserva '+estado.lower()+'.'); self._save(); return p

    def listar_equipos(self):
        result=[]
        for e in self.data['equipos']:
            p=self._prestamo_activo(e['id']); u=next((x for x in self.data['usuarios'] if p and x['id']==p['usuarioId']),None)
            result.append({**e,'estado':'Prestado' if p else e['estado'],'poseedor':u['nombre'] if u else None,'devolucion':p['fin'] if p else None})
        return result
    def listar_usuarios(self): return list(self.data['usuarios'])
    def listar_prestamos(self):
        out=[]
        for p in sorted(self.data['prestamos'],key=lambda x:x['inicio'],reverse=True):
            e=self.obtener_equipo(p['equipoId']); u=next(x for x in self.data['usuarios'] if x['id']==p['usuarioId'])
            estado='Atrasada' if p['estado']=='Entregada' and datetime.fromisoformat(p['fin'])<datetime.now() else p['estado']
            out.append({**p,'equipo':e['nombre'],'usuario':u['nombre'],'estado':estado})
        return out
    def historial_equipo(self,eid):
        self.obtener_equipo(eid); return sorted([x for x in self.data['eventos'] if x['equipoId']==eid],key=lambda x:x['fecha'],reverse=True)
    def resumen(self):
        ps=self.data['prestamos']; activos=[p for p in ps if p['estado']=='Entregada']
        return {'total':len(self.data['equipos']),'disponibles':sum(1 for e in self.data['equipos'] if e['estado']=='Disponible' and not self._prestamo_activo(e['id'])),'prestados':len(activos),'mantenimiento':sum(1 for e in self.data['equipos'] if e['estado']!='Disponible'),'atrasados':sum(1 for p in activos if datetime.fromisoformat(p['fin'])<datetime.now()),'reservasHoy':sum(1 for p in ps if p['estado']=='Confirmada' and datetime.fromisoformat(p['inicio']).date()==datetime.now().date())}
    def disponibilidad(self,tipo,inicio,fin):
        if isinstance(inicio,str): inicio=datetime.fromisoformat(inicio)
        if isinstance(fin,str): fin=datetime.fromisoformat(fin)
        return [{'id':e['id'],'nombre':e['nombre']} for e in self.data['equipos'] if e['tipo']==tipo and e['estado']=='Disponible' and not self._choque(e['id'],inicio,fin)]

    def verificar_porteria(self,codigo):
        codigo=(codigo or '').strip().upper(); e=next((x for x in self.data['equipos'] if x['id'].upper()==codigo),None)
        if e:
            p=self._prestamo_activo(e['id'])
            if not p:
                self._log(e['id'],'ALERTA portería: salida sin préstamo activo.'); self._save()
                return {'ok':False,'tipo':'equipo','mensaje':f"{e['nombre']} NO tiene préstamo activo. No debe salir.",'detalle':[]}
            u=next(x for x in self.data['usuarios'] if x['id']==p['usuarioId'])
            return {'ok':True,'tipo':'equipo','mensaje':f"{e['nombre']} autorizado para {u['nombre']}.",'detalle':[f"Documento: {u['documento']}",f"Devolución: {p['fin']}"]}
        u=next((x for x in self.data['usuarios'] if x['documento'].upper()==codigo),None)
        if u:
            ps=[p for p in self.data['prestamos'] if p['usuarioId']==u['id'] and p['estado']=='Entregada']
            if not ps: return {'ok':False,'tipo':'usuario','mensaje':f"{u['nombre']} no tiene equipos a cargo. Si lleva uno, no está autorizado.",'detalle':[]}
            detalle=[f"{p['equipoId']} · {self.obtener_equipo(p['equipoId'])['nombre']} (devuelve {p['fin']})" for p in ps]
            return {'ok':True,'tipo':'usuario','mensaje':f"{u['nombre']} tiene {len(ps)} equipo(s) autorizado(s).",'detalle':detalle}
        return {'ok':False,'tipo':'desconocido','mensaje':'Código no reconocido. Verifique manualmente.','detalle':[]}
