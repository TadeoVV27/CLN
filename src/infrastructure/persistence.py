# src/infrastructure/persistence.py
"""
Implementación concreta de repositorios en memoria para FerreMax
(Arquitectura Limpia / DDD).
"""

from typing import Dict, Optional, List

try:
    from src.application.repositories import (
        IVentaRepository,
        ICotizacionRepository,
        IInventarioRepository,
        IPedidoRepository,
        IUnitOfWork,
    )
    from src.domain.models import Venta, Cotizacion, Inventario, Pedido
except ImportError:
    from application.repositories import (
        IVentaRepository,
        ICotizacionRepository,
        IInventarioRepository,
        IPedidoRepository,
        IUnitOfWork,
    )
    from domain.models import Venta, Cotizacion, Inventario, Pedido


class InMemoryVentaRepository(IVentaRepository):
    """Repositorio en memoria para Venta."""

    def __init__(self):
        self._ventas: Dict[int, Venta] = {}

    def guardar_venta(self, venta: Venta):
        self._ventas[venta.id_venta] = venta

    def buscar_venta_por_id(self, id_venta: int) -> Optional[Venta]:
        return self._ventas.get(id_venta)

    def listar_todas(self) -> List[Venta]:
        return list(self._ventas.values())


class InMemoryCotizacionRepository(ICotizacionRepository):
    """Repositorio en memoria para Cotizacion."""

    def __init__(self):
        self._cotizaciones: Dict[int, Cotizacion] = {}

    def guardar_cotizacion(self, cotizacion: Cotizacion):
        self._cotizaciones[cotizacion.id_cotizacion] = cotizacion

    def buscar_cotizacion_por_id(self, id_cotizacion: int) -> Optional[Cotizacion]:
        return self._cotizaciones.get(id_cotizacion)

    def buscarCotizacionPorId(self, id_cotizacion: int) -> Optional[Cotizacion]:
        return self.buscar_cotizacion_por_id(id_cotizacion)

    def listar_todas(self) -> List[Cotizacion]:
        return list(self._cotizaciones.values())


class InMemoryInventarioRepository(IInventarioRepository):
    """Repositorio en memoria para Inventario."""

    def __init__(self):
        self._inventarios: Dict[int, Inventario] = {}

    def guardar_cambios(self, inventario: Inventario):
        pass

    def registrar_inventario(self, id_producto: int, inventario: Inventario):
        self._inventarios[id_producto] = inventario

    def consultar_disponibilidad(self, producto_id):
        return self._inventarios.get(producto_id)

    def buscar_inventario(self, id_producto: int) -> Optional[Inventario]:
        return self._inventarios.get(id_producto)


class InMemoryPedidoRepository(IPedidoRepository):
    """Repositorio en memoria para Pedido."""

    def __init__(self):
        self._pedidos: Dict[int, Pedido] = {}

    def guardar_pedido(self, pedido: Pedido):
        self._pedidos[pedido.id_pedido] = pedido

    def buscar_pedido_por_id(self, id_pedido: int) -> Optional[Pedido]:
        return self._pedidos.get(id_pedido)

    def listar_todos(self) -> List[Pedido]:
        return list(self._pedidos.values())


class UnitOfWorkImpl(IUnitOfWork):
    """Unit of Work en memoria para control transaccional."""

    def __init__(self):
        self.en_transaccion = False
        self.confirmado = False
        self.revertido = False

    def iniciar(self):
        self.en_transaccion = True
        self.confirmado = False
        self.revertido = False

    def confirmar(self):
        if not self.en_transaccion:
            raise RuntimeError("No hay una transacción activa para confirmar.")
        self.confirmado = True
        self.en_transaccion = False

    def revertir(self):
        self.revertido = True
        self.en_transaccion = False


# Aliases para mantener compatibilidad con stubs iniciales
VentaRepositoryImpl = InMemoryVentaRepository
CotizacionRepositoryImpl = InMemoryCotizacionRepository
InventarioRepositoryImpl = InMemoryInventarioRepository
PedidoRepositoryImpl = InMemoryPedidoRepository
