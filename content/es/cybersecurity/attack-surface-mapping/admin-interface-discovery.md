# Admin Interface Discovery

## Definición

El admin interface discovery es el proceso de identificar interfaces de gestión, plano de control, soporte, diagnóstico o privilegiadas que deberían estar restringidas pero pueden seguir siendo alcanzables.

## Por qué importa

Las superficies admin exponen acciones de alto impacto: gestión de usuarios, impersonación, facturación, moderación de contenido, exportaciones, controles de debug, colas de jobs, deployments y estado de infraestructura. A menudo están "ocultas" en lugar de fuertemente aisladas, especialmente en staging, appliances de vendor, dashboards cloud y herramientas de soporte.

Mantené el scope acotado: esta nota es sobre descubrir superficies privilegiadas o del plano de control, no sobre el descubrimiento genérico de rutas en toda la aplicación.

## Cómo funciona

El descubrimiento admin sigue **4 pistas**:

1. **Nombres.** `admin`, `manage`, `console`, `support`, `ops`, `debug`, `internal`, `grafana`, `jenkins`, `kibana`.
2. **Funciones.** Exportar, impersonar, deshabilitar, aprobar, reembolsar, deployar, reiniciar, configurar, invitar, moderar.
3. **Productos.** Dashboards de vendor, appliances, paneles CMS, herramientas de observabilidad, CI/CD, consolas de base de datos.
4. **Contexto.** Hosts no productivos, puertos inusuales, virtual hosts alternativos, supuestos solo-internos y orígenes directos.

El bug no es que existan interfaces admin. El bug son las interfaces privilegiadas alcanzables fuera de su límite de confianza previsto o protegidas por controles más débiles de lo que su impacto requiere.

Un ejemplo trabajado, ruta oculta a decisión del plano de control:

```
Pista observada:
  el bundle JavaScript referencia "/support/impersonate"

Alcanzabilidad:
  la ruta existe en el host de producción

Resultado con usuario normal:
  403 sin cambio de estado

Resultado con usuario de soporte:
  200 con evento de auditoría

Decisión de límite:
  la función privilegiada es alcanzable desde internet pero la autorización backend y la auditoría parecen presentes;
  sigue necesitando revisión del propietario por MFA, antigüedad de sesión y controles del flujo de soporte
```

El hallazgo no es solo que la ruta existe. El hallazgo depende de la alcanzabilidad, el privilegio, la política y la evidencia de auditoría.

## Técnicas / patrones

Los profesionales buscan:

- subdominios admin y nombres de rutas riesgosos
- servicios HTTP de puerto alto y paneles por defecto
- strings de rutas JavaScript/admin
- funciones API con verbos privilegiados
- firmas de appliance de vendor
- hosts de staging y preview
- acceso a origen directo detrás de CDN/proxy
- mutations GraphQL y tags admin de OpenAPI

## Variantes y bypasses

La exposición admin aparece en **6 formas**.

### 1. Subdominio admin público

Un login o dashboard privilegiado es alcanzable desde internet.

### 2. Ruta privilegiada en host ordinario

La funcionalidad admin vive bajo hosts ordinarios en rutas ocultas.

### 3. Función admin como endpoint de API

Las funciones privilegiadas existen como rutas de API, mutations GraphQL o métodos RPC.

### 4. Appliances y productos de vendor

Los productos gestionados exponen superficies admin con modelos de parches y auth separados.

### 5. Admin de staging y preview

Los entornos no productivos exponen características admin con controles más débiles.

### 6. Endpoints de diagnóstico

Las rutas de health, métricas, debug, actuator o trace filtran o alteran el estado privilegiado.

## Impacto

Ordenado aproximadamente por severidad:

- **Control total de cuenta o tenant.** Los paneles admin pueden cambiar usuarios, roles, facturación o datos.
- **Control de infraestructura.** Las consolas CI/CD, de observabilidad y de appliance afectan sistemas de producción.
- **Exportaciones sensibles.** Las herramientas de soporte y admin a menudo exponen acceso amplio a datos.
- **Ruta BFLA.** Las funciones admin ocultas pueden ser invocables por usuarios con menor privilegio.
- **Reconocimiento y encadenamiento.** Las páginas admin revelan tecnologías, versiones, rutas y nombres internos.

## Detección y defensa

Ordenado por efectividad:

1.
**Inventariás interfaces privilegiadas explícitamente.**
   Las superficies admin merecen su propia clase de activo con propietarios, requisitos de auth, redes permitidas y cadencia de revisión.

2.
**Restringís la alcanzabilidad antes de confiar en la auth de la app.**
   La auth fuerte es necesaria, pero las interfaces admin también deberían estar detrás de VPN/zero-trust, redes privadas o política estricta del gateway cuando sea posible.

3.
**Enforzás autorización a nivel de función en cada acción privilegiada.**
   Ocultar la UI admin no es suficiente; el backend debe autorizar cada operación.

4.
**Separás los orígenes públicos y admin donde sea práctico.**
   Los límites claros reducen la exposición accidental y facilitan el monitoreo.

5.
**Monitoreás y alertás en rutas de acceso admin.**
   Los logins admin, intentos fallidos, IPs inusuales y acceso a origen directo deberían ser señales de alta prioridad.

### Qué no funciona como defensa primaria

- **Rutas admin oscuras.** Las wordlists, JS, docs y defaults de productos las revelan.
- **Chequeos de rol solo en frontend.** Los llamadores API directos pueden invocar funciones backend.
- **Supuestos solo-internos sin prueba de red.** Las rutas cloud y de proxy derivan.
- **Solo auth de usuario normal compartida.** Las acciones admin generalmente necesitan mayor aseguramiento y logging.

## Labs prácticos

Usá sistemas propios o apps de lab.

### Buscá rutas privilegiadas en el código

```
rg -i "admin|manage|console|support|ops|debug|internal|impersonate|export|approve" src routes public
```

Clasificá los resultados como orientado al usuario, privilegiado, de diagnóstico o desconocido.

### Sondeá rutas admin comunes

```
for p in admin manage console dashboard support debug actuator metrics; do
  curl -i "https://app.example.test/$p"
done
```

Registrá códigos de estado, redirecciones, comportamiento de auth y headers.

### Auditá puertos de dashboard comunes

```
nmap -sV -Pn -p 3000,5000,5601,8080,8081,9000,9090,9092 target.example.test
```

Los puertos de dashboard comunes merecen revisión del propietario.

### Testéa acceso no autorizado a funciones admin

```
curl -i -X POST -H "Authorization: Bearer $NORMAL" \
  https://api.example.test/admin/users/123/disable
```

El resultado correcto es una denegación confiable sin efectos secundarios.

### Construí una tabla de inventario de superficies admin

```
superficie | host/ruta | función | alcanzable desde | auth | MFA/antigüedad sesión | propietario | logs
```

Las interfaces admin deberían tener un inventario más fuerte que las rutas ordinarias del producto.

### Revisá endpoints de diagnóstico

```
for p in actuator env heapdump trace metrics debug; do
  curl -i "https://app.example.test/$p" | head -20
done
```

Los diagnósticos son adyacentes a admin cuando revelan secretos, topología o estado mutable.

## Ejemplos prácticos

- Una consola de gestión es alcanzable en un hostname olvidado.
- Un panel de soporte/debug queda expuesto después de troubleshooting de un incidente.
- Un appliance de vendor expone una interfaz admin pública.
- Una mutation GraphQL realiza acciones admin sin autorización del resolver.
- Un dashboard de staging usa credenciales compartidas.

## Notas relacionadas

- [[exposed-service-triage|Exposed Service Triage]]
- [[endpoint-discovery]]
- [[external-attack-surface]]
- [[broken-function-level-authorization|Broken Function Level Authorization]]
- [[broken-access-control|Broken Access Control]]

### Notas atómicas futuras sugeridas

- enumerate-admin-interfaces
- support-tool-authorization
- diagnostic-endpoint-exposure
- ci-cd-control-plane-exposure
- vendor-appliance-exposure

## Referencias

- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Docs Oficiales:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control
