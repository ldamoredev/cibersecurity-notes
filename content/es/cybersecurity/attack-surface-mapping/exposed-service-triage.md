# Exposed Service Triage

## Definición

El exposed service triage es el proceso de convertir servicios de red descubiertos en decisiones de seguridad: superficie pública esperada, puerta lateral no documentada, ruta admin olvidada, acceso remoto riesgoso o deriva que necesita retiro.

## Por qué importa

Encontrar un puerto abierto es solo el comienzo. El valor de seguridad viene de decidir qué significa la exposición. Un `443` público puede ser esperado, mientras que un `22`, `3389`, puerto de base de datos, appliance de vendor o consola de gestión sin rastrear puede ser el hallazgo real.

Esta nota se mantiene enfocada en ownership, significado de exposición y priorización. [[service-enumeration|Service Enumeration]] es propietaria de la mecánica de protocolo y banner.

## Cómo funciona

El triaje tiene **5 preguntas**:

1. **¿Qué está escuchando?** Protocolo, producto, versión, certificado TLS, virtual host y comportamiento.
2. **¿Desde dónde es alcanzable?** Internet público, VPN, workload cloud, partner o segmento interno.
3. **¿Es esperado?** Superficie del producto, superficie admin, compatibilidad legacy, entorno temporal o desconocido.
4. **¿Qué privilegio o datos expone?** Fortaleza de auth, poder del plano de control, datos de tenant o secretos.
5. **¿Quién tiene la decisión?** Equipo, vendor, entorno, plan de descomisionamiento o ruta de escalación.

El bug no es "un puerto está abierto". El bug es servicio abierto más ownership débil, controles débiles, alto privilegio, datos sensibles o alcanzabilidad inesperada.

Un ejemplo de triaje trabajado:

```
Hallazgo:
  203.0.113.42:8443 sirve "Jenkins"

Pregunta 1, ¿qué está escuchando?
  consola web de Jenkins sobre TLS

Pregunta 2, ¿desde dónde es alcanzable?
  internet público, no solo VPN

Pregunta 3, ¿es esperado?
  no está en el inventario de activos públicos

Pregunta 4, ¿privilegio/datos?
  jobs de build, variables de entorno, posibles credenciales de deployment

Pregunta 5, ¿propietario?
  equipo de platform, pero el tag del host dice "migration-2024"

Triaje:
  exposición directa del plano de control de alta prioridad, no meramente "8443 abierto"
```

Un buen triaje convierte una fila del escáner en una decisión de propietario/acción.

## Técnicas / patrones

Los profesionales buscan:

- puertos no estándar y puertos de gestión
- servicios HTTP en puertos altos
- SSH, RDP, VPN, base de datos, caché, cola y protocolos admin
- páginas por defecto, indicadores de credenciales por defecto y banners de appliance
- certificados TLS que revelan hostnames o vendors
- servicios alcanzables directamente sin supuestos de CDN/proxy
- servicios de staging y temporales con datos de producción

## Variantes y bypasses

Los servicios expuestos caen en **6 clases de triaje**.

### 1. Superficie esperada y controlada

Exposición pública HTTP/API/correo/DNS/servicio que coincide con el inventario y tiene controles normales.

### 2. Acceso remoto expuesto

SSH, RDP, VPN u otros protocolos de gestión que quedaron públicos después de una migración o troubleshooting.

### 3. Origen directo expuesto

Los orígenes backend son alcanzables sin el CDN, WAF o reverse proxy previstos.

### 4. Servicios de datos expuestos

Bases de datos, cachés, colas, clusters de búsqueda o servicios de objetos alcanzables fuera de su límite de confianza.

### 5. Surfaces de appliance y de vendor

Dispositivos gestionados, dashboards y productos de terceros exponen el comportamiento del plano de control.

### 6. Servicios legados y olvidados

Versiones viejas, servicios beta, migraciones o herramientas de response a incidentes permanecen alcanzables.

## Impacto

Ordenado aproximadamente por severidad:

- **Acceso inicial.** El acceso remoto, admin o servicio explotable se convierte en el punto de entrada.
- **Exposición de datos.** Las bases de datos, búsqueda, almacenamiento o dashboards filtran información sensible.
- **Bypass de edge.** Los orígenes directos saltan la autenticación o el filtrado CDN/WAF/proxy.
- **Escalación de privilegios.** Los servicios de gestión exponen acciones poderosas.
- **Brecha de parches.** Los servicios desconocidos se retrasan respecto a la gestión de vulnerabilidades actual.

## Detección y defensa

Ordenado por efectividad:

1.
**Mantenés un inventario de servicios con exposición esperada y propietarios.**
   Cada servicio alcanzable debería mapearse a un propósito, propietario, entorno y fuente permitida.

2.
**Reducís la alcanzabilidad pública para servicios de gestión y datos.**
   Los servicios admin, base de datos, caché, cola y de acceso remoto raramente deberían estar expuestos a internet.

3.
**Validás la alcanzabilidad de origen directo y puerto alternativo.**
   Si un servicio solo debería ser alcanzable a través de un proxy/CDN, testéa que el origen rechaza el tráfico directo.

4.
**Requerís autenticación fuerte y ownership de parches.**
   La reducción de exposición es lo mejor, pero los servicios restantes necesitan MFA, claves, least privilege, versiones actuales y logging.

5.
**Triás por impacto, no por novedad.**
   Un aburrido almacenamiento expuesto o panel admin a menudo importa más que un protocolo exótico de bajo impacto.

### Qué no funciona como defensa primaria

- **Confiar en puertos inusuales.** Los escáneres y los logs de certificados los encuentran.
- **Banners ocultos pero servicios abiertos.** El comportamiento del protocolo a menudo revela suficiente.
- **Asumir que los security groups cloud se autodocumentan.** Las reglas necesitan propietario y propósito.
- **Poner un WAF delante mientras el origen permanece alcanzable.** El acceso directo al origen bypasea el control.

## Labs prácticos

Usá solo sistemas propios.

### Escaneá y clasificá servicios

```
nmap -sV -Pn --open -p 1-10000 target.example.test
```

Convertí los servicios abiertos en esperados, inesperados, desconocidos y candidatos a retiro.

### Sondeá puertos HTTP de alto rango

```
for p in 8080 8081 8443 9000 9090; do
  curl -k -i "https://target.example.test:$p/" | head
done
```

Buscá paneles admin, páginas por defecto y apps alternativas.

### Revisá los certificados TLS

```
openssl s_client -connect target.example.test:443 -servername target.example.test </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -ext subjectAltName
```

Los certificados a menudo revelan nombres internos, vendors o hosts alternativos.

### Testéa la alcanzabilidad de origen directo

```
curl -i --resolve app.example.test:443:203.0.113.10 https://app.example.test/
```

El origen no debería servir tráfico normal si se requiere mediación CDN/proxy.

### Construí una tabla de triaje de servicios

```
host | puerto | servicio | alcanzable desde | ¿esperado? | propietario | clase | próxima acción
```

Usá las clases de triaje de esta nota en lugar de tratar cada puerto abierto de igual manera.

### Auditá el acceso remoto

```
nmap -sV -Pn -p 22,3389,5900,5985,5986 target.example.test
```

La administración remota merece restricciones de fuente, controles MFA o de clave, y confirmación de propietario.

## Ejemplos prácticos

- Un host expone HTTPS y un servicio SSH sin rastrear.
- Un reverse proxy público filtra virtual hosts alternativos.
- Una base de datos supuestamente interna responde externamente en un puerto alto.
- Un origen CDN acepta tráfico directamente.
- Un appliance de vendor expone una página de login de gestión.

## Notas relacionadas

- [[ports-and-services|Ports and Services]]
- [[service-enumeration|Service Enumeration]]
- [[external-attack-surface]]
- [[admin-interface-discovery]]
- [[active-recon|Active Recon]]

### Notas atómicas futuras sugeridas

- direct-origin-exposure
- remote-access-exposure
- database-exposure
- appliance-admin-surfaces
- service-owner-triage

## Referencias

- **Docs Oficiales:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
