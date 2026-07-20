# JWT Cryptographic Correctness

## Definición

Un JSON Web Token (JWT) es un formato de token compacto para transmitir afirmaciones entre partes. Un JWT consiste en un header, un payload, y una firma o tag de autenticación, cada uno codificado en Base64url y separado por puntos: `header.payload.signature`. La corrección criptográfica del JWT es el subconjunto de preocupaciones sobre qué tan bien la librería y el código de la aplicación validan la firma, las afirmaciones, y el uso intendido.

## Por qué importa

Los JWTs son omnipresentes pero tienen múltiples vectores de ataque bien documentados, todos los cuales existen porque la librería o la aplicación tomaron una decisión de confianza incorrecta antes de aceptar el token. Las explotaciones siguen un patrón: "la librería aceptó el algoritmo o clave del token antes de que el verificador lo inspeccionara." El resultado es falsificación de token completa a pesar de que la firma es técnicamente válida para la secuencia de bytes incorrecta.

## Cómo funciona

La verificación JWT tiene **5 pasos obligatorios**:

1.
**Decidir el algoritmo antes de parsear el token.**
   El verificador debe tener una lista permitida fija — `HS256`, `RS256`, `ES256`, etc. — no derivarla del header del token.

2.
**Resolver la clave usando identidad confiable.**
   Mapear a partir de configuración, no del campo `kid` del token sin sanitizar. Si se usa un endpoint `jku`/`jwks_uri`, ese endpoint debe estar en una lista permitida fija.

3.
**Verificar la firma con el algoritmo y la clave elegidos.**
   La librería verifica el HMAC o la firma asimétrica sobre `base64url(header) || '.' || base64url(payload)`.

4.
**Validar las afirmaciones de payload.**
   Verificar `iss`, `aud`, `exp`, `nbf`, y cualquier afirmación personalizada de la aplicación.

5.
**Pinar el propósito del token.**
   Un token de reset de contraseña no debe ser aceptado donde se espera un token de sesión. Usar `aud` o una afirmación de propósito personalizada.

```
# Mal: deja que el header controle el algoritmo
jwt.decode(token, key=public_key)  # vulnerable a alg:none, RS256→HS256

# Bien: fija el algoritmo del lado del verificador
jwt.decode(token, key=public_key, algorithms=["RS256"])
```

El bug no es "JWT es inseguro." El bug es "el verificador trusts el token en sí para elegir su propio algoritmo o clave."

## Técnicas / patrones

- Buscar `algorithms=None`, `algorithm=None`, `options={"verify_signature": False}`, `ignoreExpiration`, `complete=True` sin verificación, y omisión explícita de cualquier verificación de afirmación.
- Verificar si `kid` se usa directamente en lookups de base de datos, filesystem, o URL sin validación.
- Verificar si se siguen endpoints `jku`/`jwks_uri` dinámicamente o si están fijos en configuración.
- Buscar el mismo secreto HMAC para múltiples propósitos de token.
- Verificar si `alg: "none"` es rechazado explícitamente por la configuración de la librería.
- Verificar los tipos de token: los tokens de sesión no deben ser aceptados para reset de contraseña, invite, o cualquier otro camino de alta seguridad.

## Variantes y bypasses

Las 7 formas de exploit del JWT, ordenadas del más al menos frecuente en la práctica.

### 1. `alg: "none"`

El token afirma que no se requiere firma. Algunas librerías lo aceptaron por defecto. La defensa: la lista permitida de algoritmos debe incluir solo algoritmos que produzcan firmas reales.

### 2. Confusión RS256 → HS256

Un token firmado con una clave pública RSA como secreto HMAC. Si la librería acepta tanto RS256 como HS256 y usa la misma clave para ambos, el atacante firma el token usando la clave pública conocida como secreto HMAC. La defensa: fijar el algoritmo antes del tiempo de verificación, no inferirlo del header.

### 3. Secretos HMAC débiles

Los tokens `HS256` con secretos cortos o predecibles son brute-forceables offline. La defensa: los secretos HMAC deben tener al menos 256 bits de entropía, nunca ser contraseñas o defaults.

### 4. Inyección `kid`

El header del token incluye un campo `kid` que la aplicación usa para seleccionar una clave. Si `kid` se usa en un lookup de base de datos o filesystem sin sanitización, puede convertirse en SQL injection o path traversal para forzar el uso de una clave controlada por el atacante. La defensa: mapear `kid` a claves en una estructura de datos en memoria, nunca construir queries o paths desde él.

### 5. Endpoints `jku`/`jwk`/`x5u`/`x5c` dinámicos

Si la librería sigue `jku` o `jwks_uri` del header del token para recuperar la clave de verificación, el atacante puede apuntar a un servidor propio y servir su propia clave pública. La defensa: los endpoints JWKS deben estar fijos en configuración del lado del servidor.

### 6. Afirmaciones faltantes, incorrectas, o no verificadas

Un token que no valida `exp` puede ser reutilizado indefinidamente. Un token que no valida `iss` puede ser emitido por cualquier parte. Un token que no valida `aud` puede ser un token de un servicio diferente. La defensa: verificar explícitamente cada afirmación relevante.

### 7. Confusión JWE / token bearer-replay

JWE cifra el payload pero no prueba la identidad del emisor — la encryption no es autenticación. Los bearer tokens sin vinculación al contexto del cliente (IP, DPoP, certificado TLS) son usables por cualquiera que los intercepte. La defensa: usar DPoP o mTLS sender-constraint para tokens de alto valor; usar períodos de validez cortos y revocación.

## Impacto

Ordenado aproximadamente por severidad:

- **Falsificación completa de token.** Los exploits `alg:none` y RS256→HS256 permiten la creación de tokens con cualquier payload, incluyendo roles de admin.
- **Toma de sesión.**  Los tokens de larga duración interceptados o robados son utilizables por atacantes.
- **Escalada de privilegios.** Las afirmaciones no verificadas o los tokens de propósito cruzado permiten el acceso a funciones no previstas.
- **Inyección de clave.** La inyección `kid` puede llevar a SQL injection o path traversal más allá de la semántica del token.
- **Replay persistente.** Los tokens sin verificación `exp` o sin lista de revocación pueden ser reutilizados indefinidamente.

## Detección y defensa

Ordenado por efectividad:

1.
**Fijar la lista de algoritmos permitidos en el verificador, nunca desde el header del token.**
   Cada librería tiene un parámetro para esto. Incluir solo lo que realmente se usa: `["RS256"]` o `["HS256"]`, nunca `["RS256", "HS256"]` en la misma base de código si un subconjunto de claves es válido para ambos.

2.
**Nunca confiar en `kid`, `jku`, `jwk`, `x5u`, o `x5c` para selección dinámica de claves sin lista de permitidos fija.**
   Poner las claves de verificación en configuración o un key store. Mapear desde nombres de clave limpios y predefinidos.

3.
**Verificar todas las afirmaciones estándar: `exp`, `nbf`, `iss`, `aud`, y afirmaciones personalizadas de propósito.**
   No confiar en los defaults de la librería para `aud`/`iss` — confirmar que la librería los verifica activamente, no los ignora silenciosamente.

4.
**Usar tokens de alta entropía y corta duración para propósitos sensibles.**
   Los access tokens deben expirar en minutos; los refresh tokens en horas o días con capacidad de revocación. Secretos HMAC de 256 bits mínimo.

5.
**Usar diferentes secretos o pares de clave para diferentes propósitos de token.**
   Un token de reset de contraseña verificado con el mismo secreto que los tokens de sesión es un vector de falsificación cruzada.

### Qué no funciona como defensa primaria

- **"Usamos HTTPS, así que los tokens están protegidos en tránsito."** Las vulnerabilidades de JWT son del lado del servidor en el verificador — HTTPS no previene la falsificación de tokens.
- **"El payload está cifrado (JWE)."** El cifrado no es autenticación del emisor.
- **"La librería se encarga de la validación."** Muchas librerías JWT tienen defaults permisivos para compatibilidad con versiones anteriores. Verificar la configuración explícitamente.
- **"Usamos una clave larga."** Una clave larga no protege contra confusión de algoritmo o endpoints de clave mal fijados.
- **"Ponemos la expiración en el payload."** La expiración debe verificarse, no solo estar presente.

## Labs prácticos

### Verificar JWT con lista de algoritmos explícita en Python

```
pip install pyjwt cryptography
```

```
import jwt

# Bien: algoritmo fijo, verificación completa
payload = jwt.decode(
    token,
    public_key,
    algorithms=["RS256"],
    audience="api.example.com",
    issuer="auth.example.com",
)

# Mal: permite cualquier algoritmo del header
payload = jwt.decode(token, public_key)  # vulnerable
```

### Demostrar falsificación `alg:none`

```
import base64, json

def b64url(data):
    return base64.urlsafe_b64encode(
        data if isinstance(data, bytes) else data.encode()
    ).rstrip(b"=").decode()

header  = b64url(json.dumps({"alg":"none","typ":"JWT"}))
payload = b64url(json.dumps({"sub":"admin","exp":9999999999}))
forged  = f"{header}.{payload}."

# Si la librería acepta esto sin error, está mal configurada
try:
    jwt.decode(forged, options={"verify_signature": False})
    print("VULNERABLE: alg:none aceptado")
except Exception:
    print("OK: alg:none rechazado")
```

### Auditar JWT en un codebase

```
rg -n "algorithms=\[\]|algorithms=None|verify_signature.*False|ignoreExpiration|complete=True" .
rg -n "jwt\.decode\(" . | grep -v "algorithms="
```

Cada match es una posible verificación de algoritmo mal configurada.

## Ejemplos prácticos

- Una API acepta `RS256` y `HS256`. El atacante firma un token con la clave pública RSA como secreto HMAC. La API acepta el token como válido y el atacante gana acceso como admin.
- Una app Node.js usa `jwt.verify(token, secret)` sin el parámetro `algorithms`. La librería tiene un default de "todos los algoritmos." Un token `alg:none` es aceptado.
- Un endpoint de reset de contraseña acepta tokens de sesión normales porque ambos usan el mismo secreto HMAC. Un atacante con un token de sesión robado puede resetear contraseñas.
- El campo `kid` del token se usa en `SELECT key FROM keys WHERE id = ?` sin validación; el atacante inyecta `' OR '1'='1`.

## Notas relacionadas

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[digital-signatures]]
- [[asymmetric-encryption-and-key-exchange]]
- [[random-and-csprng-pitfalls]]
- [[auth-flaws|Auth Flaws]]

## Referencias

- **Estándar / RFC:** RFC 7519 JSON Web Token (JWT) — https://www.rfc-editor.org/rfc/rfc7519
- **Estándar / RFC:** RFC 7515 JSON Web Signature (JWS) — https://www.rfc-editor.org/rfc/rfc7515
- **Fundamental:** PortSwigger JWT Attacks — https://portswigger.net/web-security/jwt
- **Investigación / Deep Dive:** "Critical Vulnerabilities in JWT" — https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/
