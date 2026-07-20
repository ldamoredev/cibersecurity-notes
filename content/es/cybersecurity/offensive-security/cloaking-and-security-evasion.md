# Cloaking and Security Evasion

## Definición

El cloaking es la práctica de mostrar comportamiento diferente a distintos visitantes según señales como IP, geografía, ASN, reverse DNS, User-Agent, browser fingerprint, reputación del proxy o identidad percibida del scanner.

## Por qué importa

El cloaking aparece en fraude, phishing, entrega de malware, scraping de zona gris e infraestructura de abuso evasiva. También se usa a veces legítimamente para localización, cumplimiento o prevención de abuso. La pregunta de seguridad no es "¿varía el contenido?". La pregunta es si la variación oculta comportamiento malicioso a defensores, crawlers, scanners o revisores.

El proyecto mirror antiguo es un ejemplo compacto: permite Argentina, bloquea redes cloud/seguridad/vendor, verifica la reputación del proxy, sirve `robots.txt` y redirige o deniega el tráfico según señales débiles.

## Cómo funciona

El cloaking tiene **4 etapas**:

1. **Observar al visitante.**
   Recolectar IP, ASN/org, geolocalización, reverse DNS, headers, User-Agent, cookies, comportamiento JavaScript y secuencia de requests.

2. **Clasificar al visitante.**
   Decidir si el visitante parece una víctima, crawler, scanner, vendor de seguridad, proxy, investigador o usuario normal.

3. **Bifurcar la response.**
   El tráfico parecido a víctimas recibe el flujo real. El tráfico sospechoso recibe un redirect, página en blanco, página benigna, error o denegación por robots.

4. **Registrar y adaptar.**
   Los logs alimentan futuros blocklists, allowlists o reglas de targeting.

Tarjeta de evidencia defensiva:

```
same URL:
  residential browser -> login page
  cloud scanner       -> 403
  security vendor ASN -> news redirect
  curl User-Agent     -> access denied
```

El error no es la negociación de contenido. El error es usar la clasificación del visitante para ocultar comportamiento riesgoso de la validación.

## Técnicas / patrones

- Compará la misma URL desde diferentes puntos de vista: redes residenciales, cloud, VPN corporativa, móvil y lab controlado.
- Variá User-Agent, idioma, cookies, ejecución de JavaScript y proxy headers para ver si el contenido cambia.
- Buscá redirects benignos, 404s falsos, páginas en blanco, responses demoradas o páginas de "mantenimiento" que aparecen solo para clientes parecidos a scanners.
- Preservá hashes del body, screenshots, headers, detalles del certificado TLS y cadenas de redirect para cada punto de vista.
- Separar la regionalización legítima del branching evasivo preguntando si el comportamiento sensible aparece solo para visitantes seleccionados.
- Tratá los blocklists de vendors de seguridad, proveedores cloud y nombres de crawlers como indicadores fuertes de cloaking cuando se combinan con contenido riesgoso.

## Variantes y bypasses

El cloaking tiene **6 variantes reconocibles**.

### 1. Geo cloaking

El comportamiento cambia por país o región. Existe localización legítima, pero el phishing y el fraude suelen apuntar a una región mientras se ocultan de scanners extranjeros.

### 2. ASN / hosting cloaking

El tráfico de proveedores cloud, data centers, VPNs y vendors de seguridad recibe contenido inofensivo. El tráfico residencial o móvil ve el flujo real.

### 3. User-Agent cloaking

Los crawlers conocidos, herramientas de línea de comando, scanners o navegadores headless son bloqueados. Los strings tipo navegador reciben contenido diferente.

### 4. Reverse-DNS cloaking

Los hostnames PTR que contienen términos de vendor, cloud, crawler o seguridad son denegados. Es frágil pero común en kits más viejos.

### 5. Fingerprint cloaking

JavaScript, APIs del navegador, timing, storage o comportamiento de rendering distingue navegadores reales de la automatización.

### 6. Interaction cloaking

El comportamiento sospechoso aparece solo después de clicks, pasos de login, demoras, referrers, parámetros de link de email o campaign tokens.

## Impacto

- **Bypass de revisión de seguridad.** Los scanners automatizados o crawlers de vendors ven contenido benigno mientras las víctimas ven el payload real.
- **Longevidad del phishing.** Los pipelines de reporte y takedown reciben evidencia engañosa.
- **Control de entrega de malware.** Los operadores reducen la exposición a sandboxes e investigadores.
- **Targeting de fraude.** Las campañas se focalizan en regiones, dispositivos o poblaciones de cuentas específicas.
- **Falsa confianza defensiva.** Un scan limpio desde un punto de vista se confunde con comportamiento limpio en todos lados.

## Detección y defensa

Ordenado por efectividad:

1. **Testeá desde múltiples puntos de vista.**
   Una ruta de red no es suficiente. Compará rutas residencial, móvil, corporativa, cloud y scanner controlado para revelar bifurcaciones en las responses.

2. **Capturá evidencia completa de la response.**
   Registrá status, headers, redirects, hash del body, screenshot, respuesta DNS, certificado TLS y timing. El cloaking suele esconderse en diferencias pequeñas.

3. **Reproducí con cambios de señal controlados.**
   Cambiá una variable a la vez: User-Agent, cookie jar, idioma, red de origen, referrer, capacidad de JavaScript o campaign token.

4. **Monitoreá blocklists de vendors defensivos.**
   El código o config que nombra vendors de seguridad, crawlers, proveedores cloud o sistemas de threat-intel es evidencia de alta señal de intención de evasión.

5. **Instrumentá los paths reportados por usuarios reales.**
   Los reportes de usuarios reales deberían preservar la URL original, referrer, headers del email, dispositivo/navegador y timestamp. El path de la víctima puede ser el único que revela el contenido.

6. **Evitá asumir que el contenido benigno prueba seguridad.**
   Tratá las responses benignas como una observación desde un punto de vista. El hallazgo es el comportamiento diferencial, no solo el payload oculto.

### Qué no funciona como defensa primaria

- **Un solo scan.** El cloaking existe para hacer esa vista incompleta.
- **Solo testear desde infraestructura cloud.** Muchas reglas de cloaking bloquean específicamente data centers y vendors de seguridad.
- **Confiar en robots.txt.** No es control de acceso y puede ser parte de la superficie señuelo.
- **Ignorar redirects.** El objetivo del redirect puede ser la decisión de cloaking.
- **Llamar maliciosa a toda variación.** La localización, los A/B tests y los banners de cumplimiento también varían; la clave es el ocultamiento de seguridad relevante.

## Labs prácticos

### Comparar fingerprints de response

```
for ua in "curl/8.0" "Mozilla/5.0 Chrome/120 Safari/537.36" "Googlebot/2.1"; do
  curl -sk -A "$ua" -D "/tmp/headers-$ua.txt" -o "/tmp/body-$ua.html" https://example.test/
  shasum "/tmp/body-$ua.html"
done
```

Los hashes de body diferentes por User-Agent son un motivo para revisar, no una prueba por sí solos.

### Registrar una matriz de puntos de vista

```
url:
vantage | ip/asn type | user-agent | status | final-url | body-hash | screenshot | notes
home    | residential | browser    |        |           |           |            |
cloud   | hosting     | browser    |        |           |           |            |
mobile  | carrier     | browser    |        |           |           |            |
cloud   | hosting     | curl       |        |           |           |            |
```

La matriz revela si la misma URL se comporta como una aplicación o como varias.

### Verificar cloaking en redirects

```
curl -skIL https://example.test/path \
  -A "Mozilla/5.0 Chrome/120 Safari/537.36"
```

Comparar ubicaciones finales entre redes; los redirects aparentemente inofensivos pueden ser la bifurcación.

### Buscar vocabulario de cloaking en el código

```
rg -n "bot|crawler|spider|google|virustotal|phishtank|asn|isp|proxy|vpn|reverse|country|geo" .
```

En código propio, estos términos identifican dónde debería revisarse la clasificación y el branching de responses.

### Preservar el contexto del path de la víctima

```
reported URL:
timestamp:
source email/referrer:
device/browser:
network type:
redirect chain:
visible content:
comparison vantage:
```

Sin el path original, los defensores pueden ver solo el señuelo.

## Ejemplos prácticos

- Una página de phishing muestra un login falso solo a IPs de carriers móviles en un país y redirige a los scanners cloud a un sitio de noticias.
- Un link de descarga malicioso devuelve un PDF limpio a ASNs de vendors de seguridad y un payload a navegadores residenciales.
- Un scraper ignora `robots.txt` pero cambia User-Agent y rango de IP después de ser bloqueado.
- Un bot de zona gris bloquea monitores de uptime y scanners de seguridad mientras ataca inventario de checkout.
- Una campaña de fraude requiere un campaign token del link de email antes de mostrar la página real.

## Notas relacionadas

- [[bot-detection-signals|Señales de Detección de Bots]]
- [[recon|Recon]]
- [[active-recon|Active Recon]]
- [[http-headers|HTTP Headers]]
- [[browser-fingerprinting|Browser Fingerprinting]]
- [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS y Pipelines de Detección Conductual]]
- [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]]

## Referencias

- **Fundamental:** OWASP Automated Threats to Web Applications — https://owasp.org/www-project-automated-threats-to-web-applications/
- **Testing / Lab:** OWASP Web Security Testing Guide — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery reconnaissance deep dive — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
