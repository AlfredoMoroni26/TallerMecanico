# Fase 2: Crear roles

> Especificación funcional · Versión 1.1.0 · Actualizada el 2026-11-05

| Elemento | Descripción |
| --- | --- |
| Fase | Fase 2: Crear roles |
| Funcionalidad | Creación de nuevos roles |
| Actor principal | Administrador |
| Precondición | Haber iniciado sesión como administrador |
| Regla de negocio | No pueden existir dos roles iguales |
| Validación | Verificar duplicados antes de guardar |
| Restricción | La recepcionista no puede crear roles |
| Resultado esperado | Rol registrado correctamente con un ID consecutivo visible |

## Alcance implementado

La pantalla permite únicamente registrar un nombre de rol. Antes de persistirlo, el nombre se normaliza: se eliminan espacios al inicio y final, los espacios internos se convierten en guiones bajos y se transforma a minúsculas. Por ejemplo, ` Supervisor   Taller ` y `supervisor taller` representan el mismo rol y el segundo intento recibe el mensaje **“El rol ya está registrado.”**

El endpoint `POST /api/v1/roles` exige el rol `administrador_taller`. Una sesión de recepcionista recibe una respuesta de acceso denegado y no puede registrar roles. Esta fase no incorpora consulta, edición, eliminación ni asignación de roles.

## Criterios de aceptación verificables

1. Un administrador autenticado puede crear un rol con un nombre válido.
2. El sistema rechaza nombres equivalentes que sólo difieran por espacios o mayúsculas.
3. La respuesta de duplicidad informa que el rol ya está registrado sin exponer detalles internos.
4. La recepcionista recibe una respuesta de autorización denegada y el registro no se crea.
5. El rol creado conserva un identificador técnico interno y muestra un ID consecutivo para consulta administrativa.
