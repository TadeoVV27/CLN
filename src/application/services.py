class VentaApplicationService:

    def __init__(self, venta_repository, inventario_repository, unit_of_work):
        self.venta_repository = venta_repository
        self.inventario_repository = inventario_repository
        self.unit_of_work = unit_of_work

    def procesar_venta_mostrador(self, venta, inventario, cantidad):
        inventario.verificar_disponibilidad(cantidad)

        self.unit_of_work.iniciar()

        try:
            inventario.descontar_existencia(cantidad)
            venta.confirmar()

            self.venta_repository.guardar_venta(venta)
            self.inventario_repository.guardar_cambios(inventario)

            self.unit_of_work.confirmar()

            return "Venta confirmada"

        except Exception:
            self.unit_of_work.revertir()
            raise


class ValidacionApplicationService:

    def validar_operacion_credito(self, cotizacion, credito):
        cotizacion.validar_vigencia()
        credito.validar_autorizacion()

        return "Operación autorizada"


class InventarioApplicationService:

    def gestionar_faltante_inventario(self, inventario, cantidad, pedido):
        try:
            inventario.verificar_disponibilidad(cantidad)
            return "Inventario disponible"

        except ValueError:
            pedido.marcar_parcial()
            return "Pedido marcado como parcial"