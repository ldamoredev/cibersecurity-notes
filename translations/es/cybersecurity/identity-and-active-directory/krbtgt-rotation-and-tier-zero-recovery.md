# KRBTGT Rotation and Tier Zero Recovery

## Definición

La rotación de KRBTGT es el reset controlado del material de contraseña de la cuenta `krbtgt` del dominio para que las claves de firma de tickets Kerberos previamente robadas ya no puedan validar Ticket Granting Tickets falsificados. No es un reset de contraseña normal. Después de un compromiso sospechado de `krbtgt`, es una operación de recuperación Tier 0 que debe tener en cuenta duraciones de tickets, historial de contraseñas, replicación de domain controllers, relaciones de trust, higiene de acceso privilegiado y riesgo de interrupción operacional.

## Por qué importa

El compromiso de [[golden-ticket-and-krbtgt-compromise|Golden Ticket]] convierte la recuperación AD en un problema de restauración de confianza. Si el atacante tiene la clave `krbtgt`, puede no necesitar ninguna contraseña de usuario en vivo para autenticarse. Puede presentar TGTs falsificados que parecen pertenecer a usuarios reales. Rotar todas las contraseñas de administrador sin cambiar `krbtgt` arregla el secreto incorrecto.

El principio de recuperación:

```
Si krbtgt está comprometido, el dominio no puede confiar plenamente en los TGTs de Kerberos
hasta que el material de krbtgt anterior quede fuera de las ventanas de validez y replicación.
```

Esto hace que la recuperación sea operativamente delicada. Rotar demasiado casualmente y los tickets falsificados siguen siendo válidos. Rotar demasiado agresivamente sin replicación y planificación de dependencias y la autenticación Kerberos legítima puede romperse en todo el dominio.

## Cómo funciona

La recuperación de KRBTGT depende de **6 mecánicas**:

1. **`krbtgt` firma y cifra los TGTs.** El KDC usa claves derivadas de la contraseña de `krbtgt` para proteger los TGTs. Los servicios no conocen la contraseña del usuario; confían en los tickets Kerberos.
2. **Los Domain Controllers cachean las claves actuales y anteriores.** AD mantiene el material de contraseña anterior para que los tickets existentes puedan seguir funcionando durante la rotación normal y la replicación.
3. **Un reset no invalida necesariamente todos los tickets falsificados.** Un ticket falsificado hecho con la clave anterior puede seguir siendo aceptado hasta el segundo reset y la expiración de las ventanas de duración de tickets/replicación.
4. **El timing de replicación importa.** Cada DC debe recibir el nuevo estado de contraseña de `krbtgt` antes de la siguiente fase. Un DC con material stale puede seguir validando tickets antiguos o emitir respuestas inconsistentes.
5. **La duración del ticket importa.** Los TGTs y tickets renovables existentes pueden continuar hasta los límites de política a menos que sean explícitamente interrumpidos por cambios de clave y controles operacionales.
6. **La contención Tier 0 debe preceder a la recuperación.** Si los atacantes todavía controlan DCSync, DCs, sesiones de admin Tier 0 o backups, simplemente pueden robar la nueva clave después de la rotación.

La lección estructural es *la rotación de KRBTGT es un problema de sequencing*. El comando de reset es pequeño; la operación de recuperación alrededor de él es el trabajo.

## Técnicas / patrones

- **Contener antes de rotar.** Remover o deshabilitar principales DCSync sospechados, aislar DCs comprometidos, proteger workstations de admin Tier 0, y detener el acceso activo del atacante antes de cambiar la raíz de confianza.
- **Usar el concepto de doble reset.** El primer reset aleja de la clave conocida comprometida; el segundo reset empuja la clave comprometida fuera del slot de contraseña anterior. Esperar por la replicación y las duraciones de tickets entre resets.
- **Validar la replicación entre fases.** Verificar la convergencia del DC antes del segundo reset. Los dominios multi-sitio y los DCs offline son los puntos de falla clásicos.
- **Asumir que la exposición de backups importa.** Si los atacantes accedieron a backups del DC, snapshots o `ntds.dit`, el límite de recuperación incluye la protección de backups y las rutas de restauración.
- **Tener en cuenta los trusts.** Los forest trusts, dominios hijo, trusts externos y SID filtering afectan a qué pueden acceder los tickets falsificados y qué dominios necesitan recuperación.
- **Separar las identidades de admin.** Usar credenciales Tier 0 limpias desde PAWs de confianza. No realizar la recuperación desde una workstation comprometida.
- **Monitorear intensamente durante y después.** Observar solicitudes de replicación, fallas Kerberos sospechosas, logons privilegiados, interrupciones de servicio y uso de tickets antiguos.

## Variantes y escenarios operacionales

La recuperación de KRBTGT tiene **5 escenarios comunes**.

### 1. Rotación de higiene rutinaria

Rotación planificada sin compromiso conocido. Menor urgencia, todavía requiere validación de replicación y conciencia del helpdesk. Útil para probar el proceso antes de una crisis.

### 2. Exposición sospechada de `krbtgt` desde DCSync

Alta confianza de que el material de `krbtgt` fue replicado o extraído. Requiere contención, doble reset y monitoreo de uso de tickets falsificados.

### 3. Compromiso de Domain Controller

Más severo que un evento DCSync único. Asumir que los atacantes pueden tener LSASS, NTDS, backup y acceso a sesiones de admin. La rotación sola es insuficiente hasta que se restaure la integridad del DC.

### 4. Compromiso de forest o multi-dominio

Cada dominio tiene su propio `krbtgt`. La recuperación debe identificar qué dominios están comprometidos y cómo los trusts pueden propagar el acceso.

### 5. Entorno legacy frágil

Aplicaciones antiguas, dependencias RC4, SPNs hard-codeados, sitios offline y DCs stale pueden hacer que la rotación sea ruidosa. Por eso importa el ensayo rutinario.

## Impacto

Ordenado por significancia de recuperación:

- **Invalida el material de firma TGT robado cuando se secuencia correctamente.** Este es el control directo contra los Golden Tickets.
- **Fuerza a los atacantes de vuelta a credenciales en vivo o claves recientemente robadas.** Una recuperación completada cierra la ruta de ticket falsificado antigua.
- **Puede interrumpir la autenticación si se apresura.** Una secuenciación incorrecta puede romper Kerberos para usuarios y servicios legítimos.
- **Revela la deuda de dependencia Tier 0.** Los trusts frágiles, DCs stale y dependencias de servicios antiguos emergen durante la planificación de la rotación.

## Detección y telemetría

Monitorear antes, durante y después de la rotación:

1.
**DCSync y abuso de replicación.**
   Observar `4662` con GUIDs de replicación y cualquier comportamiento de replicación no-DC. La rotación es inútil si los atacantes todavía tienen DCSync.

2.
**Fallas Kerberos después del reset.**
   Rastrear picos en fallas `4768`, `4769`, `4771` y `4776` por DC, sitio, cuenta y servicio. Se espera algún pico de fallas; la concentración inexplicada apunta a problemas de replicación o dependencia de servicio.

3.
**Actividad TGS con patrones de comportamiento antiguos.**
   Si el mismo patrón sospechoso de cuenta/fuente/servicio continúa después de la rotación, el atacante puede tener credenciales en vivo, acceso a nueva clave, o una ruta de persistencia que se pasó por alto.

4.
**Logons privilegiados y privilegios especiales.**
   Monitorear `4624`, `4672`, cambios de grupos de admin, logons en DCs y uso de PAW.

5.
**Telemetría de endpoint y proceso en DCs.**
   Observar acceso a LSASS, lecturas de `ntds.dit`, operaciones VSS, PowerShell sospechoso, ejecución remota y acceso a backups.

6.
**Salud de replicación.**
   La convergencia del DC es una señal de seguridad aquí, no solo higiene de operaciones.

## Controles defensivos

Ordenado por efectividad de recuperación:

1.
**Contención Tier 0 primero.**
   Deshabilitar o aislar los principales Tier 0 comprometidos, remover derechos DCSync inesperados, asegurar DCs, proteger backups, y usar workstations de admin de confianza.

2.
**Doble reset de `krbtgt` con períodos de espera validados.**
   Realizar reset 1, validar la replicación y la estabilidad operacional, esperar a través de la ventana de duración de tickets/replicación, luego realizar reset 2 y validar de nuevo.

3.
**Usar scripts y procedimientos soportados por el proveedor.**
   Microsoft publica guías de recuperación de forest y herramientas de reset de KRBTGT. Usar procedimientos soportados para que las verificaciones de replicación y compatibilidad no se improvisen bajo estrés.

4.
**Validar cada DC.**
   Confirmar la salud de replicación, sincronización de tiempo, comportamiento de autenticación y ausencia de DCs offline/stale antes de declarar la recuperación completa.

5.
**Reconstruir la confianza en el acceso privilegiado.**
   Resetear las credenciales de admin, rotar secretos de servicio donde corresponda, limpiar PAWs, revisar delegaciones y remover rutas del grafo hacia DCSync.

6.
**Monitorear post-recuperación por patrones antiguos.**
   Una rotación exitosa de `krbtgt` invalida los Golden Tickets antiguos; no prueba que el adversario no tenga otra persistencia.

### Qué no funciona como defensa primaria

- **Rotar cada contraseña humana pero no `krbtgt`.** Las credenciales humanas no son el secreto que firma los TGTs falsificados.
- **Un reset de `krbtgt` como recuperación completa.** La clave anterior puede seguir siendo aceptada. La secuencia de doble reset existe por una razón.
- **Rotar mientras los atacantes todavía tienen DCSync.** Pueden recuperar la nueva clave y la rotación se convierte en teatro.
- **Ejecutar la recuperación desde una workstation comprometida.** La recuperación Tier 0 requiere endpoints de admin limpios.
- **Asumir que la replicación se pondrá al día eventualmente.** La convergencia eventual no es una garantía de recuperación. Validarla.
- **Rollback de snapshot de DC después de la rotación.** Restaurar el estado anterior del DC puede reintroducir material de clave antiguo y romper las asunciones de confianza.

## Conceptos erróneos operacionales

- **"KRBTGT es solo otra cuenta."** Falso. Es la raíz de confianza Kerberos del dominio.
- **"El comando de reset es la recuperación."** Falso. El comando es un paso en la contención, replicación, validación y monitoreo.
- **"Si los usuarios todavía pueden loguearse, la recuperación funcionó."** Falso. La disponibilidad no es lo mismo que invalidar el material de clave sostenido por el atacante.
- **"La rotación es demasiado riesgosa para practicar."** Al revés. Es riesgosa precisamente porque las organizaciones no la ensayan.

## Labs prácticos

Ejecutar como tabletop o en un dominio lab propio. No experimentar con la rotación de `krbtgt` de producción sin un cambio aprobado y un plan de recuperación.

```
Lab 1 — Tabletop del árbol de decisión.
Objetivo: decidir cuándo se requiere la rotación de KRBTGT.
Entradas:
  - ¿DCSync confirmado? sí/no
  - ¿Material de krbtgt extraído? sí/no/desconocido
  - ¿Compromiso de DC? sí/no
  - ¿Compromiso de workstation de admin Tier 0? sí/no
  - ¿Exposición de backup? sí/no
Decisión:
  Si la exposición de krbtgt está confirmada o razonablemente sospechada, planificar doble reset después de la contención.
Concepto erróneo corregido: "no se observó Golden Ticket" no es prueba de que krbtgt esté seguro.
```

```powershell
# Lab 2 — Pre-verificación de salud de replicación en un lab.
repadmin /replsummary
dcdiag /test:replications
w32tm /monitor

# Interpretación del defensor:
# - los DCs stale y la deriva de tiempo son bloqueadores de recuperación
# - la salud de replicación es parte del control de seguridad
```

```
Lab 3 — Runbook de doble reset simulado.
Objetivo: ensayar el sequencing sin tocar producción.
Pasos:
  1. Anunciar ventana de cambio y congelar la actividad de admin Tier 0.
  2. Confirmar que las rutas DCSync están eliminadas.
  3. Resetear krbtgt una vez usando herramientas soportadas.
  4. Validar la replicación a cada DC.
  5. Esperar a través de la ventana definida de duración de tickets/replicación.
  6. Resetear krbtgt por segunda vez.
  7. Validar la autenticación, replicación y monitoreo.
Telemetría esperada:
  - eventos de password-set de cuenta para krbtgt
  - picos de fallas Kerberos si los clientes mantienen tickets stale
  - tráfico de replicación entre DCs
Limitaciones: el tabletop no puede probar compatibilidad de apps; la rotación en lab debería preceder a la aprobación del playbook de producción.
```

```powershell
# Lab 4 — Monitorear fallas Kerberos durante una ventana de reset en el lab.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4768,4769,4771,4776} -MaxEvents 500 |
  Select-Object TimeCreated, Id, ProviderName

# Ejercicio del analista:
# - agrupar por DC y cuenta
# - separar el churn de caché esperado de la interrupción persistente del servicio
# - identificar servicios todavía usando material Kerberos stale
```

```
Lab 5 — Checklist de validación post-recuperación.
Validar:
  - cada DC replicó la nueva versión de contraseña de krbtgt
  - ningún principal non-DC tiene derechos DCSync
  - las cuentas privilegiadas fueron rotadas desde PAWs limpias
  - las service accounts de alto privilegio fueron revisadas
  - los backups y snapshots del DC están protegidos
  - los patrones TGS sospechosos anteriores se detuvieron
  - el timeline del incidente registra los tiempos exactos de reset
```

## Ejemplos prácticos

- **Brecha de un solo reset.** Un equipo IR rota las contraseñas de Domain Admin y resetea `krbtgt` una vez. Los tickets falsificados continúan durante la ventana de clave anterior. El segundo reset faltante deja el dominio parcialmente no confiable.
- **Falla de replicación.** Un DC remoto está offline durante la rotación. Regresa más tarde con estado stale y crea comportamiento de autenticación inconsistente. La declaración de recuperación fue prematura.
- **Ruta DCSync no contenida.** El atacante todavía controla una service account con derechos de replicación. Roban la nueva clave de `krbtgt` después del reset.
- **Rotación rutinaria practicada.** Un equipo realiza rotación planificada anual con monitoreo y límites de rollback. Durante un incidente real, el procedimiento es conocido y el riesgo es menor.

## Notas relacionadas

- [[golden-ticket-and-krbtgt-compromise]] — el modelo de compromiso que esta operación de recuperación aborda.
- [[dcsync-and-ntdsdit-extraction]] — la forma más común en que el material de `krbtgt` es expuesto.
- [[bloodhound-attack-path-analysis]] — usar análisis de grafo para remover rutas hacia DCSync y Tier 0.
- [[tier-zero-administration-and-paw]] — la recuperación Tier 0 requiere endpoints de admin limpios y la disciplina que esta nota define.

## Referencias

- **Recuperación:** Microsoft Learn — Active Directory Forest Recovery: Reset the krbtgt password — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- **Recuperación:** Microsoft Learn — AD Forest Recovery Guide — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide
- **Fundamental:** MITRE ATT&CK T1558.001 — Golden Ticket — https://attack.mitre.org/techniques/T1558/001/
- **Recuperación:** Microsoft Security Blog — KRBTGT Account Password Reset Scripts now available for customers — https://www.microsoft.com/en-us/security/blog/2015/02/11/krbtgt-account-password-reset-scripts-now-available-for-customers/
