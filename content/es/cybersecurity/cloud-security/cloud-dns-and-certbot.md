# Cloud DNS and Certbot

## Definición

El cloud DNS and Certbot es la disciplina de gestionar el ciclo de vida nombre-a-servicio en entornos cloud: adquirir un dominio, delegar zones DNS, crear registros, exponer puertos de validación, obtener certificados TLS via Certbot/ACME y automatizar la renovación.

## Por qué importa

Para los labs cloud que necesitan HTTPS real, la cadena completa es: nombre de dominio → registros DNS → certificado TLS → renovación. Cada eslabón introduce superficies de seguridad: stale DNS apuntando a recursos eliminados, exposure temporal de validación, fallos de renovación y scope excesivo de certificados.

La unidad de seguridad correcta no es "el certificado", sino el ciclo de vida nombre-a-servicio completo.

## Cómo funciona

El setup DNS y Certbot cloud tiene **6 pasos**:

1. **Poseer o delegar el dominio.** El dominio apunta a un nameserver bajo tu control o al provider DNS del cloud.
2. **Crear registros DNS.** Los registros A, AAAA y CNAME conectan el nombre con la IP o el nombre del servicio.
3. **Exponer los puertos de validación.** El challenge HTTP-01 de ACME requiere port 80 alcanzable; el challenge DNS-01 requiere permisos de escritura en el zone.
4. **Probar el control del dominio.** Certbot/ACME verifica que quien solicita el certificado controla el dominio.
5. **Instalar los certificados.** Certbot escribe `fullchain.pem` y `privkey.pem`, usualmente en `/etc/letsencrypt/live/<dominio>/`.
6. **Automatizar la renovación.** Los certificados Let's Encrypt vencen en 90 días; la renovación automática via cron o systemd timer es necesaria.

El riesgo central de seguridad no es obtener el certificado inicial. Es el mantenimiento del nombre-a-servicio a lo largo del tiempo.

Un ejemplo trabajado, ciclo de vida DNS completo:

```
Dominio:
  lab.example.com

Registro DNS:
  A → 34.X.X.X (IP de la VM de lab)

Validación:
  HTTP-01: port 80 abierto solo durante el challenge, no después

Certificado:
  /etc/letsencrypt/live/lab.example.com/{fullchain,privkey}.pem

Renovación:
  cron `certbot renew --quiet` corriendo cada día

Teardown:
  eliminar registro DNS cuando la VM se elimina (para prevenir dangling DNS)
```

Los problemas más comunes de labs cloud no son el flujo de certificados sino el DNS que apunta a recursos eliminados.

## Técnicas / patrones

Las revisiones analizan:

- registros DNS "colgantes" (dangling) que apuntan a IPs eliminadas o recursos de cloud
- exposición de port 80 permanente cuando solo se necesita para validación
- fallos de renovación causados por cambios de IP o de security group
- scope excesivo de certificados (wildcard o múltiples dominios cuando uno es suficiente)
- clave privada del certificado con permisos de archivo sobre-amplios
- los secretos de delegación DNS (usados para el challenge DNS-01) sobre-permisivos

## Variantes y bypasses

El riesgo cloud de DNS y certificados tiene **4 formas comunes**.

### 1. DNS obsoleto a recursos eliminados

Los registros DNS siguen apuntando a IPs o nombres de recursos que ya no existen o fueron reasignados.

### 2. Exposición temporal de validación dejada abierta

El port 80 o la ruta `/.well-known/acme-challenge/` que se abrió para la validación nunca se cerró después.

### 3. Fallo de renovación

El certificado vence porque la renovación automática falló silenciosamente (cambio de IP, security group actualizado, certbot roto).

### 4. Scope amplio de wildcard o multicertificado

Un wildcard o un cert con muchos SANs es conveniente pero amplía el blast radius si la clave privada se compromete.

## Impacto

Ordenado aproximadamente por severidad:

- **Takeover de subdominio.** Los registros DNS colgantes que apuntan a recursos cloud eliminados pueden ser reclamados por un atacante.
- **Expiración del certificado.** Los usuarios ven errores TLS; el servicio puede ser interrumpido.
- **Filtración de clave privada.** Un `privkey.pem` con permisos amplios o en un backup puede comprometer el certificado.
- **Exposición de validación.** Los security groups de validación no removidos amplían la superficie de ataque.
- **Abuso de credenciales DNS.** Las credenciales de escritura DNS sobre-permisivas usadas para el challenge DNS-01 pueden ser abusadas para spoofing DNS.

## Detección y defensa

Ordenado por efectividad:

1.
**Eliminá los registros DNS cuando elimines los recursos.**
   Los registros DNS deberían estar en el checklist de teardown de cada lab.

2.
**Cerrá el port 80 después de la validación si no es necesario para la aplicación.**
   La validación HTTP-01 requiere port 80 solo durante el flujo de challenge.

3.
**Monitoreá la renovación de certificados.**
   Los logs de cron, alertas de vencimiento de certificados o herramientas de monitoreo externo deberían detectar fallos de renovación temprano.

4.
**Protegé la clave privada del certificado.**
   `/etc/letsencrypt/live/` debería ser accesible solo por root y el daemon que sirve TLS.

5.
**Limitá el scope de las credenciales DNS para el challenge DNS-01.**
   Las credenciales que pueden escribir en una zone DNS específica son más seguras que las credenciales de administración de DNS completo.

### Qué no funciona como defensa primaria

- **Certificados auto-firmados en producción.** Los clientes no los confían y son indicadores de configuración débil.
- **Ignorar las notificaciones de vencimiento de certificados.** Let's Encrypt envía emails de advertencia anticipada; actuar sobre ellos.
- **Tratar la clave privada como no sensible.** Las claves privadas de TLS son tan sensibles como cualquier otro secreto cloud.
- **Wildcards para simplificar la gestión.** Los wildcards son convenientes pero hacen la rotación y el scope más complejos.

## Labs prácticos

Usá un dominio de lab dedicado, no el dominio principal.

### Obtené un certificado con Certbot

```bash
# HTTP-01 challenge (requiere port 80 abierto temporalmente)
certbot certonly --standalone -d lab.example.com

# Verificar el certificado
certbot certificates
```

### Configurá la renovación automática

```bash
# Testear que la renovación funciona en dry-run
certbot renew --dry-run

# Verificar que el cron o timer de renovación existe
systemctl status certbot.timer  # systemd
# o
crontab -l | grep certbot       # cron
```

### Revisá los registros DNS en el teardown

```bash
# Listá los registros del dominio de lab
dig lab.example.com A
dig lab.example.com AAAA

# Si la IP ya no existe como recurso cloud, eliminá el registro
```

### Verificá la fecha de vencimiento del certificado

```bash
openssl x509 -in /etc/letsencrypt/live/lab.example.com/cert.pem \
  -noout -dates
```

### Auditá los permisos del directorio de certificados

```bash
ls -la /etc/letsencrypt/live/lab.example.com/
# La clave privada debería tener permisos 600 y propietario root
```

## Ejemplos prácticos

- Un registro DNS apunta a una IP que fue reasignada a otra cuenta después de eliminar la VM.
- El port 80 de validación queda abierto permanentemente en el security group.
- La renovación de Certbot falla silenciosamente porque la IP de la VM cambió.
- La clave privada TLS tiene permisos `644` en un servidor web.
- Las credenciales de escritura DNS para el challenge DNS-01 tienen scope de admin de zona completo.

## Notas relacionadas

- [[cloud-lab-infrastructure]]
- [[cloud-network-boundaries]]
- [[cloud-secrets-management]]
- [[dns-resolution|DNS Resolution]]
- [[tls-https|TLS and HTTPS]]

### Notas atómicas futuras sugeridas

- subdomain-takeover
- certbot-automation-patterns
- dns-01-challenge-security
- certificate-lifecycle-management

## Referencias

- **Docs Oficiales:** Certbot documentation — https://certbot.eff.org/docs/
- **Docs Oficiales:** Let's Encrypt documentation — https://letsencrypt.org/docs/
- **Docs Oficiales:** AWS Route 53 — https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html
- **Mitigación:** Subdomain takeover prevention — https://cheatsheetseries.owasp.org/cheatsheets/DNS_Security_Cheat_Sheet.html
