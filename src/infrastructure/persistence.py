from application.repositories import (
    IVentaRepository,
    ICotizacionRepository,
    IInventarioRepository,
    IPedidoRepository,
    IUnitOfWork
)


class VentaRepositoryImpl(IVentaRepository):

    def guardar_venta(self, venta):
        pass

    def buscar_venta_por_id(self, id_venta):
        pass


class CotizacionRepositoryImpl(ICotizacionRepository):

    def guardar_cotizacion(self, cotizacion):
        pass

    def buscar_cotizacion_por_id(self, id_cotizacion):
        pass


class InventarioRepositoryImpl(IInventarioRepository):

    def consultar_disponibilidad(self, producto):
        pass

    def guardar_cambios(self, inventario):
        pass


class PedidoRepositoryImpl(IPedidoRepository):

    def guardar_pedido(self, pedido):
        pass

    def buscar_pedido_por_id(self, id_pedido):
        pass


class UnitOfWorkImpl(IUnitOfWork):

    def iniciar(self):
        pass

    def confirmar(self):
        pass

    def revertir(self):
        pass