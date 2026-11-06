# src/domain/specifications.py
"""
Patrón Specification (Domain-Driven Design - Evans & Fowler) para FerreMax.
Permite encapsular reglas de negocio atómicas y combinarlas mediante
álgebra booleana (AND, OR, NOT) con sobrecarga de operadores (&, |, ~).
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


class Specification(ABC):
    """Clase base abstracta para el patrón Specification."""

    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        """Evalúa si el candidato cumple con la regla de negocio."""
        pass

    def __and__(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def and_(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)

    def or_(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification":
        return NotSpecification(self)

    def not_(self) -> "NotSpecification":
        return NotSpecification(self)


class AndSpecification(Specification):
    """Composición lógica AND entre dos especificaciones."""

    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

    def __repr__(self) -> str:
        return f"({self.left} AND {self.right})"


class OrSpecification(Specification):
    """Composición lógica OR entre dos especificaciones."""

    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

    def __repr__(self) -> str:
        return f"({self.left} OR {self.right})"


class NotSpecification(Specification):
    """Negación lógica NOT de una especificación."""

    def __init__(self, spec: Specification):
        self.spec = spec

    def is_satisfied_by(self, candidate: Any) -> bool:
        return not self.spec.is_satisfied_by(candidate)

    def __repr__(self) -> str:
        return f"(NOT {self.spec})"


# ============================================================================
# ESPECIFICACIONES CONCRETAS DE DOMINIO FERREMAX
# ============================================================================

class ActorActivoSpecification(Specification):
    """Regla: El comprador/actor debe estar activo en el sistema."""

    def is_satisfied_by(self, operacion: Any) -> bool:
        actor = getattr(operacion, "actor", None)
        if not actor:
            return False
        return bool(getattr(actor, "activo", False))

    def __repr__(self) -> str:
        return "ActorActivo"


class DetalleNoVacioSpecification(Specification):
    """Regla: La operación debe tener al menos una línea de detalle."""

    def is_satisfied_by(self, operacion: Any) -> bool:
        lineas = getattr(operacion, "lineas", [])
        return len(lineas) > 0

    def __repr__(self) -> str:
        return "DetalleNoVacio"


class OperacionAutorizadaSpecification(Specification):
    """Regla: La operación debe contar con autorización administrativa previa."""

    def is_satisfied_by(self, operacion: Any) -> bool:
        return bool(getattr(operacion, "autorizado", False))

    def __repr__(self) -> str:
        return "OperacionAutorizada"


class ActorPreferenteSpecification(Specification):
    """Regla: El actor debe ser cliente preferente (VIP)."""

    def is_satisfied_by(self, operacion: Any) -> bool:
        actor = getattr(operacion, "actor", None)
        if not actor:
            return False
        return bool(getattr(actor, "es_preferente", False))

    def __repr__(self) -> str:
        return "ActorPreferente"


class TotalMinimoSpecification(Specification):
    """Regla: El total calculado de la operación debe ser >= monto_minimo."""

    def __init__(self, monto_minimo: Decimal = Decimal("1500.00")):
        self.monto_minimo = Decimal(str(monto_minimo))

    def is_satisfied_by(self, operacion: Any) -> bool:
        if hasattr(operacion, "calcular_total"):
            total = operacion.calcular_total()
        else:
            total = getattr(operacion, "total", Decimal("0.00"))
        return Decimal(str(total)) >= self.monto_minimo

    def __repr__(self) -> str:
        return f"TotalMinimo(>={self.monto_minimo})"


class PromocionActivaSpecification(Specification):
    """Regla: La operación tiene promoción activa."""

    def is_satisfied_by(self, operacion: Any) -> bool:
        return bool(getattr(operacion, "promocion_activa", False))

    def __repr__(self) -> str:
        return "PromocionActiva"


class StockSuficienteSpecification(Specification):
    """Regla: Todos los artículos del detalle deben tener stock disponible suficiente."""

    def is_satisfied_by(self, operacion: Any) -> bool:
        lineas = getattr(operacion, "lineas", [])
        if not lineas:
            return False
        for linea in lineas:
            recurso = getattr(linea, "recurso", None)
            if recurso is not None:
                stock = getattr(recurso, "capacidad_o_stock", 0)
                if stock < linea.cantidad or not getattr(recurso, "habilitado", True):
                    return False
        return True

    def __repr__(self) -> str:
        return "StockSuficiente"


# ============================================================================
# COMPOSICIÓN DE REGLAS OFICIALES DEL DOCENTE (LEEME.txt)
# ============================================================================

def crear_especificacion_puede_procesarse() -> Specification:
    """
    Regla 1: 'puede_procesarse'
    actor activo AND operacion con al menos una linea AND autorizacion.
    """
    return (
        ActorActivoSpecification()
        & DetalleNoVacioSpecification()
        & OperacionAutorizadaSpecification()
    )


def crear_especificacion_beneficio_referencia(monto_minimo: Decimal = Decimal("1500.00")) -> Specification:
    """
    Regla 2: 'beneficio_referencia'
    actor preferente AND total >= 1500 MXN AND NOT promocion activa.
    """
    return (
        ActorPreferenteSpecification()
        & TotalMinimoSpecification(monto_minimo)
        & ~PromocionActivaSpecification()
    )
