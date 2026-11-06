# src/api/routes.py
"""
Controladores y Rutas REST para FerreMax (Clean Architecture: src/api/).
Define routers modulares para operaciones, cotizaciones y almacén.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

api_router = APIRouter(prefix="/api/v1")


class TransicionRequest(BaseModel):
    accion: str


@api_router.get("/health", tags=["Salud"])
def health_check():
    """Verifica que el servicio y la lógica de negocio se encuentren operativos."""
    return {"status": "ok", "servicio": "FerreMax Core API", "version": "1.0.0"}
