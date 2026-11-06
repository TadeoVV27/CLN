# src/application/services.py

class VentaApplicationService:
    def __init__(self, venta_repository, inventario_repository, unit_of_work):
        # Inyección de dependencias (Interfaces de Repositorios y UoW)
        self.venta_repository = venta_repository
        self.inventario_repository = inventario_repository
        self.unit_of_work = unit_of_work

    def procesar_venta_mostrador(self, venta, inventario, cantidad):
        """Coordina el CU-01: Venta de mostrador con entrega inmediata."""
        # 1. Validación de reglas de dominio
        inventario.verificar_disponibilidad(cantidad)

        # 2. Iniciar la transacción
        self.unit_of_work.iniciar()

        try:
            # 3. Operaciones de dominio
            inventario.descontar_existencia(cantidad)
            venta.confirmar()

            # 4. Persistencia mediante repositorios
            self.venta_repository.guardar_venta(venta)
            self.inventario_repository.guardar_cambios(inventario)

            # 5. Confirmar transacción
            self.unit_of_work.confirmar()

            return "Venta confirmada"

        except Exception:
            # Si algo falla (ej. base de datos caída), se revierten los cambios
            self.unit_of_work.revertir()
            raise


class ValidacionApplicationService:
    def __init__(self, cotizacion_repository, unit_of_work):
        self.cotizacion_repository = cotizacion_repository
        self.unit_of_work = unit_of_work

    def validar_operacion_credito(self, id_cotizacion, credito):
        """Coordina el CU-03: Rechazo por cotización vencida o crédito no aprobado."""
        # 1. Recuperar la entidad mediante el repositorio
        cotizacion = self.cotizacion_repository.buscar_cotizacion_por_id(id_cotizacion)
        
        if not cotizacion:
            raise ValueError("Cotización no encontrada")

        # 2. Delegar validaciones al dominio
        cotizacion.validar_vigencia()
        credito.validar_autorizacion()

        # 3. Transaccionalidad
        self.unit_of_work.iniciar()
        try:
            # Confirmamos el flujo exitoso (y cualquier cambio de estado futuro)
            self.unit_of_work.confirmar()
            return "Operación autorizada"
            
        except Exception:
            self.unit_of_work.revertir()
            raise


class InventarioApplicationService:
    def __init__(self, inventario_repository, pedido_repository, unit_of_work):
        self.inventario_repository = inventario_repository
        self.pedido_repository = pedido_repository
        self.unit_of_work = unit_of_work

    def gestionar_faltante_inventario(self, inventario, cantidad, pedido):
        """Coordina el CU-04 en caso de inventario insuficiente."""
        self.unit_of_work.iniciar()
        
        try:
            try:
                # El dominio intenta verificar disponibilidad
                inventario.verificar_disponibilidad(cantidad)
                mensaje = "Inventario disponible"
                
            except ValueError:
                # Si falla, la lógica de negocio exige marcar el pedido como parcial
                pedido.marcar_parcial()
                self.pedido_repository.guardar_pedido(pedido)
                mensaje = "Pedido marcado como parcial"
                
            # Se confirman los cambios (ya sea que todo estuviera bien o que el pedido cambiara a parcial)
            self.unit_of_work.confirmar()
            return mensaje
            
        except Exception:
            self.unit_of_work.revertir()
            raise