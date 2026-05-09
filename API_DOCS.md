# Mercado Plug — Documentación Técnica de Integración

**Versión:** 0.1.0  
**Base URL (producción):** `https://mercado-plug-api.onrender.com`  
**Base URL (local):** `http://localhost:8000`  
**Prefijo de todos los endpoints:** `/api/v1`  
**Documentación interactiva (Swagger):** `{BASE_URL}/api/v1/docs`  
**Documentación alternativa (ReDoc):** `{BASE_URL}/api/v1/redoc`

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Autenticación](#2-autenticación)
3. [Formato de Peticiones y Respuestas](#3-formato-de-peticiones-y-respuestas)
4. [Códigos de Estado HTTP](#4-códigos-de-estado-http)
5. [Manejo de Errores](#5-manejo-de-errores)
6. [Módulo de Usuarios](#6-módulo-de-usuarios)
   - [Crear usuario](#61-crear-usuario)
   - [Listar usuarios](#62-listar-usuarios)
   - [Obtener usuario por ID](#63-obtener-usuario-por-id)
   - [Actualizar usuario](#64-actualizar-usuario)
   - [Eliminar usuario](#65-eliminar-usuario)
7. [Modelos de Datos](#7-modelos-de-datos)
8. [Enumeraciones](#8-enumeraciones)
9. [Paginación](#9-paginación)
10. [Ejemplos de Integración](#10-ejemplos-de-integración)
11. [Variables de Entorno](#11-variables-de-entorno)
12. [Despliegue en Render](#12-despliegue-en-render)

---

## 1. Introducción

**Mercado Plug** es un marketplace en línea. Esta API REST provee los servicios de backend para que clientes web, móviles o terceros puedan interactuar con la plataforma de forma programática.

- Todas las peticiones y respuestas usan **JSON**.
- Los endpoints siguen convenciones **RESTful**.
- La API está construida con **FastAPI** (Python) y desplegada en **Render**.
- La base de datos es **PostgreSQL** alojada en Render.

---

## 2. Autenticación

> **Estado actual:** La API está en fase inicial. Los endpoints son públicos. La autenticación mediante JWT se habilitará en próximas versiones.

Cuando la autenticación esté activa, se usará el esquema **Bearer Token**:

```
Authorization: Bearer <tu_access_token>
```

Para obtener un token se deberá consumir el endpoint de login (próximamente):

```http
POST /api/v1/auth/login
```

---

## 3. Formato de Peticiones y Respuestas

### Cabeceras requeridas

| Cabecera       | Valor              | Requerida en          |
|----------------|--------------------|-----------------------|
| `Content-Type` | `application/json` | POST, PATCH, PUT      |
| `Accept`       | `application/json` | Todas (recomendado)   |

### Formato de fecha

Todas las fechas se devuelven en formato **ISO 8601** con zona horaria UTC:

```
2026-05-08T18:00:00Z
```

---

## 4. Códigos de Estado HTTP

| Código | Significado                                          |
|--------|------------------------------------------------------|
| `200`  | OK — Petición exitosa                                |
| `201`  | Created — Recurso creado exitosamente                |
| `204`  | No Content — Eliminación exitosa                     |
| `400`  | Bad Request — Datos inválidos o regla de negocio     |
| `404`  | Not Found — El recurso no existe                     |
| `422`  | Unprocessable Entity — Error de validación de campos |
| `500`  | Internal Server Error — Error inesperado del servidor|

---

## 5. Manejo de Errores

Todos los errores siguen el siguiente formato de respuesta:

```json
{
  "detail": "Descripción del error"
}
```

### Error de validación (422)

Cuando algún campo no cumple las reglas de validación, la respuesta incluye el detalle exacto por campo:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "correo-invalido"
    }
  ]
}
```

---

## 6. Módulo de Usuarios

### 6.1 Crear usuario

Registra un nuevo usuario en la plataforma.

```
POST /api/v1/users/
```

#### Body (JSON)

| Campo    | Tipo     | Requerido | Descripción                                  |
|----------|----------|-----------|----------------------------------------------|
| `name`   | `string` | Sí        | Nombre completo del usuario                  |
| `email`  | `string` | Sí        | Correo electrónico único (formato válido)    |
| `password` | `string` | Sí      | Contraseña en texto plano (mínimo 8 caracteres). Se almacena hasheada con bcrypt. |
| `phone`  | `string` | No        | Número de teléfono                           |
| `role`   | `string` | No        | `buyer` (defecto), `seller` o `admin`        |

#### Ejemplo de petición

```bash
curl -X POST "https://mercado-plug-api.onrender.com/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ana García",
    "email": "ana@example.com",
    "password": "MiPassword123",
    "phone": "+502 5555-1234",
    "role": "seller"
  }'
```

#### Respuesta exitosa `201 Created`

```json
{
  "id": 1,
  "name": "Ana García",
  "email": "ana@example.com",
  "phone": "+502 5555-1234",
  "role": "seller",
  "status": "active",
  "created_at": "2026-05-08T18:00:00Z"
}
```

#### Errores posibles

| Código | Condición                                  |
|--------|--------------------------------------------|
| `400`  | El correo ya está registrado               |
| `422`  | Formato de email inválido, contraseña < 8 caracteres, o campos faltantes |

---

### 6.2 Listar usuarios

Devuelve una lista paginada de todos los usuarios.

```
GET /api/v1/users/
```

#### Query Parameters

| Parámetro | Tipo  | Defecto | Descripción                        |
|-----------|-------|---------|------------------------------------|
| `skip`    | `int` | `0`     | Número de registros a omitir       |
| `limit`   | `int` | `20`    | Máximo de registros (máx. `100`)   |

#### Ejemplo de petición

```bash
curl "https://mercado-plug-api.onrender.com/api/v1/users/?skip=0&limit=10"
```

#### Respuesta exitosa `200 OK`

```json
{
  "total": 45,
  "users": [
    {
      "id": 1,
      "name": "Ana García",
      "email": "ana@example.com",
      "phone": "+502 5555-1234",
      "role": "seller",
      "status": "active",
      "created_at": "2026-05-08T18:00:00Z"
    },
    {
      "id": 2,
      "name": "Carlos López",
      "email": "carlos@example.com",
      "phone": null,
      "role": "buyer",
      "status": "active",
      "created_at": "2026-05-08T19:00:00Z"
    }
  ]
}
```

---

### 6.3 Obtener usuario por ID

Devuelve los datos de un usuario específico.

```
GET /api/v1/users/{user_id}
```

#### Path Parameters

| Parámetro | Tipo  | Descripción          |
|-----------|-------|----------------------|
| `user_id` | `int` | ID único del usuario |

#### Ejemplo de petición

```bash
curl "https://mercado-plug-api.onrender.com/api/v1/users/1"
```

#### Respuesta exitosa `200 OK`

```json
{
  "id": 1,
  "name": "Ana García",
  "email": "ana@example.com",
  "phone": "+502 5555-1234",
  "role": "seller",
  "status": "active",
  "created_at": "2026-05-08T18:00:00Z"
}
```

#### Errores posibles

| Código | Condición                  |
|--------|----------------------------|
| `404`  | El usuario no existe       |

---

### 6.4 Actualizar usuario

Actualiza parcialmente los datos de un usuario. Solo se modifican los campos enviados.

```
PATCH /api/v1/users/{user_id}
```

#### Path Parameters

| Parámetro | Tipo  | Descripción          |
|-----------|-------|----------------------|
| `user_id` | `int` | ID único del usuario |

#### Body (JSON) — todos los campos son opcionales

| Campo    | Tipo     | Descripción                                            |
|----------|----------|--------------------------------------------------------|
| `name`   | `string` | Nuevo nombre completo                                  |
| `phone`  | `string` | Nuevo número de teléfono                               |
| `role`   | `string` | Nuevo rol: `buyer`, `seller` o `admin`                 |
| `status` | `string` | Nuevo estado: `active`, `inactive` o `banned`          |

#### Ejemplo de petición

```bash
curl -X PATCH "https://mercado-plug-api.onrender.com/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "inactive"
  }'
```

#### Respuesta exitosa `200 OK`

```json
{
  "id": 1,
  "name": "Ana García",
  "email": "ana@example.com",
  "phone": "+502 5555-1234",
  "role": "seller",
  "status": "inactive",
  "created_at": "2026-05-08T18:00:00Z"
}
```

#### Errores posibles

| Código | Condición                  |
|--------|----------------------------|
| `404`  | El usuario no existe       |
| `422`  | Valor inválido en algún campo |

---

### 6.5 Eliminar usuario

Elimina permanentemente un usuario del sistema.

```
DELETE /api/v1/users/{user_id}
```

#### Path Parameters

| Parámetro | Tipo  | Descripción          |
|-----------|-------|----------------------|
| `user_id` | `int` | ID único del usuario |

#### Ejemplo de petición

```bash
curl -X DELETE "https://mercado-plug-api.onrender.com/api/v1/users/1"
```

#### Respuesta exitosa `204 No Content`

_Sin cuerpo de respuesta._

#### Errores posibles

| Código | Condición                  |
|--------|----------------------------|
| `404`  | El usuario no existe       |

---

## 7. Modelos de Datos

### Usuario (`User`)

```json
{
  "id": 1,
  "name": "string",
  "email": "user@example.com",
  "phone": "string | null",
  "role": "buyer | seller | admin",
  "status": "active | inactive | banned",
  "created_at": "2026-05-08T18:00:00Z"
}
```

> **Nota:** El campo `password_hash` nunca es retornado por la API.

---

## 8. Enumeraciones

### `role` — Rol del usuario

| Valor    | Descripción                                              |
|----------|----------------------------------------------------------|
| `buyer`  | Comprador. Puede navegar y comprar productos. (defecto)  |
| `seller` | Vendedor. Puede publicar y gestionar productos.          |
| `admin`  | Administrador. Acceso total a la plataforma.             |

### `status` — Estado del usuario

| Valor      | Descripción                                           |
|------------|-------------------------------------------------------|
| `active`   | Cuenta activa. Acceso normal. (defecto al crear)      |
| `inactive` | Cuenta desactivada temporalmente.                     |
| `banned`   | Cuenta suspendida por violación de políticas.         |

---

## 9. Paginación

El endpoint de listado soporta paginación por offset:

| Parámetro | Descripción                          |
|-----------|--------------------------------------|
| `skip`    | Desde qué registro iniciar (offset)  |
| `limit`   | Cuántos registros devolver (máx 100) |

**Ejemplo — Página 2 con 10 registros por página:**

```
GET /api/v1/users/?skip=10&limit=10
```

La respuesta siempre incluye el campo `total` con el conteo global, lo que permite calcular el número total de páginas:

```
total_paginas = ceil(total / limit)
```

---

## 10. Ejemplos de Integración

### JavaScript / Fetch

```javascript
// Crear un usuario
const response = await fetch('https://mercado-plug-api.onrender.com/api/v1/users/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Ana García',
    email: 'ana@example.com',
    password: 'MiPassword123',
    role: 'buyer'
  })
});
const user = await response.json();
console.log(user);

// Obtener usuario por ID
const res = await fetch('https://mercado-plug-api.onrender.com/api/v1/users/1');
const data = await res.json();
```

### Python / requests

```python
import requests

BASE_URL = "https://mercado-plug-api.onrender.com/api/v1"

# Crear usuario
payload = {
    "name": "Ana García",
    "email": "ana@example.com",
    "password": "MiPassword123",
    "role": "seller"
}
response = requests.post(f"{BASE_URL}/users/", json=payload)
user = response.json()

# Listar usuarios
users = requests.get(f"{BASE_URL}/users/", params={"skip": 0, "limit": 20}).json()

# Actualizar usuario
updated = requests.patch(f"{BASE_URL}/users/1", json={"status": "inactive"}).json()

# Eliminar usuario
requests.delete(f"{BASE_URL}/users/1")
```

### Dart / Flutter (http)

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

const baseUrl = 'https://mercado-plug-api.onrender.com/api/v1';

// Crear usuario
Future<Map<String, dynamic>> createUser() async {
  final response = await http.post(
    Uri.parse('$baseUrl/users/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'name': 'Ana García',
      'email': 'ana@example.com',
      'password': 'MiPassword123',
      'role': 'buyer',
    }),
  );
  return jsonDecode(response.body);
}

// Obtener usuario
Future<Map<String, dynamic>> getUser(int id) async {
  final response = await http.get(Uri.parse('$baseUrl/users/$id'));
  return jsonDecode(response.body);
}
```

---

## 11. Variables de Entorno

El proyecto requiere las siguientes variables de entorno. Se deben definir en un archivo `.env` en la raíz del proyecto (no incluido en el repositorio):

| Variable        | Descripción                                   | Ejemplo                        |
|-----------------|-----------------------------------------------|--------------------------------|
| `DATABASE_URL`  | URL de conexión a PostgreSQL                  | `postgresql://user:pass@host/db` |
| `SECRET_KEY`    | Clave secreta para JWT (mínimo 32 caracteres) | `una-clave-muy-secreta-aqui`   |

Copiar `.env.example` como punto de partida:

```bash
cp .env.example .env
```

---

## 12. Despliegue en Render

El proyecto incluye `render.yaml` para despliegue automático.

### Pasos para desplegar:

1. Crear una cuenta en [render.com](https://render.com)
2. Crear un nuevo **Web Service** apuntando al repositorio de GitHub
3. Render detectará automáticamente el `render.yaml`
4. Agregar las variables de entorno en el panel de Render:
   - `DATABASE_URL`
   - `SECRET_KEY`
5. El build command es: `pip install -r requirements.txt`
6. El start command es: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Estructura del proyecto

```
backend/
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── database.py          # Configuración SQLAlchemy
│   ├── core/
│   │   ├── config.py        # Variables de entorno (pydantic-settings)
│   │   └── security.py      # Hash y verificación de contraseñas
│   ├── models/
│   │   └── user.py          # Modelo ORM de usuarios
│   ├── schemas/
│   │   └── user.py          # Schemas Pydantic (validación)
│   └── routes/
│       └── users.py         # Endpoints CRUD de usuarios
├── .env.example             # Plantilla de variables de entorno
├── .gitignore
├── render.yaml              # Configuración de despliegue en Render
└── requirements.txt         # Dependencias Python
```

---

*Documentación generada para Mercado Plug API v0.1.0 — Mayo 2026*
