@echo off
title FerreMax - Limpiar Resultados Generados
color 0C
echo ======================================================================
echo           HERRAMIENTAS Y MATERIALES FERREMAX S.A. DE C.V.
echo            LIMPIEZA DE ARCHIVOS GENERADOS (RESET DE DATOS)
echo ======================================================================
echo.
if exist "data\casos_prueba_resueltos.csv" (
    del /f /q "data\casos_prueba_resueltos.csv"
    echo [OK] Eliminado: data\casos_prueba_resueltos.csv
) else (
    echo [INFO] data\casos_prueba_resueltos.csv no existia.
)

if exist "data\transiciones_prueba_resueltas.csv" (
    del /f /q "data\transiciones_prueba_resueltas.csv"
    echo [OK] Eliminado: data\transiciones_prueba_resueltas.csv
) else (
    echo [INFO] data\transiciones_prueba_resueltas.csv no existia.
)

echo.
echo ======================================================================
echo  [LISTO] Datos resueltos eliminados. Los archivos originales CSV quedan intactos.
echo  Puedes correr 'procesar_csvs.bat' o 'python cargar_datos.py' para regenerarlos.
echo ======================================================================
echo.
pause
