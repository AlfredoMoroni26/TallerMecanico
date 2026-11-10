---
name: Python FastAPI Best Practices
description: Guía para desarrollar y revisar módulos FastAPI seguros, mantenibles y compatibles con la arquitectura existente del proyecto.
version: 1.1.0
language: es
---

# Python FastAPI Best Practices

## Objetivo
Garantizar desarrollo de módulos FastAPI escalables, mantenibles, seguros y eficientes.

## Principios Obligatorios
- Clean Architecture
- SOLID
- DRY
- KISS
- Separation of Concerns
- Type Hints obligatorios
- Validación mediante Pydantic
- Usar asincronía únicamente cuando el flujo y las dependencias sean realmente asíncronos.
- Mantener el acceso a datos encapsulado en servicios o repositorios, según la convención existente del módulo.
- Aplicar Unit of Work sólo cuando una transacción compleja lo justifique.

## Estructura de Proyecto
```text
app/
├── api/
├── services/
├── repositories/
├── models/
├── schemas/
├── core/
├── infrastructure/
├── dependencies/
├── tests/
└── main.py
```

## Reglas FastAPI
### Endpoints y contratos
- Máximo una responsabilidad.
- No colocar reglas de negocio en las rutas.
- Declarar esquemas de entrada y salida con Pydantic.
- Usar códigos HTTP coherentes y mensajes públicos que no expongan detalles internos.

### Dependency Injection
- Utilizar Depends.
- Evitar instanciaciones directas.
- Centralizar autenticación, autorización y sesión de base de datos en dependencias reutilizables.

### Validación
- Utilizar Pydantic.
- Validar entrada y salida.
- Normalizar los datos cuando exista una regla de negocio definida.
- Revalidar siempre reglas críticas en servicios y base de datos.

## Base de Datos
### Reglas
- Consultar únicamente los datos necesarios para cada operación.
- Utilizar índices apropiados.
- Implementar paginación para listados que puedan crecer significativamente.
- Evitar N+1 Queries.
- Utilizar eager loading cuando corresponda.

### SQLAlchemy
- Usar sesiones controladas.
- Cerrar sesiones mediante la dependencia correspondiente.
- Evitar consultas dentro de ciclos que produzcan N+1.
- No introducir un patrón Repository adicional si el módulo existente ya encapsula el acceso en servicios y no lo necesita.

### Optimización
- Revisar explain plans.
- Minimizar round trips.
- Batch operations para inserciones masivas.

## Seguridad
- Usar JWT con expiración, revocación cuando exista y validación de roles en backend.
- Gestionar secretos mediante variables de entorno; nunca registrarlos ni incluirlos en respuestas.
- Validar permisos y alcance de los datos, por ejemplo `workshop_id`, antes de leer o modificar recursos.
- Validar archivos cargados por tipo, tamaño y ruta de almacenamiento.

## Logging
- Registrar eventos operativos y errores sin incluir credenciales o datos sensibles.
- Incorporar auditoría para operaciones de negocio cuando el módulo ya la requiera.

## Testing
- Añadir pruebas unitarias, de integración o API de forma proporcional al riesgo y a la infraestructura disponible.
- Como mínimo, verificar flujos correctos, validaciones, permisos y aislamiento de datos afectados.
- No afirmar cobertura ni pruebas inexistentes.

## Convenciones IA
Cuando una IA genere código:
1. Analizar requerimiento.
2. Diseñar arquitectura.
3. Identificar esquemas y contratos necesarios.
4. Implementar o ajustar servicios y persistencia respetando la estructura existente.
5. Crear o ajustar endpoints.
6. Validar seguridad, rendimiento y compatibilidad de datos.
7. Ejecutar verificaciones disponibles y reportar resultados reales.
8. Entregar resultado final.

## Checklist
- [ ] SOLID
- [ ] Clean Architecture
- [ ] Validación
- [ ] Logging
- [ ] Testing
- [ ] Seguridad
- [ ] Optimización SQL
- [ ] Documentación
- [ ] Compatibilidad con datos existentes
- [ ] Autorización y alcance de datos
