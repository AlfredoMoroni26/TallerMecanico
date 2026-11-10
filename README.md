# Taller Mecánico

> Documentación del proyecto · Versión 1.4.0 · Actualizada el 2026-11-10

Aplicación web modular para la operación de talleres mecánicos. Incluye identidad y acceso, talleres, clientes y vehículos, con autorización basada en roles y aislamiento de datos por taller.

## Tecnologías

| Capa | Tecnologías |
| --- | --- |
| Frontend | Vue 3, TypeScript, Vite, Vuetify y Axios |
| Backend | Python, FastAPI, SQLAlchemy y Pydantic |
| Persistencia local | SQLite |
| Seguridad | bcrypt, JWT de acceso y refresh tokens revocables |

## Estructura

```text
backend/
  app/
    core/                 # configuración, seguridad y excepciones compartidas
    db/                   # sesión, motor y modelo base
    modules/
      identity/           # autenticación, usuarios, roles, sesiones y recuperación
      workshops/          # talleres, clientes, vehículos y servicios de ubicación
  uploads/                # fotografías cargadas; no se versionan
  scripts/                # utilidades de mantenimiento y datos locales
frontend/
  src/
    api/                  # cliente Axios e interceptores
    modules/              # vistas, stores y tipos por dominio
    router/               # rutas y guards de autenticación/autorización
    layouts/ y styles/    # estructura visual y estilos compartidos
spec/                     # orquestador, skills y convenciones del proyecto
fase … .md/               # especificaciones funcionales implementadas
```

La aplicación separa transporte (rutas y vistas), reglas de negocio (servicios y stores) y persistencia (modelos). Los módulos nuevos deben seguir esta misma convención.

## Módulos disponibles

| Módulo | Alcance actual |
| --- | --- |
| Identidad | Registro público de clientes, inicio/cierre de sesión, JWT, recuperación de contraseña, usuarios y roles. |
| Talleres | Alta de taller, validación de RFC, consulta de ubicación y fotografía. |
| Clientes | Registro, actualización, desactivación lógica y aislamiento por taller. |
| Vehículos | Registro con fotografía, consulta por taller, actualización sin cambiar VIN/cliente y activación o desactivación lógica. |

## Arranque local

1. Copia `backend/.env.example` a `backend/.env` y configura valores locales seguros. No reutilices el `SECRET_KEY` de producción.
2. En una terminal, inicia el backend:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. Copia `frontend/.env.example` a `frontend/.env`.
4. En otra terminal, inicia el frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

Servicios locales:

- Frontend: `http://127.0.0.1:5173`
- API: `http://127.0.0.1:8000`
- Documentación interactiva: `http://127.0.0.1:8000/docs`
- Estado del backend: `http://127.0.0.1:8000/health`

## API principal

| Método | Ruta | Acceso | Propósito |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | Público | Registra únicamente una cuenta con rol Cliente. |
| POST | `/api/v1/auth/login` | Público | Inicia sesión y entrega tokens. |
| POST | `/api/v1/auth/refresh` | Público | Rota un refresh token válido. |
| POST | `/api/v1/auth/logout` | Autenticado | Revoca la sesión actual. |
| POST | `/api/v1/auth/password-reset/request` | Público | Solicita recuperación sin revelar si existe una cuenta. |
| POST | `/api/v1/auth/password-reset/confirm` | Público | Restablece la contraseña con un token válido. |
| GET / POST | `/api/v1/users` | Administrador | Consulta o crea usuarios. |
| GET / PATCH / DELETE | `/api/v1/users/{user_id}` | Administrador | Consulta, actualiza o desactiva una cuenta. |
| GET | `/api/v1/users/me` | Autenticado | Devuelve el perfil de la sesión. |
| GET / POST | `/api/v1/roles` | Administrador | Consulta o crea roles. |
| PATCH | `/api/v1/roles/{role_id}/name` | Administrador | Actualiza el nombre de un rol. |
| PATCH | `/api/v1/roles/{role_id}/suspend` | Administrador | Suspende un rol de manera lógica. |
| PATCH | `/api/v1/roles/{role_id}/activate` | Administrador | Reactiva un rol suspendido. |
| GET / POST / PATCH | `/api/v1/clients` y `/api/v1/clients/{client_id}` | Administrador, Recepcionista | Gestiona clientes del taller propio. |
| POST | `/api/v1/clients/{client_id}/deactivate` | Administrador | Desactiva un cliente sin borrar su historial. |
| GET / POST | `/api/v1/vehicles` | Administrador, Recepcionista | Consulta o registra vehículos del taller propio. |
| PATCH | `/api/v1/vehicles/{vehicle_id}` | Administrador, Recepcionista | Actualiza datos del vehículo sin cambiar VIN, cliente ni taller. |
| PATCH | `/api/v1/vehicles/{vehicle_id}/deactivate` | Administrador, Recepcionista | Desactiva un vehículo sin borrar su historial. |
| PATCH | `/api/v1/vehicles/{vehicle_id}/activate` | Administrador, Recepcionista | Reactiva un vehículo previamente desactivado. |
| POST | `/api/v1/workshops` | Roles autorizados | Registra un taller con fotografía. |

Consulta `/docs` para conocer contratos, parámetros y respuestas vigentes.

## Roles base

Los identificadores de rol son estables para autorización: `administrador_taller`, `recepcionista`, `asesor_servicio`, `tecnico`, `cliente` y `sistema`.

- El registro público asigna únicamente el rol `cliente`.
- Administradores y recepcionistas requieren un taller asignado para operar clientes y vehículos.
- El backend valida rol y alcance por taller; los guards del frontend son una ayuda de interfaz, no el control de seguridad definitivo.

## Seguridad y operación

- Las contraseñas se almacenan con bcrypt y nunca en texto plano.
- Los tokens de refresh y recuperación se almacenan como hashes, no como valores reutilizables.
- Los errores públicos no deben revelar información sensible.
- No subas `.env`, bases SQLite locales ni archivos de `backend/uploads/` al repositorio.
- Antes de publicar: usa HTTPS, un `SECRET_KEY` único, una base de datos administrada, migraciones con Alembic, cookies `HttpOnly`/`Secure` para refresh tokens y protección CSRF.

## Verificación mínima

Antes de entregar cambios, ejecuta `npm run build` dentro de `frontend/` y verifica manualmente los flujos afectados de la API. Para cambios de identidad, talleres, clientes o vehículos, prueba también permisos, pertenencia al taller, datos duplicados y respuestas de validación.

## Despliegue rápido en Railway

El repositorio incluye `Dockerfile` y `railway.toml` para publicar frontend y API en una sola URL. Railway debe crear también un servicio PostgreSQL y un volumen montado en `/data` para conservar fotografías.

Configura estas variables en Railway, nunca en el repositorio:

| Variable | Valor esperado |
| --- | --- |
| `DATABASE_URL` | Referencia al PostgreSQL de Railway (`${{Postgres.DATABASE_URL}}`). |
| `SECRET_KEY` | Valor aleatorio de al menos 32 caracteres. |
| `FRONTEND_ORIGINS` | Dominio público generado por Railway, con `https://`. |
| `UPLOADS_ROOT` | `/data/uploads`. |
| `INITIAL_ADMIN_USERNAME`, `INITIAL_ADMIN_EMAIL`, `INITIAL_ADMIN_PASSWORD` | Credenciales iniciales temporales; elimina la contraseña después del primer acceso. |
| `POSTAL_API_KEY` | Clave de CPostal para la consulta de ubicación, si se utiliza esa integración. |

Pasos de publicación:

1. Sube los cambios a GitHub.
2. En Railway, crea un proyecto desde ese repositorio y permite que detecte `Dockerfile`.
3. Agrega PostgreSQL y referencia su `DATABASE_URL` desde el servicio web.
4. Agrega un Volume en `/data`.
5. Configura las variables anteriores, genera el dominio público y confirma que `/health` devuelve `{"status":"ok"}`.
6. Abre la URL, inicia sesión y prueba registro, fotografías, roles, clientes y vehículos.

Para pruebas, Railway es la ruta más rápida. Antes de uso productivo, configura respaldos de PostgreSQL, un dominio propio y almacenamiento de objetos para fotografías si se requiere escalar.

## Análisis de seguridad con Semgrep

El flujo `.github/workflows/semgrep.yml` ejecuta Semgrep en GitHub Actions al abrir un Pull Request, subir cambios a `main` o `master`, o iniciarlo manualmente desde la pestaña **Actions**. El análisis usa reglas OWASP, Python y JavaScript, y excluye dependencias, archivos generados, cargas y bases locales. No requiere exponer secretos de la aplicación.
