# Manual de Arquitectura y Seguridad - Auth Practice

## 1. Tecnologías de Defensa (Capas de Seguridad)
Este proyecto implementa una estrategia de "Defensa en Profundidad".

| Capa | Tecnología | Función | Estado |
|------|------------|---------|--------|
| **Cifrado** | `Bcrypt` | Hash de contraseñas (Blowfish cipher). | ✅ Activo |
| **Persistencia** | `SQLAlchemy` | ORM que previene inyección SQL. | ✅ Activo |
| **Sesiones** | `Flask-Login` | Gestión segura de cookies de sesión. | ✅ Activo |
| **Anti-Ataques** | `Flask-Limiter` | Bloqueo de fuerza bruta (Rate Limiting). | ✅ Activo (5 req/min) |
| **Secretos** | `.env` | Variables de entorno para ocultar llaves. | ✅ Activo |
| **Políticas** | `Regex` | Validación de contraseña (Min 8 chars, Num, Mayús). | ✅ Activo |
| **2FA** | `PyOTP` + `QR` | Autenticación de doble factor (TOTP estándar). | ✅ Activo |
| **Recuperación** | `Secrets` | Códigos de respaldo de un solo uso (Backup Codes). | ✅ Activo |

## 2. Mapa de Funciones (`routes.py`)

### Rutas Públicas
* **`GET /` (home):** Pantalla de bienvenida.
* **`GET/POST /register`:** * Valida complejidad de contraseña.
  * Verifica unicidad de usuario.
  * Crea hash y guarda en DB.
* **`GET/POST /login`:**
  * **Escudo:** Protegido por Rate Limiting.
  * Verifica credenciales (Hash).
  * **Lógica de Desvío:** Si el usuario tiene 2FA activado, NO inicia sesión completa; redirige a `/verify-2fa` creando una sesión temporal.

### Rutas Protegidas (Requieren Login)
* **`GET/POST /verify-2fa`:**
  * Verifica el token TOTP (App Authenticator).
  * Verifica códigos de respaldo (Backup Codes).
  * **Burn-on-use:** Si se usa un código de respaldo, se elimina de la DB instantáneamente.
* **`GET /dashboard`:**
  * Panel de control. Muestra el estado del 2FA.
* **`GET /enable-2fa`:**
  * Genera secreto TOTP.
  * Genera 5 códigos de respaldo hexadecimales.
  * Renderiza QR en memoria (Buffer) para no dejar residuos en disco.
* **`GET /logout`:**
  * Cierra sesión y limpia variables temporales.

## 3. Modelo de Datos (`User`)
* `id`: Identificador único.
* `username`: Nombre de usuario.
* `password`: Hash de la contraseña.
* `otp_secret`: Clave secreta para generar códigos TOTP (Nullable).
* `backup_codes`: String de texto plano con códigos separados por comas (Nullable).