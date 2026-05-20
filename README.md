# Sistema de Control y Trazabilidad en Tiempo Real para la Gestión Eficiente de Inventarios

API REST académica para gestionar inventarios, preparada para crecer por fases hacia usuarios, roles, productos, movimientos, trazabilidad, alertas y reportes.

## Integrantes

- Pablo Garcés Hoyos
- Jilmar Said Veloza Páez
- Sara Ruiz

## Stack tecnológico

- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic y pydantic-settings
- SQLite para desarrollo local y pruebas
- Configuración mediante `DATABASE_URL` para migración futura a PostgreSQL
- JWT con `python-jose`
- Hash de contraseñas con `passlib[bcrypt]`
- pytest, pytest-cov y httpx
- Docker y Docker Compose
- GitHub Actions

## Decisiones técnicas

Python 3.11 ofrece una base moderna y estable para backend. FastAPI permite construir una API tipada, rápida y documentada automáticamente en Swagger. SQLAlchemy mantiene la capa de persistencia desacoplada de la base de datos concreta. pytest y pytest-cov facilitan pruebas automatizadas y medición de cobertura desde las primeras fases. Docker estandariza la ejecución local y GitHub Actions deja listo el control de calidad continuo del proyecto.

## Estructura de carpetas

```text
inventory-app/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- src/
|   |-- main.py
|   |-- core/
|   |   |-- config.py
|   |   `-- database.py
|   |-- models/
|   |   |-- product.py
|   |   `-- user.py
|   |-- schemas/
|   |   |-- auth.py
|   |   |-- product.py
|   |   `-- user.py
|   |-- services/
|   |   |-- product_service.py
|   |   `-- user_service.py
|   |-- repositories/
|   |   |-- product_repository.py
|   |   `-- user_repository.py
|   |-- api/
|   |   `-- routes/
|   |       |-- auth.py
|   |       |-- health.py
|   |       |-- products.py
|   |       `-- users.py
|   |-- security/
|   |   |-- dependencies.py
|   |   |-- jwt.py
|   |   `-- password.py
|   `-- exceptions/
|       |-- product_exceptions.py
|       `-- user_exceptions.py
|-- tests/
|   `-- unit/
|       |-- conftest.py
|       |-- test_auth.py
|       |-- test_health.py
|       |-- test_products.py
|       |-- test_rbac.py
|       `-- test_users.py
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- pytest.ini
`-- README.md
```

## Configuración local

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

La configuración se toma desde variables de entorno. El archivo `.env.example` contiene valores de desarrollo:

```text
DATABASE_URL=sqlite:///./inventory.db
JWT_SECRET_KEY=change-this-secret-key
```

Para desarrollo real se recomienda crear un archivo `.env` local basado en `.env.example`. El archivo `.env` está ignorado por Git.

## Ejecutar la API

```bash
uvicorn src.main:app --reload
```

Endpoint raíz:

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

## Fase 2 — Usuarios, roles y autenticación

Esta fase implementa usuarios, roles, autenticación JWT, protección de endpoints y eliminación lógica de usuarios. No incluye productos, movimientos, inventario, alertas ni reportes.

Roles disponibles:

- `ADMINISTRADOR`
- `OPERADOR`
- `AUDITOR`

Estados disponibles:

- `ACTIVO`
- `INACTIVO`

Endpoints creados:

- `POST /api/usuarios`: crea un usuario. En esta fase es público para facilitar pruebas académicas.
- `POST /api/auth/login`: autentica credenciales y retorna un JWT.
- `GET /api/usuarios/me`: retorna el usuario autenticado.
- `PUT /api/usuarios/{usuario_id}/rol`: asigna rol, requiere `ADMINISTRADOR`.
- `DELETE /api/usuarios/{usuario_id}`: eliminación lógica, requiere `ADMINISTRADOR`.

Crear usuario:

```http
POST /api/usuarios
Content-Type: application/json
```

```json
{
  "nombre": "Pablo Garcés",
  "email": "pablo@eam.edu.co",
  "password": "Segura#123",
  "rol": "OPERADOR"
}
```

Login:

```http
POST /api/auth/login
Content-Type: application/json
```

```json
{
  "email": "pablo@eam.edu.co",
  "password": "Segura#123"
}
```

Usar token en Swagger:

1. Ejecutar login y copiar `access_token`.
2. Abrir `http://localhost:8000/docs`.
3. Presionar `Authorize`.
4. Enviar el token como Bearer token.

Header HTTP equivalente:

```text
Authorization: Bearer <token>
```

Pruebas implementadas en Fase 2:

- PU-001: creación exitosa de usuario.
- PU-002: rechazo de usuario con email duplicado.
- PU-003: asignación de rol a usuario.
- PU-013: validación de token JWT inválido en endpoint protegido.
- PU-014: control de acceso basado en roles RBAC.
- PU-017: eliminación lógica de usuario.

## Fase 3 — Gestión de productos

Esta fase implementa el registro, consulta, listado y actualización de datos generales de productos. No implementa movimientos de inventario, entradas, salidas, historial, alertas ni reportes.

Endpoints creados:

- `POST /api/productos`: crea producto, requiere `ADMINISTRADOR` u `OPERADOR`.
- `GET /api/productos`: lista productos, requiere usuario autenticado.
- `GET /api/productos/{producto_id}`: consulta producto por ID, requiere usuario autenticado.
- `PUT /api/productos/{producto_id}`: actualiza datos generales, requiere `ADMINISTRADOR`.

Reglas de negocio:

- `sku` es único y se normaliza a mayúsculas.
- `sku` no se puede modificar después de crear el producto.
- `stock_inicial` se guarda como `stock_actual` al crear el producto.
- `stock_actual` no se altera al actualizar datos generales.
- `stock_inicial` y `stock_minimo` no pueden ser negativos.
- `nombre`, `sku`, `categoria` y `unidad` no pueden estar vacíos.
- El estado inicial del producto es `ACTIVO`.

Crear producto:

```http
POST /api/productos
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "nombre": "Resma de Papel",
  "sku": "PAP-001",
  "categoria": "INSUMOS",
  "stock_inicial": 50,
  "stock_minimo": 10,
  "unidad": "unidades"
}
```

Actualizar producto:

```http
PUT /api/productos/1
Authorization: Bearer <token_admin>
Content-Type: application/json
```

```json
{
  "nombre": "Resma de Papel A4",
  "categoria": "PAPELERÍA",
  "stock_minimo": 15,
  "unidad": "unidades"
}
```

Pruebas implementadas en Fase 3:

- PU-004: registro de producto con datos válidos.
- PU-005: rechazo de producto con SKU duplicado.
- PU-016: modificación de datos de producto existente.
- PU-018: validación de campos obligatorios en registro de producto.

También se agregaron pruebas de protección para listado con token, consulta por ID, rechazo de acceso sin token, rechazo de actualización por `OPERADOR` y rechazo de modificación de `sku`.

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

En estas fases se usa SQLite. PostgreSQL puede agregarse después mediante un servicio adicional en `docker-compose.yml` y cambiando `DATABASE_URL`.

## Pipeline CI

El workflow `Inventory API CI` se ejecuta en `push` a `main`, `push` a `develop` y en `pull_request` hacia `main`. El job `build-and-test` instala Python 3.11, instala dependencias, ejecuta pruebas con cobertura y sube `coverage.xml` como artifact.

En fases posteriores se agregarán pasos de construcción Docker completa, publicación de imagen y despliegue, siguiendo el documento del pipeline del proyecto.

## Estado actual

Fase 1 completada:

- Estructura base profesional creada.
- FastAPI configurado.
- Endpoint raíz disponible.
- Health check disponible en `/api/health`.
- Configuración central por variables de entorno.
- SQLAlchemy preparado para SQLite y PostgreSQL.
- Dockerfile y Docker Compose listos.
- GitHub Actions configurado para pruebas y cobertura.

Fase 2 completada:

- Modelo de usuario creado.
- Registro de usuarios disponible.
- Login con JWT disponible.
- Protección de endpoints con Bearer token.
- Control de acceso por rol `ADMINISTRADOR`.
- Eliminación lógica de usuarios mediante estado `INACTIVO`.
- Pruebas PU-001, PU-002, PU-003, PU-013, PU-014 y PU-017 implementadas.

Fase 3 completada:

- Modelo de producto creado.
- Registro de productos disponible.
- Listado y consulta de productos protegidos por JWT.
- Actualización de datos generales restringida a `ADMINISTRADOR`.
- Validación de SKU único y campos obligatorios.
- Pruebas PU-004, PU-005, PU-016 y PU-018 implementadas.

## Próximas fases

- Fase 4: movimientos, inventario, historial y alertas.
- Fase 5: reportes.
- Fase 6: implementación completa de las 18 pruebas unitarias.
- Fase 7: Docker build completo y despliegue.
