"""Reglas de negocio de PrestaTec.

La persistencia se delega a un repositorio inyectado; este módulo no conoce
ni archivos ni motores de base de datos.
"""
from datetime import datetime
from functools import wraps
from threading import RLock
from uuid import uuid4

from .errors import BusinessError, ConflictoReserva
from .identidad import Autorizador
from .politicas import Politicas
from .reloj import Reloj, a_utc
from .repository import JsonFileRepository, Repository


def _transaccional(methodo):
    """Serializa mutaciones completas (lectura, cambio y guardado)."""
    @wraps(methodo)
    def envoltorio(self, *args, **kwargs):
        with self._bloqueo:
            return methodo(self, *args, **kwargs)
    return envoltorio


class InventoryService:
    def __init__(self, data_file=None, seed=True, repository: Repository | None = None,
                 reloj: Reloj | None = None, politicas: Politicas | None = None,
                 autorizador: Autorizador | None = None):
        self._bloqueo = RLock()
        self.repository = repository or JsonFileRepository(data_file)
        self.reloj = reloj or Reloj()
        self.politicas = politicas or Politicas()
        self.autorizador = autorizador or Autorizador()
        self.data = self.repository.load()
        if seed and not self.data['equipos'] and not self.data['usuarios']:
            self._seed(); self._save()

    def _save(self):
        self.repository.save(self.data)
    def _exigir(self, actor, accion):
        """Autoriza en el caso de uso; las pruebas de dominio sin actor siguen válidas."""
        if actor is not None:
            self.autorizador.exigir(actor, accion)
    def _id(self): return uuid4().hex[:8]
    def _log(self, equipo_id, texto): self.data['eventos'].append({'fecha': self.reloj.ahora().isoformat(), 'equipoId': equipo_id, 'texto': texto})

    def _seed(self):
        for tipo, nombre in [('Portátil','Lenovo ThinkPad E14'),('Portátil','Dell Latitude 3420'),('Portátil','HP ProBook 440'),('Portátil','Acer Aspire 5'),('Proyector','Epson X49'),('Proyector','BenQ MS550')]: self.registrar_equipo(tipo,nombre,'Biblioteca')
        for nombre, doc, rol in [('Ana Torres','1001234567','Estudiante'),('Brayan Ruiz','79876543','Docente'),('Omar Díaz','80123456','Docente'),('Laura Gómez','52111222','Encargado')]: self.registrar_usuario(nombre,doc,rol)

    @_transaccional
    def registrar_usuario(self, nombre, documento, rol='Estudiante', actor=None):
        self._exigir(actor, 'CREAR_RECURSO')
        nombre, documento = (nombre or '').strip(), (documento or '').strip()
        if not nombre or not documento: raise BusinessError('Nombre y documento son obligatorios.')
        if any(u['documento']==documento for u in self.data['usuarios']): raise BusinessError('Ya existe un usuario con ese documento.')
        if rol not in ('Estudiante','Docente','Encargado','Guarda'): raise BusinessError('Rol no válido.')
        u={'id':self._id(),'nombre':nombre,'documento':documento,'rol':rol}; self.data['usuarios'].append(u); self._save(); return u

    @_transaccional
    def registrar_equipo(self, tipo, nombre, ubicacion='Biblioteca', actor=None):
        self._exigir(actor, 'CREAR_RECURSO')
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
            pi,pf=a_utc(p['inicio']),a_utc(p['fin'])
            if p['estado']=='Entregada' and pf<self.reloj.ahora(): pf=datetime.max.replace(tzinfo=pf.tzinfo)
            if pi<fin and inicio<pf: return True
        return False

    @_transaccional
    def crear_prestamo(self, equipo_id, documento, inicio, fin, actor=None):
        self._exigir(actor, 'SOLICITAR_PRESTAMO')
        inicio,fin=a_utc(inicio),a_utc(fin)
        if fin<=inicio: raise BusinessError('La fecha de fin debe ser posterior al inicio.')
        e=next((x for x in self.data['equipos'] if x['id']==equipo_id),None)
        if not e: raise BusinessError('Equipo no encontrado.')
        if e['estado']!='Disponible': raise BusinessError(f"El equipo está en '{e['estado']}' y no se puede reservar.")
        u=next((x for x in self.data['usuarios'] if x['documento']==str(documento).strip()),None)
        if not u: raise BusinessError('Solo usuarios autorizados por la universidad pueden pedir préstamos.')
        if self._choque(equipo_id,inicio,fin):
            raise ConflictoReserva(
                'El equipo ya está ocupado por una reserva o préstamo en ese horario.',
                self.disponibilidad(e['tipo'], inicio, fin),
            )
        p={'id':self._id(),'equipoId':equipo_id,'usuarioId':u['id'],'inicio':inicio.isoformat(),'fin':fin.isoformat(),'estado':'Confirmada','entregadoEn':None,'devueltoEn':None,'responsable':None,'nota':'','actorId':actor.id if actor else None}
        self.data['prestamos'].append(p); self._log(equipo_id,f"Reservado por {u['nombre']}."); self._save(); return p

    def _find_prestamo(self, pid):
        p=next((x for x in self.data['prestamos'] if x['id']==pid),None)
        if not p: raise BusinessError('Préstamo no encontrado.')
        return p
    def obtener_equipo(self, eid):
        e=next((x for x in self.data['equipos'] if x['id']==eid),None)
        if not e: raise BusinessError('Equipo no encontrado.')
        return e

    @_transaccional
    def entregar(self, pid, responsable, estado_entrega='Bueno', actor=None):
        self._exigir(actor, 'ENTREGAR_DEVOLVER')
        p=self._find_prestamo(pid)
        if p['estado']!='Confirmada': raise BusinessError('Solo se puede entregar una reserva confirmada.')
        if not (responsable or '').strip(): raise BusinessError('Indique el responsable de la entrega.')
        e=self.obtener_equipo(p['equipoId'])
        if e['estado']!='Disponible' or self._prestamo_activo(e['id']): raise BusinessError('El equipo no está disponible para entrega.')
        responsable_final = actor.nombre if actor else responsable.strip()
        p.update(estado='Entregada',entregadoEn=self.reloj.ahora().isoformat(),
                 responsable=responsable_final,estadoEntrega=estado_entrega or 'Bueno')
        if actor: p['actorId'] = actor.id
        u=next(x for x in self.data['usuarios'] if x['id']==p['usuarioId'])
        self._log(e['id'],f"Entregado a {u['nombre']} por {responsable_final}. Estado: {estado_entrega or 'Bueno'}."); self._save(); return p

    @_transaccional
    def devolver(self, pid, danio=False, nota='', actor=None, responsable_devolucion=None):
        self._exigir(actor, 'ENTREGAR_DEVOLVER')
        if danio: self._exigir(actor, 'REGISTRAR_DANO')
        p=self._find_prestamo(pid)
        if p['estado']=='Devuelta': raise BusinessError('El préstamo ya fue devuelto.')
        if p['estado']!='Entregada': raise BusinessError('Esta reserva no tiene un equipo entregado.')
        e=self.obtener_equipo(p['equipoId']); tarde=self.reloj.ahora()>a_utc(p['fin'])
        recibe = (responsable_devolucion or '').strip() or (str(actor.nombre or '') if actor else '')
        p.update(estado='Devuelta',devueltoEn=self.reloj.ahora().isoformat(),nota=nota or '',
                 responsableDevolucion=recibe)
        if actor: p['actorId'] = actor.id
        if danio: e['estado']='Mantenimiento'
        texto=f"Devuelto{' con retraso' if tarde else ''}. {'Daño reportado: '+(nota or 'Sin detalle') if danio else 'Sin novedad.'}"
        if actor: texto += f' Registrado por {actor.nombre}.'
        if recibe: texto += f' Recibido por {recibe}.'
        self._log(e['id'],texto); self._save(); return p

    @_transaccional
    def cambiar_estado(self,equipo_id,estado,nota='',actor=None):
        self._exigir(actor, 'HABILITAR' if estado == 'Disponible' else 'REGISTRAR_DANO')
        e=self.obtener_equipo(equipo_id)
        if estado not in ('Disponible','Mantenimiento','Fuera de servicio'): raise BusinessError('Estado no válido.')
        if estado=='Disponible' and self._prestamo_activo(equipo_id): raise BusinessError('No se puede habilitar un equipo que todavía está prestado.')
        texto=f'Estado cambiado a {estado}. {nota}'.strip()
        if actor: texto += f' Registrado por {actor.nombre}.'
        e['estado']=estado; self._log(equipo_id,texto); self._save(); return e

    @_transaccional
    def cancelar(self,pid,estado='Cancelada',actor=None):
        self._exigir(actor, 'ENTREGAR_DEVOLVER')
        p=self._find_prestamo(pid)
        if p['estado']!='Confirmada': raise BusinessError('Solo se puede modificar una reserva confirmada.')
        texto='Reserva '+estado.lower()+'.'
        if actor: texto += f' Registrada por {actor.nombre}.'
        p['estado']=estado; self._log(p['equipoId'],texto); self._save(); return p

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
            estado='Atrasada' if p['estado']=='Entregada' and a_utc(p['fin'])<self.reloj.ahora() else p['estado']
            out.append({**p,'equipo':e['nombre'],'usuario':u['nombre'],
                        'documento':u['documento'],'estado':estado})
        return out
    def historial_equipo(self,eid):
        self.obtener_equipo(eid); return sorted([x for x in self.data['eventos'] if x['equipoId']==eid],key=lambda x:x['fecha'],reverse=True)
    def resumen(self):
        ps=self.data['prestamos']; activos=[p for p in ps if p['estado']=='Entregada']
        ahora=self.reloj.ahora()
        return {
            'total': len(self.data['equipos']),
            'disponibles': sum(1 for e in self.data['equipos'] if e['estado']=='Disponible' and not self._prestamo_activo(e['id'])),
            'prestados': len(activos),
            'mantenimiento': sum(1 for e in self.data['equipos'] if e['estado']!='Disponible'),
            'atrasados': sum(1 for p in activos if p.get('fin') and a_utc(p['fin'])<ahora),
            'reservasHoy': sum(1 for p in ps if p['estado']=='Confirmada' and p.get('inicio') and a_utc(p['inicio']).date()==ahora.date()),
        }
    def disponibilidad(self,tipo,inicio,fin):
        inicio,fin=a_utc(inicio),a_utc(fin)
        return [{'id':e['id'],'nombre':e['nombre']} for e in self.data['equipos'] if e['tipo']==tipo and e['estado']=='Disponible' and not self._choque(e['id'],inicio,fin)]

    @_transaccional
    def verificar_porteria(self,codigo,actor=None):
        self._exigir(actor, 'VERIFICAR_PORTERIA')
        quien = f' Verificada por {actor.nombre}.' if actor else ''
        codigo=(codigo or '').strip().upper()
        e=next((x for x in self.data['equipos'] if x['id'].upper()==codigo),None)
        if e:
            p=self._prestamo_activo(e['id'])
            if not p:
                self._log(e['id'],'ALERTA portería: salida sin préstamo activo.'+quien)
                self._save()
                return {'ok':False,'tipo':'equipo','mensaje':f"{e['nombre']} NO tiene préstamo activo. No debe salir.",'detalle':[]}
            u=next(x for x in self.data['usuarios'] if x['id']==p['usuarioId'])
            self._log(e['id'],f"Portería autorizó salida de {e['nombre']} a {u['nombre']}."+quien)
            self._save()
            return {'ok':True,'tipo':'equipo','mensaje':f"{e['nombre']} autorizado para {u['nombre']}.",'detalle':[f"Documento: {u['documento']}",f"Devolución: {p['fin']}"]}
        u=next((x for x in self.data['usuarios'] if x['documento'].upper()==codigo),None)
        if u:
            ps=[p for p in self.data['prestamos'] if p['usuarioId']==u['id'] and p['estado']=='Entregada']
            if not ps:
                self._log('',f"ALERTA portería: {u['nombre']} no tiene equipos activos."+quien)
                self._save()
                return {'ok':False,'tipo':'usuario','mensaje':f"{u['nombre']} no tiene equipos a cargo. Si lleva uno, no está autorizado.",'detalle':[]}
            detalle=[f"{p['equipoId']} · {self.obtener_equipo(p['equipoId'])['nombre']} (devuelve {p['fin']})" for p in ps]
            for p in ps:
                self._log(p['equipoId'],f"Portería verificó a {u['nombre']} con {p['equipoId']}."+quien)
            self._save()
            return {'ok':True,'tipo':'usuario','mensaje':f"{u['nombre']} tiene {len(ps)} equipo(s) autorizado(s).",'detalle':detalle}
        self._log('',f'ALERTA portería: código no reconocido ({codigo}).'+quien)
        self._save()
        return {'ok':False,'tipo':'desconocido','mensaje':'Código no reconocido. Verifique manualmente.','detalle':[]}
