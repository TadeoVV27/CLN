# FerreMax - Diseño Arquitectural

Proyecto académico correspondiente a la Actividad 3 de la materia
Componentes de Lógica de Negocios.

## Alcance

El proyecto representa la propuesta arquitectural del proceso central de
FerreMax: cotización, crédito, venta, inventario y entrega.

## Arquitectura

El diseño utiliza Domain Model como patrón principal de lógica de negocio,
complementado con:

- Service Layer
- Repository
- Unit of Work
- CQRS básico
- Principios SOLID

## Estructura

- `docs/`: informe, ADR, trazabilidad y bitácora.
- `diagrams/`: diagramas UML y archivos fuente.
- `src/domain/`: entidades y reglas del negocio.
- `src/application/`: Application Services e interfaces Repository.
- `src/infrastructure/`: implementaciones de persistencia.
- `tests/`: escenarios de validación.

## Nota

El código incluido representa una estructura base de la arquitectura.
No constituye una implementación completa del sistema FerreMax.