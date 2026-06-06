# VPN DNS and IPv6 Leaks

## Definición

Las fugas de DNS e IPv6 de VPN ocurren cuando las búsquedas de dominio o el tráfico IPv6 salen por una ruta diferente a la ruta VPN prevista, exponiendo metadatos a un ISP, red local, empleador o servicio de destino.

## Por qué importa

DNS e IPv6 son lugares comunes donde "VPN conectada" y "ruta de privacidad contenida" divergen. Un usuario puede ver la IP de salida de la VPN en un test del browser mientras las consultas DNS todavía van al resolver local o el tráfico IPv6 todavía usa la interfaz normal.

El propósito del testing de fugas DNS es verificar si las búsquedas de dominio están saliendo por la ruta del resolver prevista.

## Cómo funciona

Usá el modelo de 4 rutas:

1.
**La aplicación pide un nombre**
   El browser, app o SO necesita resolver un dominio.

2.
**Se toma la decisión del resolver**
   El request puede ir al resolver del proveedor de VPN, un resolver de la red local, un resolver del ISP, DNS-over-HTTPS del browser, un resolver corporativo o un resolver configurado manualmente.

3.
**Se selecciona la familia de direcciones**
   El destino puede tener registros IPv4, registros IPv6 o ambos. El SO y la app deciden qué familia de direcciones usar.

4.
**El tráfico se envía por una ruta**
   IPv4 e IPv6 pueden tener diferentes tablas de rutas. Uno puede usar la VPN mientras el otro usa la red normal.

Ejemplo de desajuste:

```
App VPN: conectada
Ruta IPv4: túnel VPN
Resolver DNS: resolver del ISP
Ruta IPv6: interfaz Wi-Fi normal

Resultado:
  El sitio web puede ver IPv4 de la VPN para parte del tráfico, mientras DNS o IPv6 exponen la red original.
```

El bug no es "existe DNS". El bug es el desajuste no resuelto entre la resolución de nombres, la familia de direcciones y la política de ruteo.

## Técnicas / patrones

- Testear DNS por separado de la IP visible.
- Testear IPv4 e IPv6 por separado.
- Verificar si el proveedor de VPN soporta IPv6 o lo deshabilita de forma segura.
- Revisar el comportamiento de DNS-over-HTTPS del browser.
- Comparar la configuración del resolver del SO antes y después de la conexión VPN.
- Testear desde cada app que importa, no solo desde un browser.
- Re-testear después de actualizaciones del SO, del browser, del cliente VPN y cambios de red.

## Variantes y bypasses

Usá las 6 formas de fuga:

### 1. Fuga DNS del ISP

La VPN rutea el tráfico web, pero los requests DNS aún van al resolver del ISP. El ISP puede conocer las búsquedas de dominio aunque no vea el contenido de las páginas.

### 2. Fuga DNS de la red local

Un resolver del hotel, oficina, escuela o café maneja las búsquedas. Esto puede exponer los dominios al operador de la red y también puede permitir filtrado o manipulación local.

### 3. Desajuste de DNS-over-HTTPS del browser

El browser usa su propio proveedor de DNS cifrado. Esto puede mejorar la confidentiality de la red local pero puede eludir la ruta del resolver prevista del proveedor de VPN y crear un nuevo punto de confianza.

### 4. Desajuste de soporte IPv6

La VPN solo maneja IPv4. Si IPv6 sigue habilitado y ruteado fuera del túnel, los destinos de doble stack pueden exponer la red normal del usuario.

### 5. Fuga de DNS dividido y resolver corporativo

Las VPN corporativas pueden enviar intencionalmente nombres internos al DNS corporativo y nombres públicos a otro lado. La mala configuración puede filtrar nombres de host internos o enviar metadatos de navegación pública a la infraestructura corporativa.

### 6. Fuga en portal cautivo y reconexión

Antes de que la VPN se conecte, después de sleep/wake o durante el login en el portal cautivo, el comportamiento de DNS e IPv6 puede usar brevemente la red local.

## Impacto

- Visibilidad del ISP o red local sobre las búsquedas de dominio.
- Exposición de la red real a través de IPv6 mientras IPv4 parece protegido.
- Resolvers corporativos o locales viendo más metadatos de navegación de lo previsto.
- Conclusiones incorrectas del test de fugas cuando solo se verifica el IPv4 visible.
- Desanonimización o inferencia de ubicación a través de metadatos del resolver y la familia de direcciones.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar un cliente VPN que maneje explícitamente DNS e IPv6**
   El cliente debería configurar el comportamiento del resolver, rutear las familias de direcciones intencionalmente y fallar de forma cerrada donde no sea soportado.

2.
**Forzar el DNS a través de la ruta prevista**
   Decidir si el DNS debería usar el proveedor de VPN, un resolver cifrado de confianza o un resolver corporativo. Luego testear que el resolver real coincida con la decisión.

3.
**Rutear o deshabilitar IPv6 intencionalmente**
   Si la VPN soporta IPv6, verificarlo. Si no, deshabilitar IPv6 para el flujo de trabajo o usar reglas de firewall para bloquear el fallback de IPv6.

4.
**Verificar el comportamiento de DNS del browser**
   El DNS-over-HTTPS del browser puede eludir las expectativas del SO. Alinear la configuración del browser con el threat model.

5.
**Re-testear después de transiciones de red**
   Sleep/wake, cambios de Wi-Fi, portales cautivos y reconexiones son donde las configuraciones aparentemente limpias suelen filtrar.

6.
**Documentar las reglas de DNS dividido**
   En entornos corporativos, el DNS dividido debería ser esperado y auditable, no un comportamiento misterioso.

### Qué no funciona como defensa primaria

- **Verificar solo IPv4 es incompleto.** IPv6 puede seguir una ruta diferente.
- **Verificar solo la IP del browser es incompleto.** El DNS puede filtrar aunque el browser parezca usar la salida de la VPN.
- **El DNS cifrado no es automáticamente la ruta del resolver correcta.** Cambia quién ve las consultas; no elimina la confianza.
- **Deshabilitar IPv6 en todas partes sin documentarlo es frágil.** Puede romper apps y ocultar la necesidad de soporte IPv6 adecuado.

## Labs prácticos

### Capturar IPv4 e IPv6 visibles

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
```

Registrar ambos antes y después de la conexión VPN. Tratar la falla de conexión sobre IPv6 como un resultado a interpretar, no como éxito automático.

### Consultar la identidad del resolver

```
dig o-o.myaddr.l.google.com TXT @ns1.google.com
dig whoami.cloudflare @1.1.1.1
```

Comparar el output entre la red normal, VPN conectada y estados de DNS-over-HTTPS del browser.

### Inspeccionar la configuración del resolver del SO

```
scutil --dns | sed -n '1,160p'
```

En macOS, comparar las entradas del resolver antes y después de conectar la VPN.

### Inspeccionar las tablas de rutas

```
netstat -rn -f inet
netstat -rn -f inet6
```

Las tablas de rutas IPv4 e IPv6 pueden contar historias diferentes.

### Testear después de sleep/wake o cambio de red

```
1. Conectar VPN.
2. Registrar IPv4, IPv6 y DNS.
3. Poner el dispositivo en sleep o cambiar Wi-Fi.
4. Esperar la reconexión.
5. Repetir verificaciones de IPv4, IPv6 y DNS.
6. Registrar cualquier ruta de fallback.
```

El caso de reconexión es donde el comportamiento del kill switch y del resolver se vuelven visibles.

## Ejemplos prácticos

- Un cliente VPN configura rutas IPv4 pero deja el tráfico IPv6 en la interfaz Wi-Fi.
- Un browser usa DNS-over-HTTPS hacia un tercero mientras la VPN espera el DNS del proveedor.
- Una VPN corporativa envía nombres de host internos al DNS de la empresa y dominios públicos al DNS local.
- Un dispositivo móvil filtra DNS durante sleep/wake antes de que la VPN se reconecte.
- Un usuario solo valida `curl -4` y no detecta la exposición de doble stack.

## Notas relacionadas

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[vpn-protocols|VPN Protocols]]
- [[dns-resolution|DNS Resolution]]
- [[dns-security|DNS Security]]

## Referencias

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Fundamental:** [[dns-resolution|DNS Resolution]]
- **Fundamental:** [[dns-security|DNS Security]]
- **Docs Oficiales:** Tor Browser User Manual: Secure Connections - https://tb-manual.torproject.org/secure-connections/
