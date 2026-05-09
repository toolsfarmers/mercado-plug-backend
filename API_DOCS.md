# Mercado Plug — Documentación Técnica de Integración

**Versión:** 0.3.0  
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
7. [Módulo de Tiendas](#7-módulo-de-tiendas)
   - [Crear tienda](#71-crear-tienda)
   - [Listar tiendas](#72-listar-tiendas)
   - [Obtener tienda por ID](#73-obtener-tienda-por-id)
   - [Obtener tienda por slug](#74-obtener-tienda-por-slug)
   - [Actualizar tienda](#75-actualizar-tienda)
   - [Eliminar tienda](#76-eliminar-tienda)
8. [Módulo de Ubicaciones](#8-módulo-de-ubicaciones)
   - [Crear ubicación](#81-crear-ubicación)
   - [Listar ubicaciones](#82-listar-ubicaciones)
   - [Obtener ubicación por ID](#83-obtener-ubicación-por-id)
   - [Actualizar ubicación](#84-actualizar-ubicación)
   - [Eliminar ubicación](#85-eliminar-ubicación)
9. [Modelos de Datos](#9-modelos-de-datos)
10. [Enumeraciones](#10-enumeraciones)
11. [Paginación](#11-paginación)
12. [Ejemplos de Integración](#12-ejemplos-de-integración)
13. [Variables de Entorno](#13-variables-de-entorno)
14. [Despliegue en Render](#14-despliegue-en-render)

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

---

## 7. Módulo de Tiendas

Gestiona las tiendas del marketplace. Solo usuarios con rol `seller` o `admin` pueden crear tiendas.

### 7.1 Crear tienda

```
POST /api/v1/stores/
```

#### Reglas de negocio

- El `seller_id` debe corresponder a un usuario existente con rol `seller` o `admin`.
- El `slug` se genera automáticamente a partir del `store_name` si no se proporciona (normaliza tildes, espacios y caracteres especiales).
- El `slug` debe ser único en toda la plataforma.

#### Body (JSON)

| Campo              | Tipo      | Requerido | Descripción                                                     |
|--------------------|-----------|-----------|------------------------------------------------------------------|
| `seller_id`        | `int`     | Sí        | ID del usuario vendedor dueño de la tienda                      |
| `store_name`       | `string`  | Sí        | Nombre comercial de la tienda                                   |
| `slug`             | `string`  | No        | URL amigable única (ej: `mi-tienda`). Se genera automáticamente si se omite. Solo minúsculas, números y guiones. |
| `description`      | `string`  | No        | Descripción de la tienda                                        |
| `logo_url`         | `string`  | No        | URL del logo                                                    |
| `cover_image_url`  | `string`  | No        | URL de la imagen de portada                                     |
| `whatsapp_number`  | `string`  | No        | Número de WhatsApp de contacto                                  |
| `location_id`      | `int`     | No        | ID de ubicación (módulo de ubicaciones, próximamente)           |

#### Ejemplo de petición

```bash
curl -X POST "https://mercado-plug-api.onrender.com/api/v1/stores/" \
  -H "Content-Type: application/json" \
  -d '{
    "seller_id": 2,
    "store_name": "Electrónica Rápida",
    "description": "Los mejores gadgets al mejor precio",
    "whatsapp_number": "+502 5555-9999"
  }'
```

#### Respuesta exitosa `201 Created`

```json
{
  "id": 1,
  "seller_id": 2,
  "store_name": "Electrónica Rápida",
  "slug": "electronica-rapida",
  "description": "Los mejores gadgets al mejor precio",
  "logo_url": null,
  "cover_image_url": null,
  "whatsapp_number": "+502 5555-9999",
  "location_id": null,
  "status": "active",
  "created_at": "2026-05-08T18:00:00Z"
}
```

#### Errores posibles

| Código | Condición                                                   |
|--------|--------------------------------------------------------------|
| `400`  | El slug ya está en uso                                       |
| `400`  | El usuario no tiene rol `seller` o `admin`                   |
| `404`  | El `seller_id` no corresponde a ningún usuario               |
| `422`  | Campos requeridos faltantes o formato de slug inválido       |

---

### 7.2 Listar tiendas

```
GET /api/v1/stores/
```

#### Query Parameters

| Parámetro   | Tipo  | Defecto | Descripción                                  |
|-------------|-------|---------|----------------------------------------------|
| `skip`      | `int` | `0`     | Offset de paginación                         |
| `limit`     | `int` | `20`    | Máximo de resultados (máx. `100`)            |
| `seller_id` | `int` | —       | Filtrar tiendas de un vendedor específico     |

#### Ejemplo de petición

```bash
# Todas las tiendas
curl "https://mercado-plug-api.onrender.com/api/v1/stores/"

# Tiendas de un vendedor específico
curl "https://mercado-plug-api.onrender.com/api/v1/stores/?seller_id=2"
```

#### Respuesta exitosa `200 OK`

```json
{
  "total": 3,
  "stores": [
    {
      "id": 1,
      "seller_id": 2,
      "store_name": "Electrónica Rápida",
      "slug": "electronica-rapida",
      "description": "Los mejores gadgets al mejor precio",
      "logo_url": null,
      "cover_image_url": null,
      "whatsapp_number": "+502 5555-9999",
      "location_id": null,
      "status": "active",
      "created_at": "2026-05-08T18:00:00Z"
    }
  ]
}
```

---

### 7.3 Obtener tienda por ID

```
GET /api/v1/stores/{store_id}
```

#### Path Parameters

| Parámetro  | Tipo  | Descripción           |
|------------|-------|-----------------------|
| `store_id` | `int` | ID único de la tienda |

#### Ejemplo de petición

```bash
curl "https://mercado-plug-api.onrender.com/api/v1/stores/1"
```

#### Respuesta exitosa `200 OK`

```json
{
  "id": 1,
  "seller_id": 2,
  "store_name": "Electrónica Rápida",
  "slug": "electronica-rapida",
  "description": "Los mejores gadgets al mejor precio",
  "logo_url": null,
  "cover_image_url": null,
  "whatsapp_number": "+502 5555-9999",
  "location_id": null,
  "status": "active",
  "created_at": "2026-05-08T18:00:00Z"
}
```

#### Errores posibles

| Código | Condición                  |
|--------|----------------------------|
| `404`  | La tienda no existe        |

---

### 7.4 Obtener tienda por slug

Ideal para construir URLs públicas del marketplace (ej: `mercadoplug.com/tienda/electronica-rapida`).

```
GET /api/v1/stores/slug/{slug}
```

#### Path Parameters

| Parámetro | Tipo     | Descripción                       |
|-----------|----------|-----------------------------------|
| `slug`    | `string` | Slug único de la tienda           |

#### Ejemplo de petición

```bash
curl "https://mercado-plug-api.onrender.com/api/v1/stores/slug/electronica-rapida"
```

#### Respuesta exitosa `200 OK`

_Mismo formato que [Obtener tienda por ID](#73-obtener-tienda-por-id)._

#### Errores posibles

| Código | Condición                  |
|--------|----------------------------|
| `404`  | La tienda no existe        |

---

### 7.5 Actualizar tienda

Actualiza parcialmente los campos de una tienda. Solo se modifican los campos enviados.

```
PATCH /api/v1/stores/{store_id}
```

#### Path Parameters

| Parámetro  | Tipo  | Descripción           |
|------------|-------|-----------------------|
| `store_id` | `int` | ID único de la tienda |

#### Body (JSON) — todos los campos son opcionales

| Campo              | Tipo     | Descripción                                        |
|--------------------|----------|----------------------------------------------------|
| `store_name`       | `string` | Nuevo nombre de la tienda                          |
| `slug`             | `string` | Nuevo slug (debe ser único)                        |
| `description`      | `string` | Nueva descripción                                  |
| `logo_url`         | `string` | Nueva URL del logo                                 |
| `cover_image_url`  | `string` | Nueva URL de imagen de portada                     |
| `whatsapp_number`  | `string` | Nuevo número de WhatsApp                           |
| `location_id`      | `int`    | Nuevo ID de ubicación                              |
| `status`           | `string` | Nuevo estado: `active`, `inactive` o `suspended`   |

#### Ejemplo de petición

```bash
curl -X PATCH "https://mercado-plug-api.onrender.com/api/v1/stores/1" \
  -H "Content-Type: application/json" \
  -d '{
    "logo_url": "https://cdn.mercadoplug.com/logos/electronica-rapida.png",
    "status": "active"
  }'
```

#### Respuesta exitosa `200 OK`

_Mismo formato que [Obtener tienda por ID](#73-obtener-tienda-por-id) con los campos actualizados._

#### Errores posibles

| Código | Condición                          |
|--------|------------------------------------|
| `400`  | El nuevo slug ya está en uso       |
| `404`  | La tienda no existe                |
| `422`  | Valor inválido en algún campo      |

---

### 7.6 Eliminar tienda

```
DELETE /api/v1/stores/{store_id}
```

#### Path Parameters

| Parámetro  | Tipo  | Descripción           |
|------------|-------|-----------------------|
| `store_id` | `int` | ID único de la tienda |

#### Ejemplo de petición

```bash
curl -X DELETE "https://mercado-plug-api.onrender.com/api/v1/stores/1"
```

#### Respuesta exitosa `204 No Content`

_Sin cuerpo de respuesta._

#### Errores posibles

| Código | Condición                  |
|--------|----------------------------|
| `404`  | La tienda no existe        |

---

## 8. Módulo de Ubicaciones

Gestiona las ubicaciones geográficas. Una ubicación puede asociarse a una tienda mediante el campo `location_id`.

### 8.1 Crear ubicación

```
POST /api/v1/locations/
```

#### Body (JSON)

| Campo                | Tipo     | Requerido | Descripción                                                    |
|----------------------|----------|-----------|----------------------------------------------------------------|
| `province`           | `string` | Sí        | Provincia                                                      |
| `country`            | `string` | No        | País (defecto: `"República Dominicana"`)                       |
| `municipality`       | `string` | No        | Municipio                                                      |
| `sector`             | `string` | No        | Sector o barrio                                                |
| `address_line`       | `string` | No        | Dirección exacta (calle, número, edificio, etc.)               |
| `reference_point`    | `string` | No        | Punto de referencia para llegar (ej: "frente al parque central") |
| `additional_details` | `string` | No        | Detalles adicionales de la ubicación                           |

#### Ejemplo de petición

```bash
curl -X POST "https://mercado-plug-api.onrender.com/api/v1/locations/" \
  -H "Content-Type: application/json" \
  -d '{
    "province": "Santo Domingo",
    "municipality": "Santo Domingo Este",
    "sector": "Los Mameyes",
    "address_line": "Calle 5, Casa #12",
    "reference_point": "Frente a la farmacia Carol"
  }'
```

#### Respuesta exitosa `201 Created`

```json
{
  "id": 1,
  "country": "República Dominicana",
  "province": "Santo Domingo",
  "municipality": "Santo Domingo Este",
  "sector": "Los Mameyes",
  "address_line": "Calle 5, Casa #12",
  "reference_point": "Frente a la farmacia Carol",
  "additional_details": null
}
```

#### Errores posibles

| Código | Condición                             |
|--------|---------------------------------------|
| `422`  | `province` vacío o faltante           |

---

### 8.2 Listar ubicaciones

```
GET /api/v1/locations/
```

#### Query Parameters

| Parámetro      | Tipo     | Defecto | Descripción                                    |
|----------------|----------|---------|------------------------------------------------|
| `skip`         | `int`    | `0`     | Offset de paginación                           |
| `limit`        | `int`    | `20`    | Máximo de resultados (máx. `100`)              |
| `province`     | `string` | —       | Filtrar por provincia (búsqueda parcial)        |
| `municipality` | `string` | —       | Filtrar por municipio (búsqueda parcial)        |

#### Ejemplo de petición

```bash
# Todas las ubicaciones
curl "https://mercado-plug-api.onrender.com/api/v1/locations/"

# Filtrar por provincia
curl "https://mercado-plug-api.onrender.com/api/v1/locations/?province=Santiago"
```

#### Respuesta exitosa `200 OK`

```json
{
  "total": 10,
  "locations": [
    {
      "id": 1,
      "country": "República Dominicana",
      "province": "Santo Domingo",
      "municipality": "Santo Domingo Este",
      "sector": "Los Mameyes",
      "address_line": "Calle 5, Casa #12",
      "reference_point": "Frente a la farmacia Carol",
      "additional_details": null
    }
  ]
}
```

---

### 8.3 Obtener ubicación por ID

```
GET /api/v1/locations/{location_id}
```

#### Path Parameters

| Parámetro     | Tipo  | Descripción               |
|---------------|-------|---------------------------|
| `location_id` | `int` | ID único de la ubicación  |

#### Ejemplo de petición

```bash
curl "https://mercado-plug-api.onrender.com/api/v1/locations/1"
```

#### Respuesta exitosa `200 OK`

_Mismo formato que la respuesta de crear ubicación._

#### Errores posibles

| Código | Condición                    |
|--------|------------------------------|
| `404`  | La ubicación no existe       |

---

### 8.4 Actualizar ubicación

Actualiza parcialmente los campos de una ubicación.

```
PATCH /api/v1/locations/{location_id}
```

#### Path Parameters

| Parámetro     | Tipo  | Descripción               |
|---------------|-------|---------------------------|
| `location_id` | `int` | ID único de la ubicación  |

#### Body (JSON) — todos los campos son opcionales

| Campo                | Tipo     | Descripción                        |
|----------------------|----------|------------------------------------|
| `country`            | `string` | País                               |
| `province`           | `string` | Provincia                          |
| `municipality`       | `string` | Municipio                          |
| `sector`             | `string` | Sector o barrio                    |
| `address_line`       | `string` | Dirección exacta                   |
| `reference_point`    | `string` | Punto de referencia                |
| `additional_details` | `string` | Detalles adicionales               |

#### Ejemplo de petición

```bash
curl -X PATCH "https://mercado-plug-api.onrender.com/api/v1/locations/1" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "Los Trinitarios",
    "address_line": "Calle Principal #45"
  }'
```

#### Respuesta exitosa `200 OK`

_Mismo formato que la respuesta de crear ubicación con los campos actualizados._

#### Errores posibles

| Código | Condición                    |
|--------|------------------------------|
| `404`  | La ubicación no existe       |

---

### 8.5 Eliminar ubicación

```
DELETE /api/v1/locations/{location_id}
```

> Al eliminar una ubicación, el campo `location_id` de las tiendas que la referenciaban se pone automáticamente en `null` (`SET NULL`).

#### Path Parameters

| Parámetro     | Tipo  | Descripción               |
|---------------|-------|---------------------------|
| `location_id` | `int` | ID único de la ubicación  |

#### Ejemplo de petición

```bash
curl -X DELETE "https://mercado-plug-api.onrender.com/api/v1/locations/1"
```

#### Respuesta exitosa `204 No Content`

_Sin cuerpo de respuesta._

#### Errores posibles

| Código | Condición                    |
|--------|------------------------------|
| `404`  | La ubicación no existe       |

---

## 9. Modelos de Datos

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

### Tienda (`Store`)

```json
{
  "id": 1,
  "seller_id": 2,
  "store_name": "string",
  "slug": "string",
  "description": "string | null",
  "logo_url": "string | null",
  "cover_image_url": "string | null",
  "whatsapp_number": "string | null",
  "location_id": "int | null",
  "status": "active | inactive | suspended",
  "created_at": "2026-05-08T18:00:00Z"
}
```

### Ubicación (`Location`)

```json
{
  "id": 1,
  "country": "República Dominicana",
  "province": "string",
  "municipality": "string | null",
  "sector": "string | null",
  "address_line": "string | null",
  "reference_point": "string | null",
  "additional_details": "string | null"
}
```

---

## 10. Enumeraciones

### `role` — Rol del usuario

| Valor    | Descripción                                              |
|----------|----------------------------------------------------------|
| `buyer`  | Comprador. Puede navegar y comprar productos. (defecto)  |
| `seller` | Vendedor. Puede publicar y gestionar productos.          |
| `admin`  | Administrador. Acceso total a la plataforma.             |

### `status` (Usuario) — Estado del usuario

| Valor      | Descripción                                           |
|------------|-------------------------------------------------------|
| `active`   | Cuenta activa. Acceso normal. (defecto al crear)      |
| `inactive` | Cuenta desactivada temporalmente.                     |
| `banned`   | Cuenta suspendida por violación de políticas.         |

### `status` (Tienda) — Estado de la tienda

| Valor       | Descripción                                           |
|-------------|-------------------------------------------------------|
| `active`    | Tienda activa y visible en el marketplace. (defecto)  |
| `inactive`  | Tienda desactivada temporalmente por el vendedor.     |
| `suspended` | Tienda suspendida por el administrador.               |

---

## 11. Paginación

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

## 12. Ejemplos de Integración

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
    role: 'seller'
  })
});
const user = await response.json();

// Crear una tienda para ese usuario
const storeRes = await fetch('https://mercado-plug-api.onrender.com/api/v1/stores/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    seller_id: user.id,
    store_name: 'Electrónica Rápida',
    description: 'Los mejores gadgets',
    whatsapp_number: '+502 5555-9999'
  })
});
const store = await storeRes.json();

// Obtener tienda por slug
const bySlug = await fetch(`https://mercado-plug-api.onrender.com/api/v1/stores/slug/${store.slug}`);

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

# Crear tienda
store = requests.post(f"{BASE_URL}/stores/", json={
    "seller_id": user["id"],
    "store_name": "Electrónica Rápida",
    "description": "Los mejores gadgets",
}).json()

# Obtener tienda por slug
store_by_slug = requests.get(f"{BASE_URL}/stores/slug/{store['slug']}").json()

# Actualizar tienda
requests.patch(f"{BASE_URL}/stores/{store['id']}", json={"status": "inactive"})

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

## 13. Variables de Entorno

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

## 14. Despliegue en Render

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

*Documentación generada para Mercado Plug API v0.3.0 — Mayo 2026*
