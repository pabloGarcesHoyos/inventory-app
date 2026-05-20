# Sistema de Control y Trazabilidad en Tiempo Real para la Gestion Eficiente de Inventarios

API REST academica para gestionar inventarios, preparada para crecer por fases hacia usuarios, roles, productos, movimientos, trazabilidad, alertas y reportes.

## Integrantes

- Pablo Garces Hoyos
- Jilmar Said Veloza Paez
- Sara Ruiz

## Stack tecnologico

- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic y pydantic-settings
- SQLite para desarrollo local y pruebas
- Configuracion mediante `DATABASE_URL` para migracion futura a PostgreSQL
- JWT preparado con `python-jose`
- Hash de contrasenas preparado con `passlib[bcrypt]`
- pytest, pytest-cov y httpx
- Docker y Docker Compose
- GitHub Actions

## Decisiones tecnicas

Python 3.11 ofrece una base moderna y estable para backend. FastAPI permite construir una API tipada, rapida y documentada automaticamente en Swagger. SQLAlchemy mantiene la capa de persistencia desacoplada de la base de datos concreta. pytest y pytest-cov facilitan pruebas automatizadas y medicion de cobertura desde la primera fase. Docker estandariza la ejecucion local y GitHub Actions deja listo el control de calidad continuo del proyecto.

## Estructura de carpetas

```text
inventory-app/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── api/
│   │   └── routes/
│   │       └── health.py
│   ├── security/
│   └── exceptions/
├── tests/
│   └── unit/
│       └── test_health.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

## Configuracion local

Crear entorno virtual en Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Crear entorno virtual en macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

La configuracion se toma desde variables de entorno. El archivo `.env.example` contiene valores de desarrollo:

```text
DATABASE_URL=sqlite:///./inventory.db
JWT_SECRET_KEY=change-this-secret-key
```

Para desarrollo real se recomienda crear un archivo `.env` local basado en `.env.example`. El archivo `.env` esta ignorado por Git.

## Ejecutar la API

```bash
uvicorn src.main:app --reload
```

Endpoint raiz:

```text
http://localhost:8000/
```

Health check:

```text
http://localhost:8000/api/health
```

Swagger:

```text
http://localhost:8000/docs
```

## Pruebas

Ejecutar pruebas:

```bash
pytest tests/unit/ -v
```

Ejecutar pruebas con cobertura:

```bash
pytest tests/unit/ --cov=src --cov-report=term-missing -v
```

## Docker

Construir imagen:

```bash
docker build -t inventory-api .
```

Ejecutar contenedor:

```bash
docker run -p 8000:8000 inventory-api
```

Ejecutar con Docker Compose:

```bash
docker compose up --build
```

En esta fase se usa SQLite. PostgreSQL puede agregarse en una fase posterior mediante un servicio adicional en `docker-compose.yml` y cambiando `DATABASE_URL`.

## Pipeline CI

El workflow `Inventory API CI` se ejecuta en `push` a `main`, `push` a `develop` y en `pull_request` hacia `main`. El job `build-and-test` instala Python 3.11, instala dependencias, ejecuta pruebas con cobertura y sube `coverage.xml` como artifact.

En fases posteriores se agregaran pasos de construccion Docker completa, publicacion de imagen y despliegue, siguiendo el documento del pipeline del proyecto.

## Estado actual

Fase 1 completada:

- Estructura base profesional creada.
- FastAPI configurado.
- Endpoint raiz disponible.
- Health check disponible en `/api/health`.
- Configuracion central por variables de entorno.
- SQLAlchemy preparado para SQLite y PostgreSQL.
- Prueba minima funcionando.
- Dockerfile y Docker Compose listos.
- GitHub Actions configurado para pruebas y cobertura.

## Proximas fases

- Fase 2: usuarios, roles y autenticacion.
- Fase 3: productos.
- Fase 4: movimientos, inventario, historial y alertas.
- Fase 5: reportes.
- Fase 6: implementacion completa de las 18 pruebas unitarias.
- Fase 7: Docker build completo y despliegue.
