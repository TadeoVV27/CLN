import pytest

from src.domain.models import (
    Cotizacion,
    Credito,
    Inventario,
    Pedido,
    Venta,
    Transferencia,
)


def test_cotizacion_vigente():
    cotizacion = Cotizacion(id_cotizacion=1, vigente=True)
    cotizacion.validar_vigencia()


def test_cotizacion_vencida():
    cotizacion = Cotizacion(id_cotizacion=2, vigente=False)

    with pytest.raises(ValueError, match="vencida"):
        cotizacion.validar_vigencia()


def test_credito_autorizado():
    credito = Credito(autorizado=True)
    credito.validar_autorizacion()


def test_credito_no_autorizado():
    credito = Credito(autorizado=False)

    with pytest.raises(ValueError, match="no está autorizada"):
        credito.validar_autorizacion()


def test_inventario_disponible():
    inventario = Inventario(existencia=20, comprometido=5)
    inventario.verificar_disponibilidad(10)


def test_inventario_insuficiente():
    inventario = Inventario(existencia=5, comprometido=2)

    with pytest.raises(ValueError, match="Inventario insuficiente"):
        inventario.verificar_disponibilidad(4)


def test_descontar_inventario():
    inventario = Inventario(existencia=20)
    inventario.descontar_existencia(5)

    assert inventario.existencia == 15


def test_descontar_inventario_insuficiente():
    inventario = Inventario(existencia=3)

    with pytest.raises(ValueError, match="Inventario insuficiente"):
        inventario.descontar_existencia(5)

    assert inventario.existencia == 3


def test_pedido_parcial():
    pedido = Pedido(id_pedido=1, estado="Pendiente")
    pedido.marcar_parcial()

    assert pedido.estado == "Parcial"


def test_confirmar_venta():
    venta = Venta(id_venta=1)
    venta.confirmar()

    assert venta.estado == "Confirmada"


def test_venta_estado_inicial():
    venta = Venta(id_venta=2)

    assert venta.estado == "Pendiente"


def test_transferencia_estado_inicial():
    transferencia = Transferencia(id_transferencia=1)

    assert transferencia.estado == "Solicitada"
