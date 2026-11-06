from dataclasses import dataclass
from typing import List

@dataclass
class CrearCotizacionCommand:
    cliente_id: int
    productos_ids: List[int]
    cantidades: List[int]

@dataclass
class ComprometerMercanciaCommand:
    pedido_id: int
    cotizacion_id: int

@dataclass
class SolicitarTransferenciaCommand:
    producto_id: int
    cantidad_requerida: int
    sucursal_origen_id: int
    sucursal_destino_id: int

@dataclass
class AutorizarCreditoCommand:
    cliente_id: int
    monto_solicitado: float