# VPN Logging and Trust

## Definición

El logging y la confianza en VPN es el problema de decidir qué puede observar un proveedor de VPN, qué almacena, qué puede ser compelido a divulgar y si sus afirmaciones de privacidad están respaldadas por arquitectura y evidencia.

## Por qué importa

Un proveedor de VPN que dice "no logs" no es una garantía técnica por sí sola. Es una afirmación de confianza que debe evaluarse a través de arquitectura, auditorías, jurisdicción, historial e incentivos.

Las VPN a menudo reducen la visibilidad del ISP o la red local, pero concentran la visibilidad en el proveedor de VPN. Si el proveedor registra metadatos de conexión, identidad de pago, email de cuenta, IP de origen, IP de salida asignada o registros de abuso, el modelo de privacidad puede ser mucho más débil de lo que el usuario espera.

## Cómo funciona

Usá el modelo de 6 evidencias:

1.
**Afirmación**
   El proveedor dice qué registra o no.

2.
**Arquitectura**
   El diseño del servicio determina si se crean, centralizan, retienen o son técnicamente evitables los registros útiles.

3.
**Operaciones**
   Los flujos de soporte, manejo de abuso, facturación, monitoreo, reportes de crash y sistemas de fraude pueden crear registros fuera de la ruta del túnel.

4.
**Jurisdicción**
   El proveedor, el personal, los servidores, la empresa matriz, los procesadores de pago y los proveedores pueden estar sujetos a proceso legal.

5.
**Incentivos**
   El modelo de negocio de un proveedor afecta si recopilar, monetizar o compartir datos es tentador o necesario.

6.
**Historial**
   Las auditorías, registros judiciales, incidentes, cambios de propiedad y representaciones falsas previas importan más que los slogans.

Planilla de evidencia del proveedor:

```
Afirmación: no logs
Logs de conexión: sí/no/poco claro
Logs de tráfico: sí/no/poco claro
Logs de DNS: sí/no/poco claro
Email de cuenta: sí/no/poco claro
Metadatos de pago: sí/no/poco claro
Analytics de terceros: sí/no/poco claro
Auditoría independiente: fecha/alcance/¿pública?
Jurisdicción: proveedor/servidor/pago/proveedor
Infraestructura: propia/alquilada/solo RAM/poco claro
```

El bug no es confiar en un proveedor. El bug es no saber qué confianza le estás depositando.

## Técnicas / patrones

- Separar los logs de tráfico de los logs de conexión, logs de DNS, logs de cuenta, registros de pago y registros de soporte.
- Leer las políticas de privacidad sobre recopilación de datos, retención, pedidos legales, analytics y proveedores.
- Tratar las auditorías como evidencia con alcance, no como garantías permanentes.
- Verificar si la propiedad de la infraestructura y las afirmaciones de solo-RAM están claramente descritas.
- Identificar si la creación de cuenta, el pago, el referral, la telemetría de crash o los tickets de soporte crean rastros de identidad.
- Re-evaluar después de cambios de propiedad, rediseños de la app o nuevas jurisdicciones.

## Variantes y bypasses

Usá las 8 superficies de confianza:

### 1. Logs de tráfico

Los logs de tráfico describen la actividad de destino en detalle. Un proveedor que puede registrar destinos de navegación, consultas DNS o metadatos de payload puede convertirse en un punto de vigilancia de alto valor.

### 2. Logs de conexión

Los logs de conexión registran IP de origen, cuenta, tiempo de conexión, tiempo de desconexión, servidor asignado, IP de salida asignada, ancho de banda e identificadores de dispositivo. Pueden ser suficientes para correlación aunque no haya logs de tráfico completos.

### 3. Metadatos de cuenta

La dirección de email, nombre de usuario, cantidad de dispositivos, IDs de instalación de la app, códigos de referral, mensajes de soporte y canales de recuperación pueden identificar a un usuario.

### 4. Metadatos de pago

Tarjetas, PayPal, suscripciones de tiendas de apps, facturas, tarjetas de regalo y procesadores de pago crean registros de identidad. El pago alternativo reduce un vínculo pero no elimina la IP de origen ni los metadatos de cuenta.

### 5. Metadatos de infraestructura

Hosts cloud, servidores alquilados, proveedores de DNS, servicios de reportes de crash, SDKs de analytics y proveedores de monitoreo pueden crear registros fuera del control directo del proveedor de VPN.

### 6. Proceso legal

Los proveedores pueden recibir citaciones, órdenes de registro, órdenes de preservación, pedidos de seguridad nacional o pedidos de asistencia legal extranjera. La jurisdicción es multicapa, no solo la ubicación de la sede.

### 7. Alcance de la auditoría

Las auditorías pueden cubrir apps, infraestructura, configuración de logging, código fuente o solo una afirmación estrecha. Una auditoría desactualizada o estrecha es más débil que una auditoría reciente, pública, repetida con alcance claro.

### 8. Propiedad e incentivos

Las fusiones, empresas matrices, marketing de afiliados, niveles gratuitos, publicidad y liderazgo opaco pueden cambiar los incentivos después de que el usuario ya confió en el servicio.

## Impacto

- Correlación de cuenta VPN con IP de origen, identidad de pago y actividad de destino.
- Divulgación a través de registros del proveedor aunque el ISP tenga visibilidad limitada.
- Postura de privacidad engañosa cuando "no logs" excluye registros operacionales, de pago, de soporte o de abuso.
- Mayor riesgo de proveedores gratuitos u opacos cuyo modelo de negocio depende de monetizar datos.
- Falsa confianza durante flujos de trabajo sensibles que requieren mayor anonimato o compartimentación.

## Detección y defensa

Ordenado por efectividad:

1.
**Elegir el proveedor solo después de definir el threat model**
   Un proveedor adecuado para Wi-Fi hostil puede ser insuficiente para necesidades de anonimato sensibles. Si la confianza en el proveedor es inaceptable, Tor u otro flujo de trabajo puede ser más adecuado.

2.
**Preferir la arquitectura de minimización de datos**
   Los sistemas que no recopilan registros sensibles son más fuertes que las promesas de no hacer mal uso de ellos. Buscar límites claros de retención, requisitos mínimos de cuenta e infraestructura diseñada para reducir logs persistentes.

3.
**Leer cuidadosamente la política de privacidad y el material de transparencia**
   Buscar lenguaje específico sobre logs de conexión, logs de DNS, logs de tráfico, metadatos de pago, analytics, reportes de crash y pedidos legales. Las declaraciones vagas son evidencia débil.

4.
**Evaluar el alcance y la frescura de la auditoría**
   Las auditorías independientes ayudan cuando el alcance cubre la afirmación en la que se confía y el informe es suficientemente público para evaluar. Una auditoría antigua no garantiza el comportamiento actual.

5.
**Reducir la vinculación de cuenta y pago**
   Usar datos mínimos de cuenta donde sea apropiado y legal. Recordar que la minimización del pago no elimina la IP de origen ni la correlación de comportamiento.

6.
**Monitorear los cambios de propiedad y política**
   La confianza puede cambiar después de una adquisición, rediseño de la app, migración de infraestructura o actualización de política. Re-verificar los proveedores periódicamente.

### Qué no funciona como defensa primaria

- **Un slogan de no-log no es prueba.** Es una afirmación que necesita evidencia de respaldo.
- **La jurisdicción sola no es un análisis completo.** Los servidores, proveedores, procesadores de pago, personal y empresas matrices pueden crear otros vínculos legales.
- **Criptomonedas o tarjetas de regalo no hacen la VPN anónima.** La IP de origen, el comportamiento de la cuenta y los metadatos del proveedor pueden igualmente identificar o correlacionar actividad.
- **Una lista en una tienda de apps no es evidencia de confianza.** La disponibilidad en tiendas no prueba comportamiento que preserve la privacidad.
- **Una auditoría no es garantía permanente.** La arquitectura y las operaciones pueden cambiar después de la auditoría.

## Labs prácticos

### Construir una tarjeta de evidencia de confianza VPN

```
Proveedor:
Threat model:
Redacción exacta de la afirmación de no-log:
Logs de tráfico tratados:
Logs de conexión tratados:
Logs de DNS tratados:
Metadatos de cuenta tratados:
Metadatos de pago tratados:
Fecha y alcance de auditoría:
Jurisdicción:
Propiedad de infraestructura:
Incidentes conocidos:
Decisión:
```

El objetivo es hacer la decisión de confianza inspeccionable en lugar de basada en sensaciones.

### Buscar términos de log en una política de privacidad

```
rg -i 'log|metadata|dns|traffic|connection|retain|retention|payment|analytics|crash|law enforcement|subpoena|warrant' vpn-policy.md
```

Usar esto contra el texto de una política guardada. Los términos ambiguos deberían convertirse en preguntas, no en suposiciones.

### Comparar afirmaciones con la arquitectura

```
Afirmación: No guardamos logs.

Evidencia a buscar:
- cómo se manejan los reportes de abuso
- cómo se aplican los límites de cuenta
- cómo se aplican los límites de ancho de banda
- cómo se monitorea la salud del servidor
- cómo se recopilan los reportes de crash
- cómo se resuelve y registra el DNS
```

La comparación encuentra presión de logging operacional oculta.

### Registrar el alcance de la auditoría

```
Firma auditora:
Fecha:
Informe público disponible:
Apps cubiertas:
Infraestructura cubierta:
Logging del servidor cubierto:
Código fuente cubierto:
Pipeline de build cubierta:
Afirmaciones de política de privacidad cubiertas:
Limitaciones:
```

Una auditoría es útil solo para la afirmación y el período de tiempo que realmente cubre.

## Ejemplos prácticos

- Un proveedor afirma "no activity logs" pero aún mantiene timestamps de conexión e IPs de origen.
- Una cuenta VPN pagada a través de una tienda de apps vincula la suscripción a una identidad de plataforma.
- Un proveedor usa analytics de crash de terceros que recopilan identificadores de dispositivo o app.
- Un registro judicial muestra que un proveedor tenía registros a pesar del lenguaje de marketing que implicaba lo contrario.
- Una VPN corporativa registra identidad y acceso de destino intencionalmente porque el monitoreo es parte del control.

## Notas relacionadas

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-protocols|VPN Protocols]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[privacy-vs-anonymity-vs-confidentiality|Privacy vs Anonymity vs Confidentiality]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]

## Referencias

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
