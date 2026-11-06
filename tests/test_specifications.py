# tests/test_specifications.py
"""
Pruebas unitarias para el Patrón Specification en FerreMax.
Valida reglas atómicas y composición booleana (&, |, ~).
"""

import pytest
from decimal import Decimal

from src.domain.models import Actor, Recurso, DetalleOperacion, Operacion
from src.domain.specifications import (
    ActorActivoSpecification,
    DetalleNoVacioSpecification,
    OperacionAutorizadaSpecification,
    ActorPreferenteSpecification,
    TotalMinimoSpecification,
    PromocionActivaSpecification,
    StockSuficienteSpecification,
    crear_especificacion_puede_procesarse,
    crear_especificacion_beneficio_referencia,
)


def _crear_operacion_dummy(
    activo: bool = True,
    es_preferente: bool = True,
    autorizado: bool = True,
    promocion_activa: bool = False,
    precio: Decimal = Decimal("1000.00"),
    cantidad: int = 2,
    stock: int = 10,
    habilitado: bool = True,
) -> Operacion:
    actor = Actor(
        actor_id="ACT-001",
        nombre="Juan Perez",
        es_preferente=es_preferente,
        activo=activo,
    )
    recurso = Recurso(
        recurso_id="REC-001",
        descripcion="Taladro Industrial",
        precio_mxn=precio,
        capacidad_o_stock=stock,
        habilitado=habilitado,
    )
    detalle = DetalleOperacion(
        operacion_id="OP-001",
        recurso_id="REC-001",
        cantidad=cantidad,
        recurso=recurso,
    )
    operacion = Operacion(
        operacion_id="OP-001",
        actor_id="ACT-001",
        promocion_activa=promocion_activa,
        autorizado=autorizado,
        actor=actor,
        lineas=[detalle] if cantidad > 0 else [],
    )
    return operacion


def test_actor_activo_specification():
    spec = ActorActivoSpecification()
    op_activa = _crear_operacion_dummy(activo=True)
    op_inactiva = _crear_operacion_dummy(activo=False)

    assert spec.is_satisfied_by(op_activa) is True
    assert spec.is_satisfied_by(op_inactiva) is False


def test_detalle_no_vacio_specification():
    spec = DetalleNoVacioSpecification()
    op_con_lineas = _crear_operacion_dummy(cantidad=2)
    op_vacia = _crear_operacion_dummy(cantidad=0)

    assert spec.is_satisfied_by(op_con_lineas) is True
    assert spec.is_satisfied_by(op_vacia) is False


def test_composicion_and_or_not():
    spec_activo = ActorActivoSpecification()
    spec_vip = ActorPreferenteSpecification()

    # Composición AND (&)
    spec_activo_y_vip = spec_activo & spec_vip
    assert spec_activo_y_vip.is_satisfied_by(_crear_operacion_dummy(activo=True, es_preferente=True)) is True
    assert spec_activo_y_vip.is_satisfied_by(_crear_operacion_dummy(activo=True, es_preferente=False)) is False

    # Composición OR (|)
    spec_activo_o_vip = spec_activo | spec_vip
    assert spec_activo_o_vip.is_satisfied_by(_crear_operacion_dummy(activo=False, es_preferente=True)) is True

    # Composición NOT (~)
    spec_no_vip = ~spec_vip
    assert spec_no_vip.is_satisfied_by(_crear_operacion_dummy(es_preferente=False)) is True
    assert spec_no_vip.is_satisfied_by(_crear_operacion_dummy(es_preferente=True)) is False


def test_puede_procesarse_specification():
    """Valida la Regla 1 del docente: actor_activo AND detalle_no_vacio AND autorizacion."""
    spec = crear_especificacion_puede_procesarse()

    # Caso exitoso: cumple las 3 condiciones
    op_valida = _crear_operacion_dummy(activo=True, autorizado=True, cantidad=1)
    assert spec.is_satisfied_by(op_valida) is True

    # Caso falla por no autorizado
    op_no_aut = _crear_operacion_dummy(activo=True, autorizado=False, cantidad=1)
    assert spec.is_satisfied_by(op_no_aut) is False

    # Caso falla por cliente inactivo
    op_inactiva = _crear_operacion_dummy(activo=False, autorizado=True, cantidad=1)
    assert spec.is_satisfied_by(op_inactiva) is False

    # Caso falla por detalle vacío
    op_vacia = _crear_operacion_dummy(activo=True, autorizado=True, cantidad=0)
    assert spec.is_satisfied_by(op_vacia) is False


def test_beneficio_referencia_specification():
    """Valida la Regla 2 del docente: VIP AND total >= 1500 AND NOT promocion."""
    spec = crear_especificacion_beneficio_referencia(Decimal("1500.00"))

    # Éxito: VIP, total=2000 (>=1500), sin promoción
    op_exito = _crear_operacion_dummy(
        es_preferente=True,
        precio=Decimal("1000.00"),
        cantidad=2,  # 2 * 1000 = 2000 >= 1500
        promocion_activa=False,
    )
    assert spec.is_satisfied_by(op_exito) is True

    # Falla: No es VIP
    op_no_vip = _crear_operacion_dummy(
        es_preferente=False,
        precio=Decimal("1000.00"),
        cantidad=2,
        promocion_activa=False,
    )
    assert spec.is_satisfied_by(op_no_vip) is False

    # Falla: Total < 1500 (ej. 1000)
    op_total_bajo = _crear_operacion_dummy(
        es_preferente=True,
        precio=Decimal("500.00"),
        cantidad=2,  # 1000 < 1500
        promocion_activa=False,
    )
    assert spec.is_satisfied_by(op_total_bajo) is False

    # Falla: Tiene promoción activa
    op_con_promo = _crear_operacion_dummy(
        es_preferente=True,
        precio=Decimal("1000.00"),
        cantidad=2,
        promocion_activa=True,
    )
    assert spec.is_satisfied_by(op_con_promo) is False


def test_stock_suficiente_specification():
    spec = StockSuficienteSpecification()

    # Stock suficiente (10 stock >= 2 cantidad)
    op_ok = _crear_operacion_dummy(stock=10, cantidad=2, habilitado=True)
    assert spec.is_satisfied_by(op_ok) is True

    # Stock insuficiente (1 stock < 5 cantidad)
    op_insuficiente = _crear_operacion_dummy(stock=1, cantidad=5, habilitado=True)
    assert spec.is_satisfied_by(op_insuficiente) is False

    # Recurso deshabilitado
    op_deshabilitado = _crear_operacion_dummy(stock=10, cantidad=2, habilitado=False)
    assert spec.is_satisfied_by(op_deshabilitado) is False
