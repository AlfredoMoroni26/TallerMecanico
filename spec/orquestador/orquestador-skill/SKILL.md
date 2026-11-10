---
name: orquestador
description: Orquesta solicitudes del proyecto Taller Mecánico conforme al archivo orquestador, sus skills y especificaciones funcionales.
version: 1.0.0
language: es
metadata:
  short-description: Orquesta tareas del proyecto Taller Mecánico
---

# Orquestador del proyecto

Usa esta skill únicamente cuando el usuario la invoque de forma explícita para coordinar una tarea del proyecto Taller Mecánico.

## Fuente canónica

Al inicio, localiza y lee por completo `spec/orquestador/orquestador.md` desde la raíz del espacio de trabajo. Ese archivo define las fuentes, prioridades, alcance y formato aplicables. Si no existe, informa la ausencia y solicita la ubicación antes de continuar.

## Ejecución

1. Clasifica la solicitud conforme al orquestador canónico.
2. Lee únicamente las guías y especificaciones que la tabla de selección indique para esa clasificación.
3. Identifica el alcance incluido, el excluido, los archivos afectados y las validaciones necesarias.
4. Implementa o analiza sólo lo solicitado, preservando la arquitectura, permisos, relaciones de datos y restricciones existentes.
5. Verifica el resultado con las comprobaciones proporcionales al cambio y comunica sólo resultados observados.

## Límites

- No inventes requisitos, modelos, rutas, permisos ni reglas de negocio.
- No amplíes una fase funcional con capacidades de otra fase.
- Para documentación, actualiza versión y fecha sólo si el archivo modificado ya declara control de versión.
- Para cambios que afecten acceso o datos, confirma que el backend conserva la autorización y el alcance por taller.
- Para preguntas breves, responde directamente sin generar un plan o tabla innecesarios.

## Resultado

En tareas de implementación, diagnóstico amplio o documentación formal, entrega un resumen, el alcance realizado, los archivos involucrados, las validaciones ejecutadas y los límites o pendientes reales. Para tareas simples, usa una respuesta concisa.
