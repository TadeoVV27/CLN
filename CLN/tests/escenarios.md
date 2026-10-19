# Escenarios de prueba - FerreMax

## Escenario 1 - Venta de mostrador

Dado que existe inventario suficiente para atender la venta,
cuando el vendedor procesa una venta de mostrador,
entonces la venta debe confirmarse y el inventario debe actualizarse.

## Escenario 2 - Cotización vencida

Dado que una cotización se encuentra vencida,
cuando se intenta validar una operación empresarial,
entonces la operación debe detenerse.

## Escenario 3 - Crédito no autorizado

Dado que una operación a crédito no cuenta con autorización,
cuando se intenta continuar con la venta,
entonces la operación debe ser rechazada.

## Escenario 4 - Inventario insuficiente

Dado que no existe inventario suficiente en la ubicación,
cuando se intenta atender el pedido,
entonces debe identificarse la situación y permitir gestionar el pedido como parcial.