# ADR 003: Control del Ciclo de Vida mediante State Machine y Domain Events

## Estado
Aceptado

## Contexto
Una operación comercial atraviesa distintos estados (`CREADO`, `APROBADO`, `SURTIDO`, `ENTREGADO`, `CANCELADO`). Permitir modificaciones de estado arbitrarias generaría inconsistencias físicas en inventario y financieras.

## Decisión
Se implementa una **Máquina de Estados Finita (State Machine)** dentro del agregado `Operacion`:
1. Matriz explícita de transiciones permitidas.
2. Ante transiciones fuera de orden o ilegales, se emite `TransicionRechazadaEvent` y se lanza la excepción `TransicionEstadoInvalidaException`.
3. En cada transición válida se emiten eventos de dominio inmutables (`OperacionAprobadaEvent`, `OperacionSurtidaEvent`, `OperacionEntregadaEvent`, `OperacionCanceladaEvent`).

## Consecuencias
- **Positivas:** Invariantes de dominio protegidas en todo momento; auditoría total del ciclo de vida.
- **Negativas:** Exige gestionar excepciones controladas en la capa de aplicación y API REST (código HTTP 409 Conflict).
