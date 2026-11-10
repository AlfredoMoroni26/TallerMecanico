# Alta del taller mecánico

> Especificación funcional · Versión 1.1.0 · Actualizada el 2026-11-05

| Elemento | Descripción |
| --- | --- |
| Fase | Alta del taller mecánico |
| Pantalla | Registro de taller mecánico |
| Objetivo | Registrar nuevos talleres mediante un formulario único |
| Actores | Administrador y secretaria/recepcionista |
| Precondición | Sesión iniciada y permiso autorizado |
| Entrada | Datos generales, fiscales, dirección y una fotografía |
| Validación 1 | RFC único, normalizado a mayúsculas |
| Validación 2 | Formato de RFC mexicano de persona física o moral mediante expresión regular |
| Validación 3 | Taller no duplicado por nombre, calle, colonia y código postal |
| Integración | API CPostal de códigos postales de México, consumida sólo por el backend |
| Proceso | Validar, consultar la ubicación, almacenar una fotografía y registrar el taller |
| Salida exitosa | Taller registrado correctamente |
| Salida alternativa | Mensaje claro por validación, RFC duplicado, taller duplicado o consulta postal sin resultados |

## Alcance implementado

La pantalla `/workshops/new` está disponible únicamente para `administrador_taller`, `recepcionista` y el rol futuro `secretaria`. Permite buscar por código postal o seleccionar estado, municipio y colonia; la segunda ruta consulta resultados reales y permite elegir el código postal correcto cuando hay más de uno. La fotografía única se almacena en `backend/uploads/workshops` y se persiste su referencia.

No se incluyeron pantallas ni operaciones de consulta, edición, eliminación, suspensión o administración de talleres.

## Criterios de aceptación verificables

1. Un rol autorizado puede registrar un taller con todos los campos obligatorios y una fotografía válida.
2. El sistema rechaza RFC inválidos, RFC duplicados y talleres duplicados por ubicación.
3. La ubicación se obtiene exclusivamente a través del backend; el frontend no consume directamente la API postal.
4. La fotografía sólo acepta los formatos y tamaño configurados por el backend.
5. Un error de validación no deja un registro parcial ni una fotografía huérfana.
