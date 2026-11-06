# src/domain/events.py
"""
Domain Events para el sistema FerreMax.
Permite desacoplar y auditar las transiciones de negocio y cambios de estado.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class DomainEvent:
    """Clase base inmutable para todos los eventos de dominio."""
    ocurrido_en: datetime = field(default_factory=datetime.now)

    def nombre_evento(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class OperacionCreadaEvent(DomainEvent):
    operacion_id: str = ""
    actor_id: str = ""
    referencia: str = ""


@dataclass(frozen=True)
class OperacionAprobadaEvent(DomainEvent):
    operacion_id: str = ""
    actor_id: str = ""
    total: float = 0.0


@dataclass(frozen=True)
class OperacionSurtidaEvent(DomainEvent):
    operacion_id: str = ""
    lineas_surtidas: int = 0


@dataclass(frozen=True)
class OperacionEntregadaEvent(DomainEvent):
    operacion_id: str = ""
    fecha_entrega: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OperacionCanceladaEvent(DomainEvent):
    operacion_id: str = ""
    motivo: str = ""
    estado_previo: str = ""


@dataclass(frozen=True)
class TransicionRechazadaEvent(DomainEvent):
    operacion_id: str = ""
    estado_origen: str = ""
    accion_intentada: str = ""
    motivo: str = ""
