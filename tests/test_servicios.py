import pytest
from unittest.mock import MagicMock
from src.application.services import VentaApplicationService, ValidacionApplicationService
from src.domain.models import Inventario, Venta, Cotizacion, Credito

def test_procesar_venta_mostrador_exitosa():
    # 1. Preparar (Arrange)
    mock_venta_repo = MagicMock()
    mock_inv_repo = MagicMock()
    mock_uow = MagicMock()
    
    servicio = VentaApplicationService(mock_venta_repo, mock_inv_repo, mock_uow)
    
    venta = Venta(id_venta=1)
    inventario = Inventario(existencia=10, comprometido=0)
    cantidad_a_vender = 3

    # 2. Ejecutar (Act)
    resultado = servicio.procesar_venta_mostrador(venta, inventario, cantidad_a_vender)

    # 3. Verificar (Assert)
    assert resultado == "Venta confirmada"
    assert inventario.existencia == 7  # La lógica de dominio descontó el inventario
    assert venta.estado == "Confirmada"
    
    # Verificamos que los repositorios y UoW fueron llamados correctamente
    mock_uow.iniciar.assert_called_once()
    mock_venta_repo.guardar_venta.assert_called_once_with(venta)
    mock_inv_repo.guardar_cambios.assert_called_once_with(inventario)
    mock_uow.confirmar.assert_called_once()

def test_validar_operacion_credito_falla_por_cotizacion_vencida():
    # 1. Preparar
    mock_cot_repo = MagicMock()
    mock_uow = MagicMock()
    
    servicio = ValidacionApplicationService(mock_cot_repo, mock_uow)
    
    # Simulamos una cotización vencida y un crédito válido
    cotizacion_vencida = Cotizacion(id_cotizacion=1, vigente=False)
    credito = Credito(autorizado=True)
    
    mock_cot_repo.buscar_cotizacion_por_id.return_value = cotizacion_vencida

    # 2 & 3. Ejecutar y Verificar (Esperamos que lance un ValueError)
    with pytest.raises(ValueError, match="La cotización se encuentra vencida."):
        servicio.validar_operacion_credito(id_cotizacion=1, credito=credito)
        
    # Verificamos que si falla el dominio, NUNCA se confirme la transacción
    mock_uow.confirmar.assert_not_called()