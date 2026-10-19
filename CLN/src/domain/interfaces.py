# src/domain/interfaces.py
from abc import ABC, abstractmethod

class ICotizacionRepository(ABC):
    @abstractmethod
    def buscarCotizacionPorId(self, id_cotizacion: str):
        """Recupera la entidad Cotizacion desde la base de datos."""
        pass

class IUnitOfWork(ABC):
    @abstractmethod
    def iniciar(self):
        """Inicia la transacción."""
        pass
        
    @abstractmethod
    def confirmar(self):
        """Confirma los cambios (commit)."""
        pass
        
    @abstractmethod
    def revertir(self):
        """Revierte los cambios en caso de error (rollback)."""
        pass