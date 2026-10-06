from dataclasses import dataclass


@dataclass
class Cotizacion:
    id_cotizacion: int
    vigente: bool

    def validar_vigencia(self):
        if not self.vigente:
            raise ValueError("La cotización se encuentra vencida.")


@dataclass
class Credito:
    autorizado: bool

    def validar_autorizacion(self):
        if not self.autorizado:
            raise ValueError("La operación de crédito no está autorizada.")


@dataclass
class Inventario:
    existencia: int
    comprometido: int = 0

    def verificar_disponibilidad(self, cantidad: int):
        disponible = self.existencia - self.comprometido

        if disponible < cantidad:
            raise ValueError("Inventario insuficiente.")

    def descontar_existencia(self, cantidad: int):
        self.verificar_disponibilidad(cantidad)
        self.existencia -= cantidad


@dataclass
class Pedido:
    id_pedido: int
    estado: str

    def marcar_parcial(self):
        self.estado = "Parcial"


@dataclass
class Venta:
    id_venta: int
    estado: str = "Pendiente"

    def confirmar(self):
        self.estado = "Confirmada"


@dataclass
class Transferencia:
    id_transferencia: int
    estado: str = "Solicitada"