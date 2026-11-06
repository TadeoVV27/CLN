# src/main.py
"""
API REST y Servidor Web FerreMax (FastAPI)
Incluye documentación interactiva Swagger (/docs) y Frontend de Mostrador/Caja.
"""

import os
import sys
import subprocess
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Asegurar path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.application.commands import (
    CrearCotizacionCommand, 
    AutorizarCreditoCommand
)
from src.domain.models import Cotizacion, Credito, Inventario, Pedido, Venta
from src.application.services import (
    VentaApplicationService,
    ValidacionApplicationService,
    InventarioApplicationService,
)
from src.infrastructure.persistence import (
    InMemoryVentaRepository,
    InMemoryCotizacionRepository,
    InMemoryInventarioRepository,
    InMemoryPedidoRepository,
    UnitOfWorkImpl,
)

# Inicializamos FastAPI con metadata completa
app = FastAPI(
    title="API FerreMax - Sistema de Mostrador y Caja",
    description="API REST y Sistema de Mostrador para ventas, crédito e inventario de FerreMax.",
    version="1.0.0"
)

# ----------------------------------------------------------------------------
# DEPENDENCIAS E INSTANCIAS DE SERVICIO (Clean Architecture)
# ----------------------------------------------------------------------------
venta_repo = InMemoryVentaRepository()
cotizacion_repo = InMemoryCotizacionRepository()
inventario_repo = InMemoryInventarioRepository()
pedido_repo = InMemoryPedidoRepository()
unit_of_work = UnitOfWorkImpl()

venta_service = VentaApplicationService(venta_repo, inventario_repo, unit_of_work)
validacion_service = ValidacionApplicationService(cotizacion_repo, unit_of_work)
inventario_service = InventarioApplicationService(inventario_repo, pedido_repo, unit_of_work)

# Catálogo ferretero con inventario enlazado
PRODUCTOS = [
    {
        "id": 1,
        "codigo": "CEM-001",
        "nombre": "Cemento Gris Tolteca 50kg",
        "categoria": "Material de Obra",
        "precio": 245.0,
        "unidad": "Bulto",
        "icono": "🧱",
        "inventario": Inventario(existencia=60, comprometido=5),
    },
    {
        "id": 2,
        "codigo": "VAR-038",
        "nombre": 'Varilla Corrugada 3/8" (12m)',
        "categoria": "Acero",
        "precio": 185.0,
        "unidad": "Pieza",
        "icono": "🏗️",
        "inventario": Inventario(existencia=120, comprometido=10),
    },
    {
        "id": 3,
        "codigo": "TAL-650",
        "nombre": 'Taladro Percutor 1/2" 650W Industrial',
        "categoria": "Herramienta Eléctrica",
        "precio": 1250.0,
        "unidad": "Pieza",
        "icono": "⚡",
        "inventario": Inventario(existencia=8, comprometido=0),
    },
    {
        "id": 4,
        "codigo": "PIN-019",
        "nombre": "Pintura Vinílica Blanca 19L ProMax",
        "categoria": "Acabados",
        "precio": 890.0,
        "unidad": "Cubeta",
        "icono": "🪣",
        "inventario": Inventario(existencia=15, comprometido=2),
    },
    {
        "id": 5,
        "codigo": "MAR-016",
        "nombre": "Martillo de Uña Curva 16oz Mango Fibra",
        "categoria": "Herramienta Manual",
        "precio": 165.0,
        "unidad": "Pieza",
        "icono": "🔨",
        "inventario": Inventario(existencia=30, comprometido=0),
    },
    {
        "id": 6,
        "codigo": "CAR-005",
        "nombre": "Carretilla Reforzada 5.5 ft³ Llanta Neumática",
        "categoria": "Carga y Transporte",
        "precio": 1450.0,
        "unidad": "Pieza",
        "icono": "🛒",
        "inventario": Inventario(existencia=5, comprometido=1),
    },
    {
        "id": 7,
        "codigo": "DIS-045",
        "nombre": 'Disco de Corte Metal 4-1/2" Extra Fino',
        "categoria": "Abrasivos",
        "precio": 28.0,
        "unidad": "Pieza",
        "icono": "💿",
        "inventario": Inventario(existencia=50, comprometido=0),
    },
    {
        "id": 8,
        "codigo": "CLA-025",
        "nombre": 'Clavo con Cabeza para Madera 2-1/2" (Caja 1kg)',
        "categoria": "Fijación",
        "precio": 48.0,
        "unidad": "Caja",
        "icono": "🔩",
        "inventario": Inventario(existencia=45, comprometido=0),
    },
]

for p in PRODUCTOS:
    inventario_repo.registrar_inventario(p["id"], p["inventario"])

COTIZACIONES_DEMO = [
    {
        "id": 101,
        "folio": "COT-101",
        "cliente": "Constructora Regia S.A. de C.V.",
        "monto": 34850.0,
        "vigente": True,
        "credito_autorizado": True,
        "descripcion": "50 Bultos de Cemento + 40 Varillas 3/8",
    },
    {
        "id": 102,
        "folio": "COT-102",
        "cliente": "Obras y Acabados del Norte",
        "monto": 12400.0,
        "vigente": False,
        "credito_autorizado": True,
        "descripcion": "8 Cubetas de Pintura + 12 Discos de Corte (VENCIDA HACE 4 DÍAS)",
    },
    {
        "id": 103,
        "folio": "COT-103",
        "cliente": "Juan Pérez (Contratista Independiente)",
        "monto": 8750.0,
        "vigente": True,
        "credito_autorizado": False,
        "descripcion": "2 Carretillas + 4 Taladros (CRÉDITO BLOQUEADO POR COBRANZA)",
    },
]

for cot in COTIZACIONES_DEMO:
    cotizacion_repo.guardar_cotizacion(
        Cotizacion(id_cotizacion=cot["id"], vigente=cot["vigente"])
    )

_contador_ventas = 1000
HISTORIAL_VENTAS = []


# ----------------------------------------------------------------------------
# ENDPOINTS REST EXISTENTES (CONSERVADOS DEL COMMIT DEL EQUIPO)
# ----------------------------------------------------------------------------
@app.post("/cotizaciones/", tags=["Cotizaciones"], status_code=status.HTTP_201_CREATED)
def crear_cotizacion(comando: CrearCotizacionCommand):
    """
    Registra una nueva cotización en el sistema.
    - **cliente_id**: Identificador numérico del cliente.
    - **productos_ids**: Lista con los identificadores de los productos.
    - **cantidades**: Lista con las cantidades a cotizar por producto.
    """
    return {"mensaje": "Comando de cotización recibido exitosamente", "datos": comando}


@app.post("/creditos/autorizar", tags=["Créditos"], status_code=status.HTTP_200_OK)
def autorizar_credito(comando: AutorizarCreditoCommand):
    """
    Procesa la autorización de crédito para un cliente.
    - Requiere el monto solicitado y el ID del cliente.
    - Internamente delegará la validación al ValidacionApplicationService.
    """
    return {"mensaje": "Solicitud de autorización en proceso", "cliente_id": comando.cliente_id}


# ----------------------------------------------------------------------------
# MODELOS PYDANTIC PARA EL FRONTEND DE MOSTRADOR
# ----------------------------------------------------------------------------
class VentaRequest(BaseModel):
    producto_id: int
    cantidad: int

class ValidarCreditoRequest(BaseModel):
    id_cotizacion: int
    folio: str
    cliente: str
    vigente: bool
    credito_autorizado: bool

class FaltanteRequest(BaseModel):
    producto_id: int
    cantidad: int
    id_pedido: int = 501


# ----------------------------------------------------------------------------
# ENDPOINTS PARA EL FRONTEND FERRETERO
# ----------------------------------------------------------------------------
@app.get("/api/productos", tags=["Mostrador"])
def listar_productos():
    """Retorna el catálogo de productos con stock en tiempo real."""
    datos = []
    for p in PRODUCTOS:
        inv = p["inventario"]
        disponible = inv.existencia - inv.comprometido
        datos.append({
            "id": p["id"],
            "codigo": p["codigo"],
            "nombre": p["nombre"],
            "categoria": p["categoria"],
            "precio": p["precio"],
            "unidad": p["unidad"],
            "icono": p["icono"],
            "existencia": inv.existencia,
            "comprometido": inv.comprometido,
            "disponible": disponible,
        })
    return {"ok": True, "productos": datos}


@app.post("/api/venta/procesar", tags=["Mostrador"])
def procesar_venta(req: VentaRequest):
    """
    CU-01: Procesa una venta en mostrador usando VentaApplicationService.
    Descuenta inventario y confirma transacción en Unit of Work.
    """
    global _contador_ventas
    producto = next((p for p in PRODUCTOS if p["id"] == req.producto_id), None)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if req.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")

    inventario = producto["inventario"]
    _contador_ventas += 1
    id_venta = _contador_ventas
    venta = Venta(id_venta=id_venta)

    try:
        resultado = venta_service.procesar_venta_mostrador(venta, inventario, req.cantidad)
        total = round(producto["precio"] * req.cantidad, 2)
        ticket = {
            "folio": f"VTA-{id_venta}",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "producto": producto["nombre"],
            "codigo": producto["codigo"],
            "precio_unitario": producto["precio"],
            "cantidad": req.cantidad,
            "total": total,
            "estado": venta.estado,
            "stock_restante": inventario.existencia,
            "mensaje": resultado,
        }
        HISTORIAL_VENTAS.insert(0, ticket)
        return {
            "ok": True,
            "mensaje": "¡VENTA CONFIRMADA! Cobro registrado y entrega autorizada.",
            "ticket": ticket,
        }
    except ValueError as e:
        disponible = inventario.existencia - inventario.comprometido
        raise HTTPException(
            status_code=400,
            detail={
                "mensaje": f"NO SE PUEDE VENDER: {str(e)}",
                "detalle": f"Solicitaste {req.cantidad} {producto['unidad']}(s), pero en bodega solo hay {disponible} disponibles.",
                "disponible": disponible,
            }
        )


@app.get("/api/cotizaciones", tags=["Créditos"])
def listar_cotizaciones():
    """Retorna las cotizaciones registradas para prueba rápida."""
    return {"ok": True, "cotizaciones": COTIZACIONES_DEMO}


@app.post("/api/credito/validar", tags=["Créditos"])
def validar_credito_cotizacion(req: ValidarCreditoRequest):
    """
    CU-03: Valida cotización vigente y crédito autorizado.
    """
    cotizacion = Cotizacion(id_cotizacion=req.id_cotizacion, vigente=req.vigente)
    cotizacion_repo.guardar_cotizacion(cotizacion)
    credito = Credito(autorizado=req.credito_autorizado)

    try:
        resultado = validacion_service.validar_operacion_credito(req.id_cotizacion, credito)
        return {
            "ok": True,
            "autorizado": True,
            "mensaje": "✅ OPERACIÓN AUTORIZADA PARA DESPACHO A CRÉDITO",
            "detalle": f"La cotización {req.folio} está vigente y la línea de crédito para {req.cliente} fue aprobada con éxito.",
        }
    except ValueError as e:
        err = str(e)
        if "vencida" in err.lower():
            titulo = "⛔ OPERACIÓN DETENIDA: COTIZACIÓN VENCIDA"
            detalle = f"La cotización {req.folio} ha caducado. El cliente debe solicitar una re-cotización con precios actualizados."
        else:
            titulo = "⛔ OPERACIÓN RECHAZADA: CRÉDITO NO AUTORIZADO"
            detalle = f"El departamento de crédito/cobranza no autorizó la operación a {req.cliente}. Solicitar pago de contado."
        
        raise HTTPException(
            status_code=400,
            detail={"mensaje": titulo, "detalle": detalle}
        )


@app.post("/api/almacen/gestionar-faltante", tags=["Almacén"])
def gestionar_faltante(req: FaltanteRequest):
    """
    CU-04: Gestiona faltante de inventario. Si no alcanza, marca pedido como Parcial.
    """
    producto = next((p for p in PRODUCTOS if p["id"] == req.producto_id), None)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    inventario = producto["inventario"]
    pedido = Pedido(id_pedido=req.id_pedido, estado="Pendiente")
    pedido_repo.guardar_pedido(pedido)

    resultado = inventario_service.gestionar_faltante_inventario(inventario, req.cantidad, pedido)
    disponible = inventario.existencia - inventario.comprometido
    es_parcial = pedido.estado == "Parcial"

    return {
        "ok": True,
        "mensaje": resultado,
        "estado_pedido": pedido.estado,
        "es_parcial": es_parcial,
        "solicitado": req.cantidad,
        "disponible_actual": disponible,
        "detalle": (
            f"Pedido #{req.id_pedido} marcado como PARCIAL. Solo se pueden entregar {disponible} piezas. "
            f"Se generó solicitud de transferencia para el resto."
            if es_parcial
            else f"Inventario suficiente para surtir las {req.cantidad} piezas completas."
        ),
    }


@app.get("/api/ventas/historial", tags=["Mostrador"])
def historial_ventas():
    return {"ok": True, "ventas": HISTORIAL_VENTAS}


@app.post("/api/pruebas/ejecutar", tags=["Auditoría PIA"])
def ejecutar_pruebas():
    """Ejecuta pytest en el servidor y retorna el resultado."""
    test_path = os.path.join(BASE_DIR, "tests")
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=BASE_DIR,
        )
        return {
            "ok": res.returncode == 0,
            "salida": res.stdout + "\n" + res.stderr,
            "exito": res.returncode == 0,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ----------------------------------------------------------------------------
# RUTA RAÍZ: FRONTEND DEL MOSTRADOR FERRETERO
# ----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["Interfaz"])
def frontend_mostrador():
    """Entrega la interfaz gráfica para el trabajador de FerreMax."""
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>FerreMax: templates/index.html no encontrado</h1>"


if __name__ == "__main__":
    import uvicorn
    print("=" * 65)
    print(" 🛠️  FERREMAX POS - SISTEMA DE MOSTRADOR Y CAJA (FASTAPI) 🛠️")
    print("=" * 65)
    print(" -> Mostrador: http://localhost:8000")
    print(" -> Documentación Swagger API: http://localhost:8000/docs")
    print("=" * 65)
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
