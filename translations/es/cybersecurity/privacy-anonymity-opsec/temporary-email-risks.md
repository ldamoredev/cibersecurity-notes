# Temporary Email Risks

## Definición

Los riesgos del email temporal son las formas en que los buzones desechables fallan en proporcionar privacidad, anonimato o durabilidad fuertes para flujos de trabajo sensibles.

## Por qué importa

El email temporal puede ser útil para registros de bajo riesgo, pero es un control débil para cualquier cosa que necesite persistencia, recuperación, confianza o anonimato serio. El buzón puede ser compartido, registrado, bloqueado, de corta duración o vulnerable a la apropiación.

## Cómo funciona

Usá las 5 capas de debilidad:

1.
**Duración**
   El buzón puede expirar antes de que el flujo de trabajo se complete.

2.
**Accesibilidad**
   Cualquiera que conozca la dirección o pueda adivinar el nombre del buzón puede leer los mensajes.

3.
**Confianza del proveedor**
   El servicio puede registrar actividad, reutilizar nombres de buzón o exponer metadatos.

4.
**Recuperación de cuenta**
   Las direcciones temporales son frecuentemente malos canales de recuperación para cualquier cosa importante.

5.
**Reputación y abuso**
   Los sitios pueden bloquear las direcciones desechables o tratarlas como de mayor riesgo.

El bug no es usar una dirección temporal para un registro de bajo riesgo. El bug es usarla donde importan la identidad, la durabilidad o el control de acceso.

## Técnicas / patrones

- Usar correo desechable solo para tareas de bajo riesgo y baja persistencia.
- Nunca depender de un buzón temporal para la recuperación de cuentas.
- Verificar si el servicio es público, compartido o adivinable.
- Tratar el buzón como no confiable para cualquier cosa sensible.
- Esperar que los sistemas anti-abuso rechacen los dominios temporales.
- Evitar usar correo desechable para flujos de trabajo legales, financieros o sensibles a fuentes.

## Variantes y bypasses

Usá los 6 casos de correo temporal:

### 1. Buzón desechable público

Fácil de usar, pero la confidencialidad y el control de acceso más débiles.

### 2. Alias desechable privado

Más controlado, pero aún temporal y frecuentemente no adecuado para recuperación.

### 3. Alias de reenvío

Puede ser más seguro que los buzones públicos, pero el proveedor de reenvío se convierte en un punto de privacidad.

### 4. Buzón de tiempo limitado

Útil para verificación única, pero no para relaciones de larga duración.

### 5. Dominio desechable bloqueado por el sitio

El servicio puede rechazar o limitar el registro.

### 6. Identidad desechable reutilizada

Reutilizar la misma dirección temporal entre servicios crea correlación y sorpresas.

## Impacto

- Las cuentas pueden perderse si el buzón expira.
- Los mensajes sensibles pueden ser accesibles para otros si el buzón es público.
- Los flujos de trabajo de recuperación y soporte pueden fallar.
- Los dominios desechables pueden crear problemas de confianza y entrega.
- El buzón temporal puede convertirse en un punto de correlación si se reutiliza.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar correo desechable solo cuando la cuenta es desechable**
   Si la cuenta necesita recuperación o control a largo plazo, usar en cambio una estrategia de buzón o alias adecuada.

2.
**Evitar datos sensibles en buzones temporales**
   Tratarlos como endpoints de baja confianza.

3.
**Verificar el bloqueo y la confiabilidad**
   Si el servicio rechaza los dominios desechables, eso es una restricción de despliegue, no un avance de privacidad.

4.
**Separar los flujos de registro de bajo riesgo de los sensibles**
   Un buzón temporal puede estar bien para newsletters y no estar bien para fuentes, finanzas o recuperación.

### Qué no funciona como defensa primaria

- **El email temporal no es correo anónimo.**
- **Los buzones públicos no son privados.**
- **Una dirección desechable no es una estrategia de recuperación.**
- **Reutilizar un buzón temporal entre servicios crea correlación.**

## Labs prácticos

### Clasificar un registro

```
Servicio:
Necesita recuperación:
Necesita acceso de soporte:
Necesita uso a largo plazo:
¿Permite email desechable?:
¿Usar email temporal? sí/no
Alternativa:
```

Este es el primer punto de decisión.

### Revisar la exposición del buzón

```
Tipo de buzón:
Público o privado:
Expiración:
Quién puede acceder:
Contraseña o ninguna:
Reenvío:
Logs/retención:
```

Si las respuestas son débiles, el buzón no es adecuado para uso sensible.

### Testear el riesgo de recuperación de cuenta

```
¿Podés recuperar la cuenta si el buzón desaparece? sí/no
¿Podés cambiar el email después? sí/no
¿Puede el soporte verificar la identidad sin ese buzón? sí/no
```

El correo temporal debería fallar estas verificaciones por diseño.

### Comparar alternativas

```
Opción:
Buzón temporal
Alias
Buzón principal
Dirección de reenvío

Riesgo:
Persistencia:
Recuperación:
Privacidad:
```

La comparación debería alejar los usos sensibles del correo desechable.

## Ejemplos prácticos

- Un registro de foro usa una dirección desechable y la cuenta es intencionalmente temporal.
- Un buzón temporal expira antes de que se lea un email de verificación.
- Un buzón desechable público expone los mensajes de verificación a cualquiera con la dirección.
- Un servicio bloquea los dominios desechables al registrarse.
- Un usuario reutiliza el mismo buzón temporal en varios servicios y crea vinculabilidad.

## Notas relacionadas

- [[private-email-threat-models|Private Email Threat Models]]
- [[anonymity-threat-models|Anonymity Threat Models]]
- [[account-correlation|Account Correlation]]
- [[secure-file-sharing|Secure File Sharing]]

## Referencias

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Fundamental:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Mitigación:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
