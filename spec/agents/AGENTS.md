# Repository Guidelines

> Versión de guía: 1.1.0 · Actualizada el 2026-11-05

## Project Structure & Module Organization
This workshop management application uses FastAPI, SQLAlchemy, and Pydantic in `backend/`, with Vue 3, TypeScript, Pinia, Vuetify, and Vite in `frontend/`.
- `backend/app/core/`: configuration, security, and shared errors; `db/`: database setup.
- `backend/app/modules/identity/` and `workshops/`: modelos, esquemas, servicios y rutas por dominio. Mantén las reglas de negocio en servicios y el manejo HTTP en rutas.
- `frontend/src/modules/`: domain views, stores, and types; `api/`: shared HTTP client; `router/`: navigation and access guards; `layouts/` and `styles/`: shared presentation.
- `backend/uploads/`: archivos cargados; `backend/scripts/`: utilidades locales. Los directorios raíz `fase … .md/` contienen especificaciones funcionales.
- Los módulos de talleres incluyen talleres, clientes y vehículos. Todo acceso de personal a clientes o vehículos debe respetar el `workshop_id` en backend.

## Build, Test, and Development Commands
Run commands from the indicated directory in separate terminals:
- Backend setup: `python -m venv .venv`, then `.\.venv\Scripts\Activate.ps1` and `pip install -r requirements.txt`.
- Backend development: `uvicorn app.main:app --reload`. Inspecciona endpoints en `http://127.0.0.1:8000/docs`; `/health` proporciona una comprobación básica.
- Frontend setup: `npm install`.
- Frontend development: `npm run dev`.
- Frontend validation/build: `npm run build` runs TypeScript checks and creates `frontend/dist/`.
- Frontend preview: `npm run preview` serves the production build locally.

## Coding Style & Naming Conventions
Use four-space indentation and `snake_case` functions/files in Python, with `PascalCase` classes. Use two-space indentation, single-quoted imports, and `camelCase` functions/variables in TypeScript. Name Vue views and layouts in `PascalCase`, such as `CreateWorkshopView.vue`, and use `<script setup lang="ts">`. Preserve stable role identifiers such as `administrador_taller`. No formatter or lint command is configured; follow neighboring code and avoid unrelated reformatting.

## Testing Guidelines
No automated test suite, test runner, or coverage threshold is currently configured. Run the frontend build and manually verify affected API/UI flows. For identity, clients, vehicles or workshop changes, check authentication, role restrictions, workshop isolation, validation failures, duplicate handling, and successful submissions. Describe checks and real results in the pull request; add explicit setup instructions if introducing a test runner.

## Commit & Pull Request Guidelines
History contains one descriptive Spanish initial commit, so no formal commit convention is established. Use concise, action-oriented subjects and keep changes focused. Pull requests should explain behavior changes, include verification steps, link relevant issues or feature specifications, and provide screenshots for UI changes. Call out schema and configuration changes.

## Security & Configuration
Copy each application's `.env.example` to `.env`; configure `SECRET_KEY`, database access, and initial administrator settings locally. Never commit credentials, tokens, local databases, or customer uploads. Enforce authorization in backend routes/services as well as frontend guards.

Never change a resource's `workshop_id`, client association, role, or security status from a frontend-only control. Validate the operation in the backend service and limit queries by the authenticated user's scope.
