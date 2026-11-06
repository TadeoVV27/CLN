# src/domain/interfaces.py
from abc import ABC, abstractmethod


class ICotizacionRepository(ABC):
    @abstractmethod
    def buscar_cotizacion_por_id(self, id_cotizacion: str):
        """Recupera una cotización por su identificador."""
        pass


class IVentaRepository(ABC):
    @abstractmethod
    def guardar_venta(self, venta):
        """Guarda una venta."""
        pass

    @abstractmethod
    def buscar_venta_por_id(self, id_venta: int):
        """Busca una venta por su identificador."""
        pass


class IInventarioRepository(ABC):
    @abstractmethod
    def guardar_cambios(self, inventario):
        """Guarda los cambios realizados al inventario."""
        pass

    @abstractmethod
    def buscar_inventario(self, id_producto: int):
        """Busca el inventario de un producto."""
        pass


class IPedidoRepository(ABC):
    @abstractmethod
    def guardar_pedido(self, pedido):
        """Guarda un pedido."""
        pass

    @abstractmethod
    def buscar_pedido_por_id(self, id_pedido: int):
        """Busca un pedido por su identificador."""
        pass


class ICreditoRepository(ABC):
    @abstractmethod
    def guardar_credito(self, credito):
        """Guarda una operación de crédito."""
        pass


class ITransferenciaRepository(ABC):
    @abstractmethod
    def guardar_transferencia(self, transferencia):
        """Guarda una transferencia."""
        pass

    @abstractmethod
    def buscar_transferencia_por_id(self, id_transferencia: int):
        """Busca una transferencia por su identificador."""
        pass


class IUnitOfWork(ABC):
    @abstractmethod
    def iniciar(self):
        """Inicia una transacción."""
        pass

    @abstractmethod
    def confirmar(self):
        """Confirma los cambios."""
        pass

    @abstractmethod
    def revertir(self):
        """Revierte los cambios si ocurre un error."""
        pass
