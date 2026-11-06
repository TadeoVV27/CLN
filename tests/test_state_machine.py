# tests/test_state_machine.py
"""
Pruebas unitarias para la Máquina de Estados (State Machine) en FerreMax.
Valida transiciones legales, flujo completo, excepciones ante transiciones ilegales
y emisión de Domain Events.
"""

import pytest
from src.domain.state_machine import (
    OperacionStateMachine,
    EstadoOperacion,
    TransicionEstadoInvalidaException,
)
from src.domain.events import (
    OperacionAprobadaEvent,
    OperacionSurtidaEvent,
    OperacionEntregadaEvent,
    OperacionCanceladaEvent,
    TransicionRechazadaEvent,
)


def test_flujo_normal_estado_por_estado():
    sm = OperacionStateMachine(EstadoOperacion.CREADO.value)
    assert sm.estado == EstadoOperacion.CREADO

    # 1. CREADO -> APROBADO
    sm.aprobar("OP-100", "CLI-1", 2500.0)
    assert sm.estado == EstadoOperacion.APROBADO

    # 2. APROBADO -> SURTIDO
    sm.surtir("OP-100", lineas=3)
    assert sm.estado == EstadoOperacion.SURTIDO

    # 3. SURTIDO -> ENTREGADO
    sm.entregar("OP-100")
    assert sm.estado == EstadoOperacion.ENTREGADO

    # Validar eventos generados en orden
    eventos = sm.eventos
    assert len(eventos) == 3
    assert isinstance(eventos[0], OperacionAprobadaEvent)
    assert isinstance(eventos[1], OperacionSurtidaEvent)
    assert isinstance(eventos[2], OperacionEntregadaEvent)


def test_metodo_completar_ejecuta_secuencia_completa():
    sm = OperacionStateMachine()
    sm.completar("OP-200", "CLI-2", 1500.0, lineas=2)
    assert sm.estado == EstadoOperacion.ENTREGADO
    assert len(sm.eventos) == 3


def test_flujo_cancelacion_desde_creado():
    sm = OperacionStateMachine()
    sm.cancelar("OP-300", motivo="Cliente no aceptó presupuesto")
    assert sm.estado == EstadoOperacion.CANCELADO
    assert len(sm.eventos) == 1
    assert isinstance(sm.eventos[0], OperacionCanceladaEvent)
    assert sm.eventos[0].estado_previo == "CREADO"


def test_flujo_cancelacion_desde_aprobado():
    sm = OperacionStateMachine()
    sm.aprobar("OP-301")
    sm.cancelar("OP-301", motivo="Cancelado antes de surtir")
    assert sm.estado == EstadoOperacion.CANCELADO


def test_excepcion_saltar_estado_invalido():
    """Intentar pasar de CREADO directo a ENTREGADO sin pasar por APROBADO ni SURTIDO."""
    sm = OperacionStateMachine()

    with pytest.raises(TransicionEstadoInvalidaException) as exc_info:
        sm.entregar("OP-400")

    assert exc_info.value.estado_actual == "CREADO"
    assert exc_info.value.accion == "entregar"

    # Verificar que el evento de rechazo quedó registrado
    rechazados = [e for e in sm.eventos if isinstance(e, TransicionRechazadaEvent)]
    assert len(rechazados) == 1


def test_excepcion_repetir_aprobacion():
    """Intentar aprobar una orden que ya está aprobada."""
    sm = OperacionStateMachine()
    sm.aprobar("OP-500")

    with pytest.raises(TransicionEstadoInvalidaException) as exc_info:
        sm.aprobar("OP-500")

    assert exc_info.value.estado_actual == "APROBADO"
    assert exc_info.value.accion == "aprobar"


def test_excepcion_modificar_operacion_cancelada():
    """Intentar aprobar o surtir una orden que ya está cancelada."""
    sm = OperacionStateMachine()
    sm.cancelar("OP-600")

    with pytest.raises(TransicionEstadoInvalidaException):
        sm.aprobar("OP-600")

    with pytest.raises(TransicionEstadoInvalidaException):
        sm.surtir("OP-600")
