from abc import ABC, abstractmethod


class IVentaRepository(ABC):

    @abstractmethod
    def guardar_venta(self, venta):
        pass

    @abstractmethod
    def buscar_venta_por_id(self, id_venta):
        pass


class ICotizacionRepository(ABC):

    @abstractmethod
    def guardar_cotizacion(self, cotizacion):
        pass

    @abstractmethod
    def buscar_cotizacion_por_id(self, id_cotizacion):
        pass


class IInventarioRepository(ABC):

    @abstractmethod
    def consultar_disponibilidad(self, producto):
        pass

    @abstractmethod
    def guardar_cambios(self, inventario):
        pass


class IPedidoRepository(ABC):

    @abstractmethod
    def guardar_pedido(self, pedido):
        pass

    @abstractmethod
    def buscar_pedido_por_id(self, id_pedido):
        pass


class IUnitOfWork(ABC):

    @abstractmethod
    def iniciar(self):
        pass

    @abstractmethod
    def confirmar(self):
        pass

    @abstractmethod
    def revertir(self):
        pass