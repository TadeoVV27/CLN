@echo off
title FerreMax POS - Sistema de Mostrador y Caja (FastAPI)
color 0E
echo ======================================================================
echo           HERRAMIENTAS Y MATERIALES FERREMAX S.A. DE C.V.
echo            SISTEMA DE MOSTRADOR, CAJA Y CONTROL DE STOCK
echo ======================================================================
echo.
echo [1/2] Iniciando servidor FastAPI FerreMax...
start "" http://localhost:8000
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
pause
