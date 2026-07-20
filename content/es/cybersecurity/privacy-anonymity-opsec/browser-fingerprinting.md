# Browser Fingerprinting

## Definición

El browser fingerprinting es la identificación o correlación de un browser a través de características estables como user agent, fuentes, extensiones, comportamiento de renderizado, tamaño de pantalla, timezone, idioma y soporte de funcionalidades.

## Por qué importa

Cambiar la dirección IP no cambia el browser. Los sitios pueden correlacionar usuarios a través de características a nivel de aplicación aunque una VPN o Tor cambie la ruta de red.

## Cómo funciona

Usá el modelo de browser de 5 señales:

1.
**Identidad declarada**
   User agent y hints de plataforma.

2.
**Identidad de renderizado**
   Canvas, WebGL, fuentes, comportamiento CSS y peculiaridades de layout.

3.
**Identidad de entorno**
   Tamaño de pantalla, timezone, idioma, funcionalidades de hardware y comportamiento del SO.

4.
**Identidad de estado**
   Cookies, local storage, historial y estado de login.

5.
**Identidad de comportamiento**
   Cómo se usa el browser y qué páginas o acciones aparecen.

El bug no es que los browsers puedan identificarse. El bug es pretender que el enmascaramiento de IP resuelve la unicidad del browser.

## Técnicas / patrones

- Reducir las personalizaciones del browser cuando el anonimato importa.
- Preferir browsers anti-fingerprinting para uso sensible.
- Mantener los perfiles separados.
- Evitar plugins y extensiones que cambien el comportamiento del browser.
- Testear las superficies de fingerprint después de actualizaciones.
- Separar la identidad del browser de la identidad de cuenta.

## Variantes y bypasses

Usá los 6 vectores de fingerprint:

### 1. Headers y user agent

Declaraciones básicas del browser y el SO.

### 2. Superficies de renderizado

Canvas, WebGL, fuentes, media, CSS y timing.

### 3. Huella de extensiones

Las extensiones instaladas pueden ser altamente identificadoras.

### 4. Forma de ventana y dispositivo

Tamaño de pantalla, DPI, soporte táctil y hints de hardware.

### 5. Estado de almacenamiento

Cookies, local storage y estado de sesión vinculan visitas.

### 6. Patrones de comportamiento

Cómo se usa el browser puede ser tan identificador como las propiedades estáticas.

## Impacto

- Correlación entre sesiones y sitios.
- Anonimato degradado aunque la privacidad de transporte sea fuerte.
- Rastreo del lado del sitio que sobrevive a los cambios de IP.
- Mayor unicidad por personalización excesiva.
- Falsa confianza al usar un browser normal a través de una VPN.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar browsers anti-fingerprinting para tareas de anonimato**
   Tor Browser está diseñado para reducir la unicidad.

2.
**Mantener los browsers aburridos**
   Menos extensiones y menos ajustes personalizados generalmente significan menos fingerprints.

3.
**Separar identidades por perfil de browser**
   Un perfil no debería contener múltiples personas.

4.
**Limitar el estado de almacenamiento**
   Borrar o evitar cookies y almacenamiento del sitio cuando la unlinkability importa.

5.
**Retestear regularmente**
   Las actualizaciones del browser y el SO pueden cambiar el fingerprint.

### Qué no funciona como defensa primaria

- **Una VPN no detiene el browser fingerprinting.**
- **El modo privado no es una defensa contra el fingerprinting.**
- **Más extensiones suelen ser peor, no mejor.**
- **Las personalizaciones aleatorias pueden hacer que el browser sea más único.**

## Labs prácticos

### Hacer inventario de las superficies de fingerprint

```
Browser:
Perfil:
User agent:
Timezone:
Idioma:
Extensiones:
Fuentes:
Tamaño de pantalla:
Cookies:
Estado de login:
```

Esto muestra cuánto es visible antes de cualquier request de red.

### Comparar perfiles

```
Browser diario:
Perfil limpio:
Browser anti-fingerprinting:

Diferencias:
- extensiones
- estado de almacenamiento
- personalización
- estado de login
```

Esto hace que la unicidad del browser sea más fácil de ver.

### Revisar el riesgo de extensiones

```
Extensión:
Necesaria:
¿Cambia páginas?:
¿Lee contenido de página?:
¿Crea comportamiento único?:
Conservar o eliminar:
```

Las extensiones son a menudo la forma más rápida de destacarse.

### Verificar después de actualización

```
Actualización:
Qué cambió:
Resultado del sitio de fingerprint:
¿Nueva unicidad?
```

El retesteo post-actualización debería ser rutinario.

## Ejemplos prácticos

- Un usuario de Tor Browser evita extensiones adicionales para mantenerse en el conjunto de anonimato compartido.
- Un browser normal a través de una VPN sigue revelando el mismo conjunto de extensiones y tamaño de ventana.
- Un paquete de fuentes personalizado hace que un browser sea más fácil de identificar.
- Un sitio reutiliza cookies aunque la dirección IP haya cambiado.
- Un perfil de browser dedicado a una persona evita la vinculación cruzada.

## Notas relacionadas

- [[vpn-fingerprinting-limitations|VPN Fingerprinting Limitations]]
- [[tor-browser-security-settings|Tor Browser Security Settings]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[session-management|Session Management]]

## Referencias

- **Docs Oficiales:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
