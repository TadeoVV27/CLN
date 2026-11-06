from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import List

# Importamos los comandos que creaste previamente
from src.application.commands import (
    CrearCotizacionCommand, 
    AutorizarCreditoCommand
)

# Inicializamos la aplicación configurando la metadata para Swagger
app = FastAPI(
    title="API FerreMax",
    description="API REST para el sistema de gestión de ventas, crédito e inventario de FerreMax.",
    version="1.0.0"
)

@app.post("/cotizaciones/", tags=["Cotizaciones"], status_code=status.HTTP_201_CREATED)
def crear_cotizacion(comando: CrearCotizacionCommand):
    """
    Registra una nueva cotización en el sistema.
    
    - **cliente_id**: Identificador numérico del cliente.
    - **productos_ids**: Lista con los identificadores de los productos.
    - **cantidades**: Lista con las cantidades a cotizar por producto.
    """
    # Aquí es donde FastAPI pasaría el 'comando' a los servicios de Tadeo
    return {"mensaje": "Comando de cotización recibido exitosamente", "datos": comando}

@app.post("/creditos/autorizar", tags=["Créditos"], status_code=status.HTTP_200_OK)
def autorizar_credito(comando: AutorizarCreditoCommand):
    """
    Procesa la autorización de crédito para un cliente.
    
    - Requiere el monto solicitado y el ID del cliente.
    - Internamente delegará la validación al ValidacionApplicationService.
    """
    return {"mensaje": "Solicitud de autorización en proceso", "cliente_id": comando.cliente_id}