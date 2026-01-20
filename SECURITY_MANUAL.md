# Manual de Arquitectura y Seguridad - Auth Practice (v2.1)

## 1. Tecnologías de Defensa (Capas de Seguridad)
Este proyecto implementa una estrategia de "Defensa en Profundidad" escalable hacia seguridad Poscuántica.

| Capa | Tecnología | Función | Estado |
|------|------------|---------|--------|
| **Cifrado** | `Bcrypt` | Hash de contraseñas robusto (Blowfish cipher). | ✅ Activo |
| **Persistencia** | `SQLAlchemy` | ORM que previene inyección SQL de forma nativa. | ✅ Activo |
| **Sesiones** | `Flask-Login` | Gestión segura de cookies de sesión (HttpOnly). | ✅ Activo |
| **Anti-Ataques** | `Flask-Limiter` | Bloqueo de fuerza bruta (5 req/min) en Login/2FA/SMS. | ✅ Activo |
| **Comunicación** | `Flask-Mail` | Envío de tokens seguros vía SMTP (TLS). | ✅ Activo |
| **Móvil** | `SMS (Simulado)` | Verificación de propiedad de línea telefónica. | ✅ Activo (Dev Mode) |
| **Tokens** | `ItsDangerous` | Firmado criptográfico de enlaces temporales (Time-based). | ✅ Activo |
| **Secretos** | `.env` | Variables de entorno para ocultar llaves y credenciales. | ✅ Activo |
| **Políticas** | `Regex` | Validación estricta (Min 8 chars, Num, Mayús, Simb). | ✅ Activo |
| **2FA** | `PyOTP` + `QR` | Autenticación de doble factor (TOTP estándar). | ✅ Activo |
| **Recuperación** | `Secrets` | Códigos de respaldo de un solo uso (Backup Codes). | ✅ Activo |

## 2. Arquitectura Modular (Blueprints)

El sistema ha evolucionado de un monolito a una arquitectura basada en paquetes (`app/blueprints/auth/`).

### Rutas de Autenticación (`auth/routes_auth.py`)
* **`GET/POST /register`:**
  * Normalización de correo a minúsculas.
  * Captura de teléfono (`phone`).
  * Creación de usuario en estado `confirmed=False`.
  * Envío automático de correo de confirmación.
* **`GET /confirm/<token>`:**
  * Valida la firma criptográfica y la expiración del token.
  * Cambia el estado del usuario a `confirmed=True`.
* **`GET/POST /login`:**
  * **Escudo 1:** Rate Limiting.
  * **Escudo 2:** Verificación de Hash.
  * **Escudo 3:** Verificación de Email Confirmado (Bloquea si no confirmó).
  * **Escudo 4:** Si tiene 2FA, redirige a flujo de verificación.

### Rutas de Seguridad (`auth/routes_security.py`)
* **`GET/POST /verify-2fa-login`:** Validación de TOTP o Backup Codes.
* **`GET/POST /reset_password`:** Solicitud de enlace de recuperación (No revela si el mail existe).
* **`GET/POST /reset_password/<token>`:** Cambio de contraseña mediante token firmado.
* **`GET /enable-2fa`:** Generación de secretos y QR en memoria (Buffer).
* **`GET /send-sms-verification`:**
  * Genera código numérico aleatorio (6 dígitos).
  * Simula envío (Flash Message / Terminal) para modo desarrollo.
  * Almacena código en sesión temporalmente.
* **`GET/POST /verify-sms`:**
  * Valida que el código ingresado coincida con el generado.
  * Marca el teléfono como verificado (`is_phone_verified=True`).

## 3. Modelo de Datos (`User`)
* `id`: Identificador único (PK).
* `username`: Nombre de usuario (Unique).
* `email`: Correo electrónico (Unique, Obligatorio).
* `phone_number`: Número de celular (Unique, Nullable).
* `password`: Hash de la contraseña.
* `confirmed`: Booleano (True/False) - Email confirmado.
* `confirmed_on`: Fecha y hora de confirmación de email.
* `is_phone_verified`: Booleano (True/False) - Teléfono validado por SMS.
* `otp_secret`: Clave secreta TOTP (Nullable).
* `backup_codes`: String de códigos de emergencia (Nullable).

## 4. Flujos de Usuario
1. **Registro:** Usuario -> Datos (+Teléfono) -> BD (Inactivo) -> Email Token.
2. **Activación:** Usuario -> Clic Email -> Validación Token -> BD (Activo).
3. **Login:** Usuario -> Credenciales -> Check Activo -> (Opcional 2FA) -> Dashboard.
4. **Verificación Móvil:** Dashboard -> Solicitar SMS -> Código Simulado -> Validación -> BD (Teléfono Verificado).