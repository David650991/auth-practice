# Manual de Arquitectura y Seguridad - Auth Practice (v3.1 - Integral)

## 1. Tecnologías de Defensa (Capas de Seguridad)
Este proyecto implementa una estrategia de "Defensa en Profundidad" que combina seguridad clásica bancaria con defensa biométrica avanzada.

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
| **Biometría** | `Dlib` + `HOG` | Reconocimiento Facial mediante vectores de 128 dimensiones. | ✅ Activo |
| **Frontend** | `JS` + `Canvas` | Validación de "Liveness" básica y gestión de hardware (Cámara). | ✅ Activo |

## 2. Arquitectura Modular (Blueprints & Static)

El sistema opera bajo una arquitectura híbrida: Backend Modular (Blueprints) y Frontend Desacoplado.

### A. Backend (`app/blueprints/auth/`)
1.  **Rutas de Autenticación (`routes_auth.py`):**
    * **Registro:** Captura de datos + Teléfono + Envío de Email.
    * **Confirmación:** Validación de token criptográfico.
    * **Login:** 4 Escudos (Rate Limit -> Hash -> Email Check -> 2FA Check).
2.  **Rutas de Seguridad (`routes_security.py`):**
    * **2FA:** Generación de secretos TOTP y validación de códigos QR.
    * **Backup Codes:** Generación y validación de códigos de emergencia autodestructibles.
    * **SMS:** Lógica de generación de código (6 dígitos), almacenamiento en sesión y validación para marcar `is_phone_verified=True`.
    * **Reset Password:** Flujo seguro de recuperación vía Email.
3.  **Rutas Biométricas (`routes_biometric.py`) [NUEVO]:**
    * **`POST /face-enroll`:**
        * Recibe imagen Base64.
        * **Estrategia Híbrida:** Detecta rostro en Escala de Grises (Estabilidad) -> Codifica en RGB (Precisión).
        * Almacena el encoding (Pickle) en la BD.
    * **`POST /face-login`:**
        * Compara la imagen en vivo contra el encoding almacenado.
        * Tolerancia configurada: 0.5 (Alta precisión).

### B. Frontend (`app/static/`) [NUEVO]
Se ha eliminado el código monolítico en HTML para separar responsabilidades.
* **CSS (`static/css/`):** Estilos separados para `biometrics.css` (Registro) y `face_login.css` (Modo Oscuro).
* **JS (`static/js/`):** Lógica separada en `biometrics.js` y `face_login.js`.
* **Inyección de Configuración:** Patrón `window.CONFIG` para puente seguro Backend->Frontend.

## 3. Infraestructura Crítica y Compatibilidad
Para garantizar el funcionamiento de la IA (Dlib) en Windows, el entorno está congelado en versiones específicas ("Gold Standard").

* **Numpy:** `1.26.4` (Requerido para compatibilidad binaria con Dlib C++).
* **OpenCV:** `4.9.0.80` (Alineado con Numpy 1.x).
* **Dlib:** `.whl` precompilado manualmente.
* **Gestión de Memoria:** Implementación de `np.array(..., copy=True, order='C')` en el backend.

## 4. Modelo de Datos (`User`)
Representación completa de la tabla de usuarios en SQLite:

* `id`: Identificador único (PK).
* `username`: Nombre de usuario (Unique).
* `email`: Correo electrónico (Unique, Obligatorio).
* `phone_number`: Número de celular (Unique, Nullable).
* `password`: Hash Bcrypt.
* `confirmed`: Booleano (True/False) - Email confirmado.
* `confirmed_on`: Fecha y hora de confirmación.
* `is_phone_verified`: Booleano - Teléfono validado por SMS.
* `otp_secret`: Clave secreta TOTP (2FA).
* `backup_codes`: String de códigos de emergencia (Nullable).
* `face_encoding`: **[BLOB]** Huella matemática del rostro (Pickle).

## 5. Flujos de Usuario Completos
1.  **Registro:** Usuario -> Datos (+Teléfono) -> BD (Inactivo) -> Email Token.
2.  **Activación:** Usuario -> Clic Email -> Validación Token -> BD (Activo).
3.  **Login Clásico:** Credenciales -> Check Activo -> (Opcional 2FA/Backup Code) -> Dashboard.
4.  **Verificación Móvil:** Dashboard -> Solicitar SMS -> Código Simulado -> Validación -> BD (Teléfono Verificado).
5.  **Registro Biométrico:** Dashboard -> Encender Cámara -> Detección -> Guardado de Huella.
6.  **Login Facial:** Página Login -> "Login Facial" -> Detección -> Comparación Vectorial -> Acceso Directo.