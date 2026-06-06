# Bot Detection Signals

## Definición

Las señales de detección de bots son atributos observables de requests HTTP, sesiones de navegador y patrones de comportamiento que diferencian el tráfico automatizado del tráfico humano legítimo. No existe una señal única suficiente — la detección efectiva puntúa múltiples familias de señales en conjunto.

## Por qué importa

La mayoría de los ataques de aplicación a escala son llevados a cabo por bots: credential stuffing, card testing, web scraping, abuso de APIs, fraude de inventario, y explotación de lógica de negocio automatizada. Las señales de detección de bots son tanto un primitivo defensivo (cómo los defensores detectan y bloquean el tráfico automatizado) como un primitivo ofensivo (cómo los atacantes sofisticados evaden la detección). Entender el modelo de señales en ambas direcciones es lo que separa la evasión de bots basada en reglas de la evasión real.

## Las cinco familias de señales

### 1. Señales de red

Atributos de la capa de transporte y red que son difíciles de falsificar o costosos de diversificar:

- **Reputación de IP** — las IPs en rangos conocidos de datacenter, IPs previamente vistas en abuso, IPs en blocklists públicas (Spamhaus, AbuseIPDB), o IPs con baja edad de primera vista.
- **ASN / proveedor de hosting** — el Número de Sistema Autónomo identifica el proveedor de red. El tráfico legítimo de usuarios viene principalmente de ISPs residenciales y de telefonía móvil; el tráfico de bots a escala frecuentemente se concentra en pocos ASNs de hosting o proxy.
- **Proporción de proxies y TOR** — las IPs de salida de TOR y los proxies residenciales conocidos (BrightData, Oxylabs, etc.) son señales de alto valor cuando el caso de uso no los justifica.
- **Geolocalización vs. Accept-Language** — un request con `Accept-Language: en-US` desde una IP de geolocalización en un país no angloparlante es un mismatch de señal débil.
- **Huella de TLS** — el fingerprint JA3/JA4 de la negociación TLS identifica la librería de cliente (cURL, Python requests, un navegador específico). El spoofing requiere controlar la librería de TLS, no solo el User-Agent.

### 2. Señales de protocolo HTTP

Propiedades del request HTTP que difieren entre clientes reales y automatizados:

- **Orden de headers y presencia** — los navegadores reales envían headers en un orden consistente específico del navegador. Los clientes HTTP automatizados tienen sus propios órdenes por defecto. Las librerías como `requests` de Python omiten headers que los navegadores siempre incluyen (`Accept-Encoding`, `Accept-Language`, `Upgrade-Insecure-Requests`, `Sec-Fetch-*`).
- **Headers Sec-Fetch-*** — `Sec-Fetch-Site`, `Sec-Fetch-Mode`, `Sec-Fetch-Dest`, `Sec-Fetch-User` son inyectados por el navegador y reflejan el contexto del request (navegación vs. fetch vs. subresource). Los clientes automatizados generalmente los omiten o establecen valores inconsistentes.
- **Accept y Accept-Encoding** — los navegadores tienen firmas de Accept específicas de versión. `Accept: */*` (el default de cURL/requests) es señal de bot.
- **Cookie de sesión ausente o sintética** — la ausencia de cookies de sesión o cookies de fingerprint de dispositivo que los humanos acumularían en sesiones reales.
- **Referer inconsistente** — un request de "navegación directa" que llega a una página de pago profunda sin referer de la página del producto es biológicamente inusual.

### 3. Señales declaradas por el cliente

Atributos que el cliente declara sobre sí mismo:

- **User-Agent** — la señal más fácilmente falseada, pero igualmente hay valor en: UA de navegadores obsoletos (bots frecuentemente no actualizan sus strings), UAs de librerías de HTTP reconocibles (Python-requests, Go-http, Java/OkHttp), UAs que no coinciden con fingerprints de TLS, y UAs ausentes.
- **Cabeceras de plataforma** (`Sec-CH-UA`, `Sec-CH-UA-Platform`, `Sec-CH-UA-Mobile`) — estas Client Hints revelan la plataforma real declarada por el navegador. Los bots que falsean Chrome en desktop pero omiten estas headers (requeridas por Chrome moderno) se detectan por omisión.
- **Accept-Language y zona horaria** — los humanos tienen zonas horarias y lenguajes consistentes con su comportamiento de uso.

### 4. Señales de browser/runtime

Atributos de la ejecución JavaScript en el contexto del navegador — la familia de señales más rica para los bots que usan navegadores reales o headless:

- **Fingerprinting del navegador** — canvas fingerprint, WebGL renderer, propiedades de AudioContext, fuentes disponibles, resolución de pantalla y profundidad de color, propiedades de navigator, zona horaria declarada por JS. Un headless Chrome tiene un fingerprint muy diferente a un Chrome usuario real.
- **Propiedades de automatización** — `navigator.webdriver` (true en WebDriver/Selenium/Playwright), `window.callPhantom`, `window._phantom`, `navigator.plugins.length === 0` (headless Chrome), propiedades de timing que revelan ejecución no interactiva.
- **Señales de interacción humana** — curvas de movimiento de mouse (los humanos tienen jitter, aceleración y desaceleración; los bots tienen movimiento lineal o cuadrático), posición de clic (los humanos raramente hacen clic exactamente en el centro de un botón), timing de teclado (los humanos tienen ritmo de tecleo variable), eventos de scroll y profundidad de página.
- **Fingerprint de lienzo y WebGL** — idéntico en todas las sesiones del mismo bot, diferente en cada usuario humano real.
- **Verificación de entorno de sandbox** — propiedades que revelan contenedores de browser automation (ausencia de extensiones, absence de historial del navegador, tiempos de carga de página perfectamente consistentes).

### 5. Señales de comportamiento / negocio

Patrones de interacción de nivel de sesión y de escala de cuenta que son anomalías estadísticas para usuarios reales:

- **Velocidad de requests** — cientos de requests de login por minuto desde una IP o ASN. Los humanos hacen login una o dos veces; los atacantes de credential stuffing hacen miles.
- **Distribución de pares usuario/contraseña** — el credential stuffing prueba muchas cuentas distintas; el password spraying prueba la misma contraseña en muchas cuentas. Ninguno tiene el patrón de reintentos de un usuario humano que olvidó su contraseña.
- **Distribución de sesiones entre IPs** — los usuarios legítimos tienen sesiones estables desde una o pocas IPs; los bots rotan IPs a través de proxies.
- **Patrones de navegación** — el tráfico humano sigue distribuciones de Zipf por página visitada. Los bots a menudo acceden a un conjunto uniforme de endpoints (solo la API de búsqueda, solo el endpoint de checkout) con distribuciones anormalmente planas.
- **Tiempo en página y profundidad de scroll** — el tiempo de sesión cero, sin scroll, y con click directo al form es un patrón de bot.
- **Señales específicas del dominio de negocio** — compras en múltiples cuentas con las mismas credenciales de pago, redención de cupones desde cuentas recién creadas, creación masiva de cuentas con nombres de usuario con patrones, transacciones de alto valor con comportamiento de navegación bajo.

## Ataques comunes y sus perfiles de señal

### Credential Stuffing

**Perfil:** gran volumen de intentos de login con pares usuario/contraseña de bases de datos de filtraciones. Señales: alta tasa de requests de login, alta tasa de fallo (muchos 401/403), rotación de IPs (proxies residenciales), UAs imitando navegadores reales pero con fingerprints de TLS y headers inconsistentes, tiempo de sesión cero (sin actividad post-login exitoso en muchas pruebas), patrones de timing de requests consistentes (no naturalmente jittered).

**Objetivo de detección:** detectar la campaña, no el intento individual. Ningún intento individual es distinguible de un login humano fallido; la distribución de la campaña es lo que se detecta.

### Scraping

**Perfil:** extracción sistemática de contenido de la app a gran escala. Señales: ausencia de JS execution (para scrapers simples basados en HTTP), fingerprint de navegador headless (para scrapers basados en Playwright/Puppeteer), patrones de navegación extremadamente regulares (cada URL de producto, sin variación), ausencia de señales de interacción humana, acceso directo a endpoints de API evitando el HTML.

**Objetivo de detección:** las primeras solicitudes de cualquier scraper son a menudo indistinguibles. La firma se hace visible en la secuencia de URLs visitadas y en la ausencia de comportamiento de exploración lateral.

### Carding (Card Testing)

**Perfil:** probar grandes volúmenes de números de tarjeta robados en formularios de pago. Señales: alto volumen de transacciones rechazadas, variación mínima en el monto de transacción (frecuentemente $0.01 o $1.00 para probar), patrones de velocidad (muchas transacciones por minuto), ausencia de comportamiento normal de compra (sin carrito, sin browsing, directo al checkout), alta densidad de fallo seguida ocasionalmente de éxito.

## Detección y defensa

Ordenado por efectividad:

1.
**Puntuación multicapa de señales.**
   No hay ninguna señal que sea suficiente. Un único User-Agent falso, o una sola IP de datacenter, puede tener explicaciones legítimas. La detección efectiva agrega señales de múltiples familias en un score. Un score alto de red + alto de protocolo + bajo de interacción humana = bot de alta confianza, incluso si cada señal individual es ambigua.

2.
**Fingerprinting de TLS (JA3/JA4).**
   La huella de handshake TLS es mucho más difícil de falsear que el User-Agent. Requerir que el fingerprint TLS coincida con la librería de TLS del navegador declarado en el User-Agent elimina la mayoría de los bots simples que usan cURL o Python requests con UAs de Chrome.

3.
**Verificación de señales de browser runtime (JavaScript).**
   Desplegar challenges de JS que recopilan señales de fingerprint de navegador, propiedades de automatización, y comportamiento de interacción. Los reCAPTCHA de Google y hCaptcha hacen esto. Las soluciones propias pueden implementarlo sin mostrar un challenge visible al usuario.

4.
**Limitar velocidad y aplicar escalonamiento progresivo.**
   Para el credential stuffing, el rate limiting de login por cuenta, por IP, y por fingerprint de dispositivo es más efectivo que bloquear IPs individuales. Aplicar delay exponencial en reintentos de fallo, agregar challenges (CAPTCHA, MFA) al umbrales de velocidad.

5.
**Reputación de IP y ASN en tiempo real.**
   Usar feeds comerciales o comunitarios de reputación de IP (Cloudflare, AWS WAF, DataDome, PerimeterX, Arkose, Akamai Bot Manager) que agregan señales de abuse a través de muchos clientes. Las IPs de proxies residenciales son un desafío continuo — su reputación cambia más rápido que las listas estáticas.

6.
**Señales de comportamiento de negocio como segunda capa.**
   Construir detectores específicos del dominio: velocidad de redención de cupones por cuenta nueva, ratio de transacciones rechazadas por método de pago, velocidad de creación de cuentas desde fingerprints de dispositivo similares.

### Qué no funciona como defensa primaria

- **Bloquear solo por User-Agent.** Los bots modernos falsean UAs. El bloqueo por UA también bloquea usuarios legítimos con UAs no estándar (lectores de pantalla, navegadores menos comunes).
- **Bloqueo estático de IPs.** Los bots rotan a través de proxies residenciales. La vida útil de un bloqueo de IP individual es horas para un atacante motivado.
- **CAPTCHAs como única defensa.** Los CAPTCHAs modernos se resuelven con frecuencias altas por servicios de resolución humana y visión por computadora. Son una fricción de señal, no una barrera absoluta.
- **Throttling sin fingerprinting.** El rate limiting basado solo en IP se evade trivialmente con rotación de proxy.

## Ejemplos prácticos

- Un formulario de login recibe 50,000 intentos de credential stuffing en 20 minutos: la rotación de proxies residenciales hace que el bloqueo por IP sea ineficaz, pero el fingerprint JA3 consistente (todos los bots usan la misma librería Python) y la ausencia de headers `Sec-Fetch-*` permiten detectar la campaña.
- Un scraper de e-commerce usa Playwright con Chrome headless: supera las verificaciones de User-Agent y TLS, pero `navigator.webdriver === true`, canvas fingerprint idéntico entre "sesiones", y ausencia de jitter en el movimiento del mouse lo delatan.
- Card testing en un checkout: cada transacción es $0.01, el tráfico llega sin cookies de sesión previas, el tiempo en página es < 1 segundo, y el ratio de fallo es 98%. Cada señal individual podría ser un usuario legítimo; la combinación es inequívoca.

## Notas relacionadas

- [[rate-limiting]] — el mecanismo de mitigación primario para ataques de volumen.
- [[browser-fingerprinting]] — la familia de señales de runtime del navegador en detalle.
- [[auth-flaws]] — el credential stuffing es el vector de ataque de autenticación más escalado.
- [[business-logic-vulnerabilities]] — muchos ataques de bots explotan lógica de negocio.

## Referencias

- **Fundamental:** OWASP Automated Threats to Web Applications — https://owasp.org/www-project-automated-threats-to-web-applications/
- **Investigación / Deep Dive:** Incolumitas Bot Detection Benchmark — https://bot.incolumitas.com/
- **Investigación / Deep Dive:** JA3 TLS fingerprinting — https://github.com/salesforce/ja3
- **Mitigación:** Cloudflare Bot Management documentation — https://developers.cloudflare.com/bots/
