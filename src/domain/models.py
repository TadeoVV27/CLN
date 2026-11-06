from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from src.domain.state_machine import OperacionStateMachine, EstadoOperacion
from src.domain.events import DomainEvent, OperacionCreadaEvent


# ============================================================================
# ENTIDADES DEL DATASET OFICIAL DEL DOCENTE (FerreMax PIA)
# ============================================================================

@dataclass
class Actor:
    """Comprador / Cliente en FerreMax."""
    actor_id: str
    nombre: str
    es_preferente: bool = False
    activo: bool = True
    ciudad: str = "Monterrey"


@dataclass
class Recurso:
    """Artículo ferretero en catálogo (taladro, tornillo, pintura, martillo)."""
    recurso_id: str
    descripcion: str
    precio_mxn: Decimal
    capacidad_o_stock: int
    habilitado: bool = True

    def __post_init__(self):
        if not isinstance(self.precio_mxn, Decimal):
            self.precio_mxn = Decimal(str(self.precio_mxn))


@dataclass
class DetalleOperacion:
    """Línea de detalle de una operación (recurso y cantidad)."""
    operacion_id: str
    recurso_id: str
    cantidad: int
    recurso: Optional[Recurso] = None

    def calcular_subtotal(self) -> Decimal:
        if self.recurso:
            return self.recurso.precio_mxn * Decimal(self.cantidad)
        return Decimal("0.00")


@dataclass
class Operacion:
    """
    Agregado raíz Operacion.
    Coordina detalles, actor, totalización y máquina de estados.
    """
    operacion_id: str
    actor_id: str
    estado_inicial: str = "CREADO"
    fecha_solicitud: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    promocion_activa: bool = False
    autorizado: bool = False
    referencia: str = ""
    actor: Optional[Actor] = None
    lineas: List[DetalleOperacion] = field(default_factory=list)

    def __post_init__(self):
        self._state_machine = OperacionStateMachine(self.estado_inicial)

    @property
    def estado(self) -> str:
        return self._state_machine.estado.value

    @property
    def eventos(self) -> List[DomainEvent]:
        return self._state_machine.eventos

    def calcular_total(self) -> Decimal:
        """Calcula total = suma(precio_mxn * cantidad) usando Decimal."""
        total = Decimal("0.00")
        for linea in self.lineas:
            total += linea.calcular_subtotal()
        return total

    # Delegación de máquina de estados
    def aprobar(self):
        return self._state_machine.aprobar(
            self.operacion_id, self.actor_id, float(self.calcular_total())
        )

    def surtir(self):
        return self._state_machine.surtir(self.operacion_id, len(self.lineas))

    def entregar(self):
        return self._state_machine.entregar(self.operacion_id)

    def completar(self):
        return self._state_machine.completar(
            self.operacion_id, self.actor_id, float(self.calcular_total()), len(self.lineas)
        )

    def cancelar(self, motivo: str = "Cancelado"):
        return self._state_machine.cancelar(self.operacion_id, motivo)


# ============================================================================
# ENTIDADES PREVIAS (COMPATIBILIDAD CON SERVICIOS EXISTENTES)
# ============================================================================

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
