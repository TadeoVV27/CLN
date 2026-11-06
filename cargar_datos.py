#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cargar_datos.py - Procesador Oficial de Datasets FerreMax (PIA)
Ejecuta la carga limpia de los CSVs originales, calcula totales con Decimal,
evalúa las Specifications (120 casos) y la State Machine (20 transiciones).
"""

import os
import sys

# Compatibilidad con consolas Windows (evitar errores de codificación)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Asegurar path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.application.evaluador_docente import EvaluadorDocenteService

def main():
    print("=" * 70)
    print(" [*] FERREMAX - PROCESADOR OFICIAL DE DATASETS CSV (PIA)")
    print("=" * 70)

    data_dir = os.path.join(BASE_DIR, "data")
    if not os.path.exists(data_dir):
        print(f"[!] Error: La carpeta '{data_dir}' no existe.")
        sys.exit(1)

    print(f"\n[1/4] Leyendo datasets originales desde: {data_dir}")
    evaluador = EvaluadorDocenteService(data_dir)
    
    # 1. Cargar datos
    evaluador.cargar_datos()
    print(f"      [OK] Actores cargados (actores.csv):       {len(evaluador.actores)} compradores")
    print(f"      [OK] Articulos en catalogo (catalogo.csv): {len(evaluador.recursos)} productos")
    print(f"      [OK] Operaciones (operaciones.csv):        {len(evaluador.operaciones)} ordenes")

    # Muestra de totales calculados con Decimal
    print("\n[2/4] Calculando totales con precision monetaria (Decimal)...")
    primeras_ops = list(evaluador.operaciones.values())[:3]
    for op in primeras_ops:
        nombre_cliente = op.actor.nombre if op.actor else "N/A"
        print(f"      - {op.operacion_id} ({op.referencia}) | Cliente: {nombre_cliente} | Total: ${op.calcular_total():,.2f} MXN")

    # 2. Evaluar 120 casos de prueba
    print("\n[3/4] Evaluando 120 Casos de Prueba con Specification Pattern...")
    print("      - Regla 1: 'puede_procesarse' (ActorActivo & DetalleNoVacio & Autorizado)")
    print("      - Regla 2: 'beneficio_referencia' (VIP & Total>=1500 & NOT Promocion)")
    casos = evaluador.resolver_casos_prueba(guardar_archivo=True)
    cumplen = sum(1 for c in casos if c["resultado_alumno"] in ("CUMPLE", "APLICA"))
    no_cumplen = len(casos) - cumplen
    print(f"      [OK] 120 casos evaluados exitosamente ({cumplen} positivos, {no_cumplen} negativos).")
    print("      [OK] Generado: data/casos_prueba_resueltos.csv")

    # 3. Evaluar 20 transiciones de prueba
    print("\n[4/4] Evaluando 20 Pruebas de Transicion con State Machine Pattern...")
    print("      - Validando transiciones legales: CREADO -> APROBADO -> SURTIDO -> ENTREGADO | CANCELADO")
    print("      - Capturando excepciones de dominio: TransicionEstadoInvalidaException")
    trans = evaluador.resolver_transiciones_prueba(guardar_archivo=True)
    estados_exito = sum(1 for t in trans if t["resultado_alumno"].startswith("ESTADO_"))
    excepciones = sum(1 for t in trans if t["resultado_alumno"].startswith("EXCEPCION_"))
    print(f"      [OK] 20 transiciones evaluadas ({estados_exito} transiciones legales, {excepciones} excepciones controladas).")
    print("      [OK] Generado: data/transiciones_prueba_resueltas.csv")

    print("\n" + "=" * 70)
    print(" [EXITO] PROCESAMIENTO COMPLETADO EXITOSAMENTE AL 100%")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
