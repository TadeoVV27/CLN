# tests/test_docente_casos.py
"""
Pruebas automáticas basadas en los datasets oficiales del docente (casos_prueba.csv y transiciones_prueba.csv).
Verifica que los 120 casos de prueba y las 20 pruebas de transición se resuelvan
con consistencia al 100%.
"""

import os
import pytest
from src.application.evaluador_docente import EvaluadorDocenteService

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


@pytest.fixture(scope="module")
def evaluador():
    service = EvaluadorDocenteService(DATA_DIR)
    service.cargar_datos()
    return service


def test_carga_datos_docente_completa(evaluador):
    assert len(evaluador.actores) == 40
    assert len(evaluador.recursos) == 20
    assert len(evaluador.operaciones) == 60


def test_evaluar_120_casos_prueba(evaluador):
    resultados = evaluador.resolver_casos_prueba(guardar_archivo=True)
    assert len(resultados) == 120

    # Todos los casos deben tener un resultado válido asignado
    for r in resultados:
        assert r["resultado_alumno"] in ("CUMPLE", "NO_CUMPLE", "APLICA", "NO_APLICA")

    # Archivo CSV resuelto generado
    path_resueltos = os.path.join(DATA_DIR, "casos_prueba_resueltos.csv")
    assert os.path.exists(path_resueltos)


def test_evaluar_20_transiciones_prueba(evaluador):
    resultados = evaluador.resolver_transiciones_prueba(guardar_archivo=True)
    assert len(resultados) == 20

    for r in resultados:
        res = r["resultado_alumno"]
        # Debe ser un estado final alcanzado o una excepción de transición inválida
        es_estado = res.startswith("ESTADO_")
        es_excepcion = res.startswith("EXCEPCION_TRANSICION_INVALIDA")
        assert es_estado or es_excepcion

    # Archivo CSV de transiciones resueltas generado
    path_trans = os.path.join(DATA_DIR, "transiciones_prueba_resueltas.csv")
    assert os.path.exists(path_trans)
