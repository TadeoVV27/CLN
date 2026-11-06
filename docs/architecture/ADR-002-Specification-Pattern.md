# ADR 002: Encapsulamiento de Reglas mediante el Patrón Specification

## Estado
Aceptado

## Contexto
Las reglas de validación comercial (como `puede_procesarse` y `beneficio_referencia`) implican evaluar múltiples condiciones booleanas independientes que pueden reutilizarse o combinarse de formas diversas en distintos puntos del sistema.

## Decisión
Se implementa el patrón **Specification** (Evans & Fowler) con una clase abstracta `Specification` que sobrecarga los operadores de Python (`&`, `|`, `~` y métodos `and_`, `or_`, `not_`).
Reglas atómicas creadas:
- `ActorActivoSpecification`
- `DetalleNoVacioSpecification`
- `OperacionAutorizadaSpecification`
- `ActorPreferenteSpecification`
- `TotalMinimoSpecification`
- `PromocionActivaSpecification`
- `StockSuficienteSpecification`

Reglas compuestas:
- `PuedeProcesarseSpecification` = `ActorActivo & DetalleNoVacio & OperacionAutorizada`
- `BeneficioReferenciaSpecification` = `ActorPreferente & TotalMinimo & ~PromocionActiva`

## Consecuencias
- **Positivas:** Las reglas son atómicas, nombrables, autodocumentadas y testeables por separado. Cumple el Principio de Responsabilidad Única (SRP) y Abierto/Cerrado (OCP).
