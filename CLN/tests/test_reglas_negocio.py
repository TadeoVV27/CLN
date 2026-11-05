
import pytest
from unittest.mock import Mock, patch

import sys
import os

# Ajustar path para importar desde la raíz del subproyecto CLN/CLN
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.domain.models import (
    Cotizacion,
    Credito,
    Inventario,
    Pedido,
    Venta,
    Transferencia,
)
from src.application.services import (
    VentaApplicationService,
    ValidacionApplicationService,
    InventarioApplicationService,
)


# ============================================================================
# REPOSITORIOS IN-MEMORY (para pruebas de persistencia)
# ============================================================================

class InMemoryCotizacionRepository:
    """Implementación de repositorio en memoria para Cotización."""

    def __init__(self):
        self._storage = {}

    def guardar_cotizacion(self, cotizacion: Cotizacion):
        self._storage[cotizacion.id_cotizacion] = cotizacion

    def buscar_cotizacion_por_id(self, id_cotizacion: int):
        return self._storage.get(id_cotizacion)


class InMemoryVentaRepository:
    """Implementación de repositorio en memoria para Venta."""

    def __init__(self):
        self._storage = {}

    def guardar_venta(self, venta: Venta):
        self._storage[venta.id_venta] = venta

    def buscar_venta_por_id(self, id_venta: int):
        return self._storage.get(id_venta)


class InMemoryInventarioRepository:
    """Implementación de repositorio en memoria para Inventario."""

    def __init__(self):
        self._storage = {}

    def guardar_cambios(self, inventario: Inventario):
        self._storage["inv"] = inventario

    def consultar_disponibilidad(self, producto):
        return self._storage.get(producto)


# ============================================================================
# RN-01: VIGENCIA DE COTIZACIÓN
# "Una cotización vencida impide cualquier operación empresarial."
# ============================================================================

class TestRN01VigenciaCotizacion:
    """Regla de Negocio 01 - Validación de vigencia de cotización."""

    def test_exito_cotizacion_vigente(self):
        """ÉXITO: Una cotización vigente permite continuar la operación."""
        cotizacion = Cotizacion(id_cotizacion=1, vigente=True)

        # No debe lanzar excepción
        cotizacion.validar_vigencia()

    def test_error_cotizacion_vencida(self):
        """ERROR: Una cotización vencida detiene la operación."""
        cotizacion = Cotizacion(id_cotizacion=2, vigente=False)

        with pytest.raises(ValueError, match="vencida"):
            cotizacion.validar_vigencia()

    def test_edge_cotizacion_recien_creada_vigente(self):
        """EDGE CASE: Una cotización recién creada (id mínimo) debe ser vigente
        si se marcó como vigente, incluso con id_cotizacion = 0."""
        cotizacion = Cotizacion(id_cotizacion=0, vigente=True)

        # No debe lanzar excepción aunque el id sea 0
        cotizacion.validar_vigencia()
        assert cotizacion.vigente is True


# ============================================================================
# RN-02: AUTORIZACIÓN DE CRÉDITO
# "Una operación a crédito no puede continuar sin autorización previa."
# ============================================================================

class TestRN02AutorizacionCredito:
    """Regla de Negocio 02 - Validación de autorización de crédito."""

    def test_exito_credito_autorizado(self):
        """ÉXITO: Un crédito autorizado permite continuar la operación."""
        credito = Credito(autorizado=True)

        # No debe lanzar excepción
        credito.validar_autorizacion()

    def test_error_credito_no_autorizado(self):
        """ERROR: Un crédito no autorizado rechaza la operación."""
        credito = Credito(autorizado=False)

        with pytest.raises(ValueError, match="no está autorizada"):
            credito.validar_autorizacion()

    def test_edge_validacion_operacion_credito_completa(self):
        """EDGE CASE: Validar la orquestación completa de cotización vigente +
        crédito autorizado a través del servicio de aplicación con mocks."""
        mock_repo = Mock()
        mock_uow = Mock()

        cotizacion = Cotizacion(id_cotizacion=99, vigente=True)
        credito = Credito(autorizado=True)

        # El repositorio retorna la cotización cuando se busca por id
        mock_repo.buscar_cotizacion_por_id.return_value = cotizacion

        servicio = ValidacionApplicationService(mock_repo, mock_uow)

        resultado = servicio.validar_operacion_credito(99, credito)
        assert resultado == "Operación autorizada"
        mock_repo.buscar_cotizacion_por_id.assert_called_once_with(99)
        mock_uow.iniciar.assert_called_once()
        mock_uow.confirmar.assert_called_once()


# ============================================================================
# RN-03: DISPONIBILIDAD DE INVENTARIO
# "No se puede vender si la cantidad solicitada excede el inventario disponible
#  (existencia - comprometido)."
# ============================================================================

class TestRN03DisponibilidadInventario:
    """Regla de Negocio 03 - Verificación de disponibilidad de inventario."""

    def test_exito_inventario_suficiente(self):
        """ÉXITO: Con inventario suficiente, la verificación pasa sin error."""
        inventario = Inventario(existencia=50, comprometido=10)

        # Solicitar 30 unidades — disponible es 40 (50 - 10)
        inventario.verificar_disponibilidad(30)

    def test_error_inventario_insuficiente(self):
        """ERROR: Si la cantidad excede lo disponible, se lanza error."""
        inventario = Inventario(existencia=10, comprometido=8)

        # Disponible: 10 - 8 = 2, solicitar 5 → insuficiente
        with pytest.raises(ValueError, match="Inventario insuficiente"):
            inventario.verificar_disponibilidad(5)

    def test_edge_inventario_exacto_al_limite(self):
        """EDGE CASE: Solicitar exactamente lo disponible (disponible == cantidad).
        Debe permitirse sin error ya que no es menor."""
        inventario = Inventario(existencia=10, comprometido=5)

        # Disponible: 10 - 5 = 5, solicitar exactamente 5
        inventario.verificar_disponibilidad(5)

        # Ahora descontar las 5 unidades
        inventario.descontar_existencia(5)
        assert inventario.existencia == 5


# ============================================================================
# PRUEBA DE PERSISTENCIA (Repositorio In-Memory)
# ============================================================================

class TestPersistencia:
    """Pruebas de persistencia usando repositorios en memoria."""

    def test_persistencia_guardar_y_recuperar_venta(self):
        """Verifica que una Venta se persiste y se recupera correctamente
        manteniendo la integridad de sus atributos de dominio."""
        repo = InMemoryVentaRepository()

        # Crear y confirmar una venta
        venta = Venta(id_venta=100)
        venta.confirmar()

        # Persistir
        repo.guardar_venta(venta)

        # Recuperar
        venta_recuperada = repo.buscar_venta_por_id(100)

        # Verificar integridad
        assert venta_recuperada is not None
        assert venta_recuperada.id_venta == 100
        assert venta_recuperada.estado == "Confirmada"

    def test_persistencia_buscar_inexistente_retorna_none(self):
        """Verifica que buscar un ID inexistente retorna None."""
        repo = InMemoryVentaRepository()

        resultado = repo.buscar_venta_por_id(999)
        assert resultado is None


# ============================================================================
# PRUEBA CON MOCK (Servicio de Aplicación con dependencias externas)
# ============================================================================

class TestMockServicioVenta:
    """Pruebas con mock para el servicio de aplicación VentaApplicationService,
    aislando los repositorios e infraestructura externos."""

    def test_mock_procesar_venta_mostrador_exitosa(self):
        """Verifica que el servicio orquesta correctamente la venta:
        descuenta inventario, confirma venta, y persiste a través de repos."""
        # Arrange: Mocks de repositorios y unit of work
        mock_venta_repo = Mock()
        mock_inventario_repo = Mock()
        mock_uow = Mock()

        servicio = VentaApplicationService(
            mock_venta_repo, mock_inventario_repo, mock_uow
        )

        venta = Venta(id_venta=200)
        inventario = Inventario(existencia=50, comprometido=0)
        cantidad = 10

        # Act
        resultado = servicio.procesar_venta_mostrador(venta, inventario, cantidad)

        # Assert: resultado correcto
        assert resultado == "Venta confirmada"
        assert venta.estado == "Confirmada"
        assert inventario.existencia == 40  # 50 - 10

        # Assert: interacciones con infraestructura
        mock_uow.iniciar.assert_called_once()
        mock_uow.confirmar.assert_called_once()
        mock_venta_repo.guardar_venta.assert_called_once_with(venta)
        mock_inventario_repo.guardar_cambios.assert_called_once_with(inventario)

    def test_mock_procesar_venta_con_inventario_insuficiente_revierte(self):
        """Verifica que si el inventario es insuficiente, la operación
        NO inicia el unit of work y lanza error."""
        mock_venta_repo = Mock()
        mock_inventario_repo = Mock()
        mock_uow = Mock()

        servicio = VentaApplicationService(
            mock_venta_repo, mock_inventario_repo, mock_uow
        )

        venta = Venta(id_venta=201)
        inventario = Inventario(existencia=5, comprometido=3)
        cantidad = 10  # Disponible: 5 - 3 = 2, insuficiente

        # Act & Assert
        with pytest.raises(ValueError, match="Inventario insuficiente"):
            servicio.procesar_venta_mostrador(venta, inventario, cantidad)

        # La venta NO debe haberse confirmado
        assert venta.estado == "Pendiente"

        # El unit of work NO debe haberse iniciado (falla antes)
        mock_uow.iniciar.assert_not_called()
        mock_uow.confirmar.assert_not_called()
