# src/domain/state_machine.py
"""
Máquina de Estados (State Machine Pattern) para FerreMax.
Gestiona el ciclo de vida de una Operación:
  CREADO -> APROBADO -> SURTIDO -> ENTREGADO
  Alternativa: CREADO -> CANCELADO | APROBADO -> CANCELADO
Protege la consistencia del dominio evitando saltos ilegales de estado
y disparando Domain Events correspondientes.
"""

from enum import Enum
from typing import List, Optional
from src.domain.events import (
    DomainEvent,
    OperacionAprobadaEvent,
    OperacionSurtidaEvent,
    OperacionEntregadaEvent,
    OperacionCanceladaEvent,
    TransicionRechazadaEvent,
)


class EstadoOperacion(str, Enum):
    CREADO = "CREADO"
    APROBADO = "APROBADO"
    SURTIDO = "SURTIDO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class TransicionEstadoInvalidaException(Exception):
    """Excepción de dominio lanzada ante un intento de transición ilegal."""
    def __init__(self, estado_actual: str, accion: str, motivo: Optional[str] = None):
        self.estado_actual = estado_actual
        self.accion = accion
        self.motivo = motivo or f"No se puede ejecutar '{accion}' desde el estado '{estado_actual}'."
        super().__init__(self.motivo)


class OperacionStateMachine:
    """Controlador de máquina de estados para una Operación."""

    # Matriz de transiciones válidas: (estado_origen, accion) -> estado_destino
    TRANSICIONES_VALIDAS = {
        (EstadoOperacion.CREADO, "aprobar"): EstadoOperacion.APROBADO,
        (EstadoOperacion.APROBADO, "surtir"): EstadoOperacion.SURTIDO,
        (EstadoOperacion.SURTIDO, "entregar"): EstadoOperacion.ENTREGADO,
        (EstadoOperacion.CREADO, "cancelar"): EstadoOperacion.CANCELADO,
        (EstadoOperacion.APROBADO, "cancelar"): EstadoOperacion.CANCELADO,
    }

    def __init__(self, estado_inicial: str = EstadoOperacion.CREADO.value):
        try:
            self._estado = EstadoOperacion(estado_inicial)
        except ValueError:
            self._estado = EstadoOperacion.CREADO
        self._eventos: List[DomainEvent] = []

    @property
    def estado(self) -> EstadoOperacion:
        return self._estado

    @property
    def eventos(self) -> List[DomainEvent]:
        return list(self._eventos)

    def limpiar_eventos(self):
        self._eventos.clear()

    def _ejecutar_transicion(self, accion: str, operacion_id: str = "") -> EstadoOperacion:
        clave = (self._estado, accion)
        if clave not in self.TRANSICIONES_VALIDAS:
            evento_fallo = TransicionRechazadaEvent(
                operacion_id=operacion_id,
                estado_origen=self._estado.value,
                accion_intentada=accion,
                motivo=f"Transición inválida: de '{self._estado.value}' con acción '{accion}'",
            )
            self._eventos.append(evento_fallo)
            raise TransicionEstadoInvalidaException(self._estado.value, accion)

        nuevo_estado = self.TRANSICIONES_VALIDAS[clave]
        estado_previo = self._estado
        self._estado = nuevo_estado
        return nuevo_estado

    def aprobar(self, operacion_id: str = "", actor_id: str = "", total: float = 0.0) -> EstadoOperacion:
        nuevo = self._ejecutar_transicion("aprobar", operacion_id)
        self._eventos.append(OperacionAprobadaEvent(operacion_id=operacion_id, actor_id=actor_id, total=total))
        return nuevo

    def surtir(self, operacion_id: str = "", lineas: int = 0) -> EstadoOperacion:
        nuevo = self._ejecutar_transicion("surtir", operacion_id)
        self._eventos.append(OperacionSurtidaEvent(operacion_id=operacion_id, lineas_surtidas=lineas))
        return nuevo

    def entregar(self, operacion_id: str = "") -> EstadoOperacion:
        nuevo = self._ejecutar_transicion("entregar", operacion_id)
        self._eventos.append(OperacionEntregadaEvent(operacion_id=operacion_id))
        return nuevo

    def completar(self, operacion_id: str = "", actor_id: str = "", total: float = 0.0, lineas: int = 0) -> EstadoOperacion:
        """
        Ejecuta el flujo completo sugerido:
        CREADO -> APROBADO -> SURTIDO -> ENTREGADO
        """
        self.aprobar(operacion_id, actor_id, total)
        self.surtir(operacion_id, lineas)
        self.entregar(operacion_id)
        return self._estado

    def cancelar(self, operacion_id: str = "", motivo: str = "Cancelado por el usuario") -> EstadoOperacion:
        estado_previo = self._estado.value
        nuevo = self._ejecutar_transicion("cancelar", operacion_id)
        self._eventos.append(OperacionCanceladaEvent(operacion_id=operacion_id, motivo=motivo, estado_previo=estado_previo))
        return nuevo
