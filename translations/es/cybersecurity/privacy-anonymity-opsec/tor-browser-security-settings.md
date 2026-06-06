# Tor Browser Security Settings

## Definición

Los ajustes de seguridad de Tor Browser son controles integrados que intercambian compatibilidad web por una superficie de ataque reducida y un comportamiento del browser que preserva más el anonimato.

## Por qué importa

Tor Browser es más que Firefox apuntando a Tor. Su valor proviene de la combinación de ruteo Tor, resistencia al fingerprinting del browser, aislamiento de estado, valores por defecto más seguros y niveles de seguridad que pueden deshabilitar funcionalidades web riesgosas.

Cambiar la configuración casualmente puede hacer que un usuario sea más único. El objetivo no es la máxima personalización; es mantenerse dentro de un gran conjunto de anonimato predecible mientras se eleva el nivel de seguridad cuando la actividad justifica el costo de usabilidad.

## Cómo funciona

Usá el modelo de 4 controles:

1.
**Nivel de seguridad**
   Standard, Safer y Safest deshabilitan progresivamente más funcionalidades web. Los niveles más altos pueden romper páginas pero reducen la exposición a funcionalidades del browser riesgosas.

2.
**Protecciones contra fingerprinting**
   Tor Browser intenta hacer que los usuarios se vean similares a través de defensas como el aislamiento de primera parte, el comportamiento del user agent y las protecciones del tamaño de ventana.

3.
**Gestión de identidad**
   Los controles Nueva Identidad y Nuevo Circuito Tor ayudan a separar la actividad, aunque no borran las decisiones de cuenta ya tomadas en un sitio.

4.
**Restricción de extensiones y plugins**
   Las extensiones y plugins pueden crear fingerprints únicos o eludir las protecciones de Tor Browser.

Tabla de decisión simple:

```
¿Necesito compatibilidad de navegación ordinaria?: Standard
¿Necesito superficie de ataque reducida de scripts/media/fuentes?: Safer
¿Necesito acceso a sitios estáticos/básicos con máxima reducción de funcionalidades del browser?: Safest
¿Necesito anonimato del destino?: evitar login de cuenta y personalización
```

El bug no es elegir Standard. El bug es asumir que Standard más comportamiento de cuenta inseguro es anonimato.

## Técnicas / patrones

- Usar los valores por defecto de Tor Browser a menos que un threat model exija un nivel de seguridad más alto.
- Preferir los cambios de nivel de seguridad sobre el hardening aleatorio de about:config.
- Evitar instalar extensiones de browser.
- Evitar redimensionar y personalizar de formas que hagan que el browser se destaque.
- Usar Nueva Identidad al moverse entre actividades no vinculables.
- Mantener la identidad de cuenta separada de la identidad de navegación.

## Variantes y bypasses

Usá las 5 clases de riesgo del browser:

### 1. Riesgo de scripts y contenido activo

JavaScript y las funcionalidades web ricas pueden aumentar la superficie de ataque y la superficie de fingerprinting. Los niveles de seguridad más altos reducen estas funcionalidades.

### 2. Riesgo de fuentes, media y renderizado

Las fuentes, íconos, media, símbolos matemáticos, canvas y las diferencias de renderizado pueden ayudar a hacer fingerprinting de un browser o exponer superficie de ataque.

### 3. Unicidad de extensiones

Las extensiones pueden añadir APIs, alterar páginas, filtrar datos o hacer que el fingerprint del browser sea inusual. El modelo de protección de Tor Browser asume una personalización mínima.

### 4. Fuga de estado de identidad

Las cookies, sesiones, logins y almacenamiento del sitio pueden vincular actividades. Los controles del browser ayudan, pero hacer login en una cuenta identificadora aún identifica al usuario ante ese servicio.

### 5. Fuga de aplicación externa

Abrir archivos descargados en apps externas puede eludir Tor Browser y exponer señales de red, metadatos o del dispositivo local.

## Impacto

- Superficie de exploit y fingerprinting del browser reducida en niveles de seguridad más altos.
- Menor usabilidad en sitios dinámicos cuando se deshabilitan funcionalidades riesgosas.
- Mejor compartimentación cuando se usa Nueva Identidad correctamente.
- Riesgo de desanonimización cuando los usuarios personalizan el browser, instalan extensiones o hacen login en cuentas identificadoras.
- Riesgo de cruce de límite por archivos descargados y aplicaciones auxiliares.

## Detección y defensa

Ordenado por efectividad:

1.
**Mantener Tor Browser cerca de los valores por defecto**
   Los valores por defecto están diseñados para un conjunto de anonimato compartido. La configuración personalizada única puede debilitar el anonimato aunque se sienta más segura.

2.
**Elevar el nivel de seguridad según el riesgo de la actividad**
   Safer y Safest reducen las funcionalidades del browser expuestas. Usarlos cuando la consecuencia de la explotación del browser o el fingerprinting supera la compatibilidad del sitio.

3.
**Evitar extensiones y plugins**
   Las extensiones son de alto riesgo porque cambian el comportamiento del browser y pueden crear fingerprints únicos o filtrar datos.

4.
**Usar Nueva Identidad para la separación de actividades**
   Nueva Identidad ayuda a resetear el estado entre actividades no relacionadas. No hace anónima una cuenta con login.

5.
**Tratar las descargas como cruces de límite**
   Inspeccionar, aislar o evitar archivos que necesiten aplicaciones externas. Las apps externas pueden conectarse fuera de Tor o revelar metadatos.

6.
**No perseguir puntajes de test de fingerprint haciendo ajustes**
   Los cambios aleatorios pueden hacer que el browser sea más único. La consistencia con la población de Tor Browser es generalmente el punto.

### Qué no funciona como defensa primaria

- **El hardening personalizado no es automáticamente mejor.** La configuración única puede crear un fingerprint distintivo.
- **Las extensiones no son inocuas.** Incluso las extensiones de privacidad pueden alterar el fingerprint y el comportamiento.
- **Nueva Identidad no anonimiza los logins con nombre real.** El servicio aún conoce la cuenta.
- **Un nivel de seguridad más alto no arregla los errores OPSEC.** Los archivos, cuentas, comportamiento y compromiso del endpoint persisten.

## Labs prácticos

### Registrar la decisión de nivel de seguridad

```
Actividad:
Consecuencia si el browser es explotado:
¿Necesita sitios con mucho JavaScript?:
¿Necesita media/fuentes?:
Nivel elegido: Standard / Safer / Safest
Razón:
Re-testear si hay rotura:
```

El resultado vincula la configuración al riesgo en lugar de a la superstición.

### Comparar el comportamiento del sitio entre niveles

```
Sitio:
Standard funciona:
Safer funciona:
Safest funciona:
Funcionalidades rotas:
¿El beneficio de seguridad vale la rotura?:
```

Usar solo sitios a los que tenés permitido acceder. El punto es aprender el balance de compatibilidad.

### Verificar la disciplina de extensiones

```
Extensiones instaladas:
Por qué se necesita cada una:
¿Podría alterar el fingerprint?:
¿Podría leer páginas?:
¿Podría hacer requests de red?:
Decisión:
```

La mayoría de los flujos de trabajo de Tor Browser no deberían tener extensiones adicionales.

### Planificar la separación de identidad

```
Actividad A:
Actividad B:
¿Misma cuenta? sí/no
¿Mismo sitio? sí/no
¿Necesitar Nueva Identidad entre ellas? sí/no
¿Archivos descargados? sí/no
¿Apps externas abiertas? sí/no
```

Esto distingue la separación de estado del browser de la separación de cuenta.

## Ejemplos prácticos

- Un usuario pasa de Standard a Safer para investigación sensible que solo necesita páginas simples.
- Un sitio se rompe bajo Safest porque los scripts están deshabilitados; el usuario documenta el balance de compatibilidad.
- Un usuario instala una extensión de gestor de contraseñas y se vuelve más huella-imprimible.
- Un usuario abre un documento descargado en un lector PDF normal, cruzando fuera del modelo de protección de Tor Browser.
- Un usuario usa Nueva Identidad entre tareas de investigación no relacionadas pero evita hacer login en cuentas identificadoras.

## Notas relacionadas

- [[tor-and-onion-services|Tor and Onion Services]]
- [[vpn-vs-tor|VPN vs Tor]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[content-security-policy|Content Security Policy]]

## Referencias

- **Docs Oficiales:** Tor Browser Security Levels - https://support.torproject.org/tor-browser/features/security-levels/
- **Docs Oficiales:** Tor Browser Fingerprinting Protections - https://support.torproject.org/tor-browser/features/fingerprinting-protections/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
