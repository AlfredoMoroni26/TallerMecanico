# Taller Mecánico — Módulo de Identidad

Base modular para una aplicación de taller mecánico.

## Diseño y estructura

```
backend/
  app/
    core/             # configuración, seguridad y excepciones
    db/               # conexión y modelo base
    modules/identity/ # dominio aislado: modelos, esquemas, servicios y rutas
frontend/
  src/
    api/              # cliente HTTP e interceptores
    modules/identity/ # vistas, estado y tipos del dominio
    router/           # protección de rutas por rol
```

El diseño separa transporte (rutas/vistas), reglas de negocio (servicios/stores) y persistencia (modelos). Cada módulo futuro (órdenes, vehículos, inventario) puede repetir esta convención sin acoplarse a Identidad.

## Arranque

1. Copia `backend/.env.example` a `backend/.env`, cambia `SECRET_KEY`, configura la base de datos y define las tres variables `INITIAL_ADMIN_*` una única vez para crear el primer administrador.
2. Backend: `cd backend; python -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt; uvicorn app.main:app --reload`.
3. Copia `frontend/.env.example` a `frontend/.env`.
4. Frontend: `cd frontend; npm install; npm run dev`.

La documentación interactiva de la API queda en `http://localhost:8000/docs`.

## API de Identidad

| Método | Ruta | Acceso | Propósito |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | Público | Registra exclusivamente un cliente |
| POST | `/api/v1/auth/login` | Público | Inicia sesión y entrega access/refresh JWT |
| POST | `/api/v1/auth/refresh` | Público | Rota un refresh token |
| POST | `/api/v1/auth/logout` | Público | Revoca una sesión |
| POST | `/api/v1/auth/password-reset/request` | Público | Solicita recuperación sin revelar cuentas |
| POST | `/api/v1/auth/password-reset/confirm` | Público | Establece la nueva contraseña |
| GET/POST | `/api/v1/users` | Administrador | Lista o crea usuarios |
| GET/PATCH/DELETE | `/api/v1/users/{user_id}` | Administrador | Consulta, actualiza o desactiva un usuario |
| GET | `/api/v1/users/me` | Autenticado | Perfil de la sesión actual |
| GET/POST | `/api/v1/roles` | Administrador | Lista o crea roles |
| PATCH/DELETE | `/api/v1/roles/{role_id}` | Administrador | Actualiza o elimina roles personalizados |

Los roles de sistema son: `administrador_taller`, `recepcionista`, `asesor_servicio`, `tecnico`, `cliente` y `sistema`. Se nombraron con identificadores estables para autorización y se inicializan automáticamente. Los roles de sistema no se borran ni editan mediante la API.

## Notas de seguridad

- Contraseñas: bcrypt con sal; no se guarda ni registra texto plano.
- Access token de 15 minutos y refresh token rotativo/revocable (configurables).
- Los refresh y reset tokens se guardan como SHA-256, no como valores utilizables.
- El endpoint de recuperación responde de manera indistinguible para cuentas existentes o inexistentes. Falta conectar un proveedor SMTP/transaccional para enviar el token generado; el token no sale en la respuesta HTTP.
- Para producción se recomienda servir sobre HTTPS, cambiar `SECRET_KEY`, sustituir SQLite por PostgreSQL, usar Alembic y mover el refresh token a una cookie `HttpOnly`/`Secure` con protección CSRF.
