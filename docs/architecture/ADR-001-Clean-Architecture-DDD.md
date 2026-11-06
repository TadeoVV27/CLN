# ADR 001: Adopción de Domain-Driven Design (DDD) y Arquitectura Limpia

## Estado
Aceptado

## Contexto
El sistema FerreMax maneja reglas complejas de negocio (vigencia de cotizaciones, validaciones de crédito empresarial, control de inventario con stock comprometido y cálculo de beneficios VIP). Se requiere desacoplar las reglas de negocio de la infraestructura y frameworks externos (FastAPI, bases de datos o interfaces web).

## Decisión
Se implementa una arquitectura en capas basada en principios de Clean Architecture y DDD:
1. **Domain:** Entidades (`Actor`, `Recurso`, `Operacion`), Value Objects, Specifications, State Machine y Domain Events.
2. **Application:** Servicios de orquestación (`VentaApplicationService`, `ValidacionApplicationService`, `EvaluadorDocenteService`) e interfaces de repositorios y Unit of Work.
3. **Infrastructure:** Implementación de repositorios en memoria/persistencia y adaptadores.
4. **API / Presentación:** Controladores REST con FastAPI y Frontend Web de Mostrador.

## Consecuencias
- **Positivas:** Máxima testabilidad (pruebas unitarias corren en 0.1s sin depender de base de datos externa), alta coherencia y bajo acoplamiento.
- **Negativas:** Mayor número de clases y abstracciones iniciales.
