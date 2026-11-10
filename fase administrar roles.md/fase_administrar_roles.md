# Fase: Administrar roles

> Especificación funcional · Versión 1.1.0 · Actualizada el 2026-11-05

| Elemento | Descripción |
| --- | --- |
| Fase | Administración de roles |
| Funcionalidad | Actualizar nombre y cambiar el estado de roles mediante Soft Delete |
| Actor autorizado | Administrador con sesión iniciada |
| Precondiciones | Rol existente, conexión de base de datos y autorización administrativa |
| Consulta de apoyo | Visualización del ID consecutivo, nombre y estatus para seleccionar el rol |
| Actualización | Cambia únicamente el nombre; el ID y demás campos se conservan |
| Validación | El nombre se normaliza y no puede duplicar otro rol por mayúsculas o espacios |
| Estado | Alterna únicamente `id_estatus` entre Activo y Suspendido; no existe eliminación física |
| Relación de datos | `roles.id_estatus` referencia `estatus.id_estatus` |
| Estatus inicial | Los roles existentes se conservan y reciben Activo (ID 1) |
| Resultado esperado | Nombre actualizado o estado modificado con mensaje de confirmación |

## Alcance implementado

La pantalla `/admin/roles` muestra los roles existentes exclusivamente como apoyo para seleccionar uno. Cada registro muestra un ID consecutivo visible (1, 2, 3…), su nombre, estatus y las acciones **Actualizar nombre** y **Suspender** o **Activar**, según el estado actual. El UUID interno se conserva únicamente para las relaciones técnicas del sistema y no se muestra al usuario.

La operación de actualización conserva el mismo ID y sólo modifica el nombre. Antes de persistirlo, el sistema normaliza espacios y mayúsculas para impedir equivalencias duplicadas.

La suspensión es una eliminación lógica: el registro se conserva y su `id_estatus` cambia a 2, que corresponde a `Suspendido`. Un rol suspendido puede volver a Activo mediante la acción **Activar**. No se expone ningún endpoint DELETE para roles. Los roles suspendidos no se consideran activos en la verificación de permisos.

## Criterios de aceptación verificables

1. El administrador puede actualizar el nombre sin modificar el ID del rol.
2. El sistema rechaza nombres duplicados tras normalizar mayúsculas y espacios.
3. Un rol activo puede suspenderse sin eliminar su historial.
4. Un rol suspendido puede reactivarse.
5. Ninguna operación de esta fase elimina físicamente roles.
