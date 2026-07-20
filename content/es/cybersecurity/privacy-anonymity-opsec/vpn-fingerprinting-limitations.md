# VPN Fingerprinting Limitations

## Definición

Las limitaciones de fingerprinting de VPN son las razones por las que una VPN no puede detener el fingerprinting del browser, cuenta, dispositivo y comportamiento aunque la visibilidad de la ruta de red cambie.

## Por qué importa

Una VPN puede ocultar la IP real del usuario a un sitio web, pero el sitio aún puede hacer fingerprinting del browser, rastrear cookies, correlacionar el comportamiento de login y comparar el estado del dispositivo y la cuenta. La dirección IP es solo una señal entre muchas.

## Cómo funciona

Usá el modelo de 5 señales:

1.
**Señal de red**
   La VPN cambia la IP de origen y a menudo cambia la ubicación aproximada.

2.
**Señal del browser**
   El user agent, fuentes, extensiones, canvas, WebGL, tamaño de pantalla, timezone e idioma persisten.

3.
**Señal de cuenta**
   Hacer login en la misma cuenta vincula las sesiones directamente.

4.
**Señal de comportamiento**
   El timing, clics, estilo de escritura, secuencia de búsqueda y hábitos de navegación siguen siendo observables.

5.
**Señal del dispositivo**
   La versión del SO, clase del dispositivo, software instalado y comportamiento del hardware pueden aún identificar al usuario.

El bug no es que exista el fingerprinting. El bug es creer que una VPN borra la superficie de fingerprinting.

## Técnicas / patrones

- Separar el ocultamiento de IP de la identidad del browser.
- Usar compartimentación del browser cuando la separación de identidad importa.
- Evitar el login en sesiones que deben mantenerse no vinculables.
- Tratar timezone, idioma y tamaño de ventana como señales de identidad.
- Preferir browsers anti-fingerprinting para tareas de anonimato.
- Re-testear después de actualizaciones del browser y del SO.

## Variantes y bypasses

Usá los 6 casos de fingerprinting:

### 1. Rotación de IP

Cambiar las salidas de la VPN ayuda contra el rastreo de IP aproximado pero no contra el rastreo de browser o cuenta.

### 2. Correlación por cookies y sesión

Las cookies persistentes y las sesiones con login pueden identificar completamente a un usuario independientemente de la IP.

### 3. Unicidad del browser

Las extensiones, fuentes y configuraciones inusuales hacen que un browser se destaque aunque la IP cambie.

### 4. Unicidad a nivel de dispositivo

Los fingerprints de SO y hardware pueden persistir entre cambios de VPN.

### 5. Fingerprinting de comportamiento

Los patrones repetidos entre sesiones pueden identificar al mismo operador.

### 6. Correlación entre servicios

El mismo login o estilo de escritura entre servicios puede conectar los puntos aunque cada sitio solo vea una IP de VPN.

## Impacto

- La salida de la VPN ya no define el límite de identidad.
- Los sitios web aún pueden rastrear usuarios a través del estado del browser y la cuenta.
- La investigación sensible puede vincularse a través de señales de comportamiento y dispositivo.
- La confianza en privacidad se vuelve demasiado dependiente de la rotación de IP.
- Las protecciones al estilo de Tor Browser siguen siendo relevantes aunque haya una VPN presente.

## Detección y defensa

Ordenado por efectividad:

1.
**Tratar la IP como solo una señal**
   Una VPN solo cambia una parte del modelo de rastreo. El resto debe gestionarse por separado.

2.
**Usar browsers y cuentas compartimentados**
   Si la unlinkability importa, no reutilices el mismo perfil de browser ni conjunto de cuentas.

3.
**Preferir browsers anti-fingerprinting para tareas sensibles**
   Tor Browser está diseñado para reducir la unicidad; los browsers normales no lo están.

4.
**Reducir personalizaciones**
   Los ajustes aleatorios de privacidad pueden hacer que un browser sea más único, no menos.

5.
**Testear desde el flujo de trabajo real**
   El browser, cuenta y dispositivo usados en la tarea real son lo que importa.

### Qué no funciona como defensa primaria

- **La rotación de IP de VPN no es anti-rastreo.**
- **El modo de navegación privada no borra los fingerprints.**
- **Cambiar de país no elimina la unicidad del dispositivo o del comportamiento.**
- **Una cuenta con login sigue siendo identificable independientemente de la VPN.**

## Labs prácticos

### Registrar señales de fingerprint visibles

```
Sitio:
Salida VPN:
Perfil de browser:
User agent:
Timezone:
Idioma:
Tamaño de pantalla:
Extensiones:
Con login:
Cuenta usada:
```

El objetivo es ver que la VPN es solo una fila en la tabla.

### Comparar perfiles

```
Perfil A: browser diario
Perfil B: browser limpio
Perfil C: browser anti-fingerprinting

Comparar:
- extensiones
- fuentes
- timezone
- estado de login
- estado de cookies
```

Esto muestra cuánta identidad vive fuera de la VPN.

### Verificar la correlación de login

```
Login sitio A:
Login sitio B:
¿Mismo email?
¿Mismos datos de recuperación?
¿Mismo método de pago?
¿Mismo dispositivo?
¿Mismo perfil de browser?
```

La VPN no cambia estos vínculos.

### Re-testear después de actualizaciones

```
Actualización del browser:
Actualización del SO:
Actualización del cliente VPN:
Nuevo resultado del sitio de fingerprint:
Deriva notable:
```

La postura de fingerprinting cambia con el tiempo.

## Ejemplos prácticos

- Un usuario cambia el país de VPN pero sigue siendo rastreable porque el perfil del browser no ha cambiado.
- Un sitio de compras vincula sesiones a través de cookies y un login de cuenta.
- Una extensión de privacidad hace que el browser sea más inusual en lugar de menos.
- Un flujo de trabajo de investigación usa Tor Browser porque la necesidad de anonimato es más amplia que el enmascaramiento de IP.
- Una VPN corporativa oculta la ruta de red pero no la identidad del empleado ante el servicio de destino.

## Notas relacionadas

- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[privacy-vs-anonymity-vs-confidentiality|Privacy vs Anonymity vs Confidentiality]]
- [[tor-browser-security-settings|Tor Browser Security Settings]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[session-management|Session Management]]

## Referencias

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Docs Oficiales:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
