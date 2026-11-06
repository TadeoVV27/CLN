# src/application/evaluador_docente.py
"""
Servicio de Aplicación: Evaluador Oficial de Casos y Transiciones FerreMax.
Lee los datasets oficiales del docente (actores, catalogo, operaciones, detalle),
ejecuta las Specifications y la State Machine, y resuelve los 120 casos de prueba
y 20 pruebas de transición.
"""

import os
import csv
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from src.domain.models import Actor, Recurso, DetalleOperacion, Operacion
from src.domain.specifications import (
    crear_especificacion_puede_procesarse,
    crear_especificacion_beneficio_referencia,
)
from src.domain.state_machine import TransicionEstadoInvalidaException


class EvaluadorDocenteService:
    """Carga y evalúa los datos y pruebas del paquete docente."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.actores: Dict[str, Actor] = {}
        self.recursos: Dict[str, Recurso] = {}
        self.operaciones: Dict[str, Operacion] = {}
        self.spec_puede_procesarse = crear_especificacion_puede_procesarse()
        self.spec_beneficio = crear_especificacion_beneficio_referencia(Decimal("1500.00"))

    def cargar_datos(self):
        """Carga actores, catálogo, operaciones y detalle desde los CSVs."""
        # 1. Actores
        path_actores = os.path.join(self.data_dir, "actores.csv")
        with open(path_actores, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                actor = Actor(
                    actor_id=row["actor_id"],
                    nombre=row["nombre"],
                    es_preferente=bool(int(row["es_preferente"])),
                    activo=bool(int(row["activo"])),
                    ciudad=row.get("ciudad", ""),
                )
                self.actores[actor.actor_id] = actor

        # 2. Catálogo (Recursos)
        path_cat = os.path.join(self.data_dir, "catalogo.csv")
        with open(path_cat, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                recurso = Recurso(
                    recurso_id=row["recurso_id"],
                    descripcion=row["descripcion"],
                    precio_mxn=Decimal(row["precio_mxn"]),
                    capacidad_o_stock=int(row["capacidad_o_stock"]),
                    habilitado=bool(int(row["habilitado"])),
                )
                self.recursos[recurso.recurso_id] = recurso

        # 3. Operaciones
        path_ops = os.path.join(self.data_dir, "operaciones.csv")
        with open(path_ops, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                actor_id = row["actor_id"]
                operacion = Operacion(
                    operacion_id=row["operacion_id"],
                    actor_id=actor_id,
                    estado_inicial=row["estado_inicial"],
                    fecha_solicitud=row["fecha_solicitud"],
                    promocion_activa=bool(int(row["promocion_activa"])),
                    autorizado=bool(int(row["autorizado"])),
                    referencia=row["referencia"],
                    actor=self.actores.get(actor_id),
                    lineas=[],
                )
                self.operaciones[operacion.operacion_id] = operacion

        # 4. Detalle Operaciones
        path_det = os.path.join(self.data_dir, "detalle_operaciones.csv")
        with open(path_det, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                op_id = row["operacion_id"]
                rec_id = row["recurso_id"]
                cantidad = int(row["cantidad"])
                recurso = self.recursos.get(rec_id)
                detalle = DetalleOperacion(
                    operacion_id=op_id,
                    recurso_id=rec_id,
                    cantidad=cantidad,
                    recurso=recurso,
                )
                if op_id in self.operaciones:
                    self.operaciones[op_id].lineas.append(detalle)

    def resolver_casos_prueba(self, guardar_archivo: bool = True) -> List[Dict]:
        """
        Ejecuta los 120 casos de prueba de casos_prueba.csv.
        Evalúa validar_operacion (PuedeProcesarse) y evaluar_beneficio (VIP & >=1500 & NOT promo).
        """
        if not self.operaciones:
            self.cargar_datos()

        path_casos = os.path.join(self.data_dir, "casos_prueba.csv")
        resultados = []

        with open(path_casos, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                caso_id = row["caso_id"]
                op_id = row["operacion_id"]
                tipo = row["tipo_prueba"]
                op = self.operaciones.get(op_id)

                if not op:
                    res_val = "ERROR_OP_NO_EXISTE"
                elif tipo == "validar_operacion":
                    cumple = self.spec_puede_procesarse.is_satisfied_by(op)
                    res_val = "CUMPLE" if cumple else "NO_CUMPLE"
                elif tipo == "evaluar_beneficio":
                    cumple = self.spec_beneficio.is_satisfied_by(op)
                    res_val = "APLICA" if cumple else "NO_APLICA"
                else:
                    res_val = "TIPO_DESCONOCIDO"

                nueva_fila = dict(row)
                nueva_fila["resultado_alumno"] = res_val
                resultados.append(nueva_fila)

        if guardar_archivo:
            path_salida = os.path.join(self.data_dir, "casos_prueba_resueltos.csv")
            fieldnames = ["caso_id", "operacion_id", "tipo_prueba", "regla_a_verificar", "resultado_alumno", "instrucciones"]
            with open(path_salida, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(resultados)

        return resultados

    def resolver_transiciones_prueba(self, guardar_archivo: bool = True) -> List[Dict]:
        """
        Ejecuta las 20 pruebas de transición de transiciones_prueba.csv.
        Registra el estado final alcanzado o la excepción atrapada.
        """
        if not self.operaciones:
            self.cargar_datos()

        path_trans = os.path.join(self.data_dir, "transiciones_prueba.csv")
        resultados = []

        with open(path_trans, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                caso_id = row["caso_id"]
                op_id = row["operacion_id"]
                accion = row["accion_sugerida"]
                op = self.operaciones.get(op_id)

                if not op:
                    res_val = "ERROR_OP_NO_EXISTE"
                else:
                    # Crear una instancia limpia de la operación para no contaminar
                    op_copia = Operacion(
                        operacion_id=op.operacion_id,
                        actor_id=op.actor_id,
                        estado_inicial="CREADO",
                        promocion_activa=op.promocion_activa,
                        autorizado=op.autorizado,
                        actor=op.actor,
                        lineas=list(op.lineas),
                    )

                    try:
                        if accion == "aprobar":
                            op_copia.aprobar()
                            res_val = f"ESTADO_{op_copia.estado}"
                        elif accion == "completar":
                            op_copia.completar()
                            res_val = f"ESTADO_{op_copia.estado}"
                        elif accion == "cancelar":
                            op_copia.cancelar()
                            res_val = f"ESTADO_{op_copia.estado}"
                        elif accion == "repetir_aprobacion":
                            op_copia.aprobar()
                            # Intento de repetir aprobación (debe fallar)
                            op_copia.aprobar()
                            res_val = f"ESTADO_{op_copia.estado}"
                        elif accion == "saltar_estado":
                            # Intento ilegal: pasar de CREADO directo a ENTREGADO
                            op_copia.entregar()
                            res_val = f"ESTADO_{op_copia.estado}"
                        else:
                            res_val = f"ACCION_DESCONOCIDA_{accion}"
                    except TransicionEstadoInvalidaException as e:
                        res_val = f"EXCEPCION_TRANSICION_INVALIDA({e.estado_actual}->{e.accion})"

                nueva_fila = dict(row)
                nueva_fila["resultado_alumno"] = res_val
                resultados.append(nueva_fila)

        if guardar_archivo:
            path_salida = os.path.join(self.data_dir, "transiciones_prueba_resueltas.csv")
            fieldnames = ["caso_id", "operacion_id", "accion_sugerida", "estado_inicial", "resultado_alumno", "instrucciones"]
            with open(path_salida, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(resultados)

        return resultados
