# FerreMax — Sistema de Gestión Comercial, Lógica de Negocio y Mostrador

**Producto Integrador de Aprendizaje (PIA) — Componentes de Lógica de Negocio**  
**Facultad de Ingeniería Mecánica y Eléctrica (FIME - UANL)**  
**Semestre:** Agosto - Diciembre 2026

---

## 🏗️ Arquitectura y Patrones Implementados

El proyecto materializa una solución basada en **Arquitectura Limpia (Clean Architecture)** y **Domain-Driven Design (DDD)**:

- **Domain Model:** Agregados (`Operacion`), Entidades (`Actor`, `Recurso`, `Cotizacion`, `Credito`, `Inventario`, `Venta`, `Pedido`) y Value Objects.
- **Specification Pattern:** Reglas de negocio atómicas y composiciones booleanas (`&`, `|`, `~`):
  - `PuedeProcesarseSpecification`: `ActorActivo & DetalleNoVacio & OperacionAutorizada`.
  - `BeneficioReferenciaSpecification`: `ActorPreferente (VIP) & TotalMinimo(>=1500 MXN) & ~PromocionActiva`.
- **State Machine Pattern:** Ciclo de vida estricto para operaciones:
  - `CREADO` $\rightarrow$ `APROBADO` $\rightarrow$ `SURTIDO` $\rightarrow$ `ENTREGADO`.
  - Cancelación controlada (`CREADO` $\rightarrow$ `CANCELADO`).
  - Protección contra saltos inválidos (`TransicionEstadoInvalidaException`).
- **Domain Events:** Emisión de eventos inmutables en cada transición (`OperacionAprobadaEvent`, `OperacionSurtidaEvent`, etc.).
- **Unit of Work & Repository Pattern:** Aislamiento transaccional y persistencia desacoplada.
- **API REST (FastAPI):** Documentación OpenAPI/Swagger activa en `/docs`.
- **Frontend de Mostrador (POS):** Interfaz industrial intuitiva para empleados sin tecnicismos.

---

## 📂 Estructura del Repositorio

```text
CLN/
├── docs/
│   ├── BRD.md                                 # BRD completo, 15 User Stories en Gherkin, BPMN y glosario
│   ├── architecture/
│   │   ├── ADR-001-Clean-Architecture-DDD.md   # Decisión técnica: DDD y Clean Architecture
│   │   ├── ADR-002-Specification-Pattern.md    # Decisión técnica: Specification Pattern
│   │   └── ADR-003-State-Machine-Events.md    # Decisión técnica: Máquina de estados y eventos
│   └── api/
│       └── openapi.json                       # Especificación OpenAPI exportada
├── data/                                      # Datasets oficiales del docente (actores, catalogo, ops, pruebas)
├── src/
│   ├── domain/                                # Entidades, Specifications, State Machine y Events
│   ├── application/                           # Casos de uso, servicios y evaluador oficial
│   ├── infrastructure/                        # Repositorios en memoria y persistencia
│   ├── api/                                   # Controladores y endpoints REST
│   └── main.py                                # Servidor FastAPI y montaje web
├── templates/
│   └── index.html                             # Interfaz web de mostrador/caja
├── tests/                                     # 31 pruebas unitarias y de integración
├── .github/workflows/
│   └── ci.yml                                 # Pipeline de integración continua (CI/CD)
├── docker-compose.yml                         # Contenerización Docker
├── .env.example                               # Variables de entorno
├── iniciar_ferremax.bat                       # Lanzador directo para Windows
└── README.md
```

---

## 🚀 Instrucciones de Instalación y Ejecución

### Requisitos Previos
- Python 3.12+ instalado.
- Git.

### 1. Clonar el Repositorio
```powershell
git clone https://github.com/TadeoVV27/CLN.git
cd CLN
```

### 2. Instalar Dependencias
```powershell
pip install -r requirements.txt
# O manualmente:
pip install fastapi uvicorn pytest pydantic
```

### 3. Iniciar la Aplicación

#### Opción Rápida (Windows):
Haz doble clic sobre:
```text
iniciar_ferremax.bat
```

#### Opción Manual:
```powershell
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Frontend de Mostrador:** [http://localhost:8000](http://localhost:8000)
- **Documentación Swagger UI (OpenAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Ejecución de Pruebas Automatizadas (Pytest)

El proyecto cuenta con **31 pruebas unitarias y de integración** que validan la lógica de negocio, Specifications, State Machine y el dataset de 120 casos del docente.

Para ejecutar todas las pruebas:
```powershell
python -m pytest tests/ -v
```

### Cobertura de las Pruebas:
- `tests/test_specifications.py`: Validación de reglas atómicas y compuestas (`&`, `|`, `~`).
- `tests/test_state_machine.py`: Flujo de vida, transiciones legales e ilegales y eventos de dominio.
- `tests/test_docente_casos.py`: Resolución automatizada de los 120 casos de prueba y 20 pruebas de transición.
- `tests/test_reglas_negocio.py`: 13 pruebas de reglas comerciales, persistencia y mocks.
- `tests/test_servicios.py`: Pruebas de integración de servicios de aplicación.

---

## 🐳 Ejecución con Docker Compose

```powershell
docker-compose up --build
```
Acceder a `http://localhost:8000`.

---

## 📋 Trazabilidad BRD $\rightarrow$ Reglas $\rightarrow$ Código $\rightarrow$ Pruebas

| ID Historia | Regla de Negocio | Componente en Código | Prueba Asociada |
|---|---|---|---|
| US-01 | Venta de Mostrador inmediata | `VentaApplicationService.procesar_venta_mostrador` | `test_procesar_venta_mostrador_exitosa` |
| US-02 | Verificación de inventario disponible | `Inventario.verificar_disponibilidad` | `test_error_inventario_insuficiente` |
| US-03 | Validación de cotización vigente | `Cotizacion.validar_vigencia` | `test_error_cotizacion_vencida` |
| US-04 | Autorización de crédito empresarial | `Credito.validar_autorizacion` | `test_error_credito_no_autorizado` |
| US-05 | Gestión de pedido parcial por faltante | `InventarioApplicationService.gestionar_faltante_inventario` | `test_pedido_parcial` |
| US-06, US-07 | Regla `puede_procesarse` | `PuedeProcesarseSpecification` | `test_puede_procesarse_specification` |
| US-08, US-09 | Regla `beneficio_referencia` (VIP) | `BeneficioReferenciaSpecification` | `test_beneficio_referencia_specification` |
| US-10 a US-14 | Ciclo de vida y transiciones | `OperacionStateMachine` | `test_state_machine.py` (7 tests) |
