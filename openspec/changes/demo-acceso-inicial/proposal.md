# Propuesta: acceso usable en el primer arranque

## Problema

En un clon limpio, `python run.py` muestra en la pantalla de acceso las
cuentas `admin` / `admin123`, `celador` / `celador123` y `estudiante` /
`estudiante123`, pero ninguna existe: `identidades.json` está fuera de Git y
`estudiante` tampoco está dado de alta como usuario de negocio. El resultado es
un `401 Credenciales inválidas.` en el primer intento. Quien evalúa el proyecto
prueba lo que ve en pantalla y concluye que no funciona.

## Alcance

- Una preparación **explícita** y **opt-in** de la demostración.
- Crear las tres credenciales y el usuario de negocio `estudiante` de una sola
  vez, sin pasos manuales intermedios.
- Idempotente: repetirla no sobrescribe credenciales ni usuarios existentes.
- Dos formas de invocarla: `python run.py --demo` y un script dedicado.

## Fuera de alcance

- Crear cuentas automáticamente en el arranque normal (`python run.py`).
- Sobrescribir contraseñas o datos ya existentes.
- SSO, correo institucional ni cuentas reales.

## Criterios de aceptación

- **DEMO-01:** tras la preparación, las tres credenciales verifican con las
  claves mostradas en pantalla y tienen los roles `Encargado`, `Guarda` y
  `Consulta`.
- **DEMO-02:** `estudiante` existe como usuario de negocio, para poder reservar.
- **DEMO-03:** si una credencial o el usuario ya existen, se conservan; la
  preparación informa solo lo que creó.
- **DEMO-04:** después de preparar, `POST /api/auth/login` con
  `admin` / `admin123` devuelve `200` y un token en la misma app que sirve la UI.

## Justificación

Cierra una brecha funcional verificable del primer arranque. Se hace con ciclo
Spec → Test → Código completo para sumar un tercer ciclo a la evidencia del
método, sin inventar políticas institucionales ni secretos ocultos.
