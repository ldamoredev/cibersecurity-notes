# SSH Access to Cloud Hosts

## Definición

El acceso SSH a hosts cloud es la ruta administrativa controlada para alcanzar máquinas virtuales Linux a través de claves, identidad, reglas de red y trazas de auditoría.

## Por qué importa

SSH es a menudo el primer paso práctico de un lab cloud y una de las formas más fáciles de crear exposición accidental. Una VM con el puerto 22 abierto al mundo, una clave privada reutilizada o un usuario por defecto privilegiado puede convertirse en el punto débil de todo el lab.

La lección específica del cloud es que la seguridad SSH no es solo `sshd_config`; incluye ciclo de vida de claves, security groups, IPs públicas, IAM y logging.

## Cómo funciona

El acceso SSH cloud tiene **5 puertas**:

1. **Identidad de la instancia.** La VM existe en una cuenta, región, subred y contexto de seguridad específicos.
2. **Alcanzabilidad de red.** Los security groups, firewalls, rutas e IPs públicas deciden si SSH es alcanzable.
3. **Autenticación del host.** El cliente verifica la clave host del servidor.
4. **Autenticación del usuario.** El servidor acepta una clave, certificado o identidad de sesión gestionada.
5. **Límite de privilegio.** Sudo, usuarios y roles de instancia deciden el impacto post-login.

El bug raramente es "SSH existe". El bug es SSH expuesto demasiado ampliamente con identidad débil y privilegios post-login excesivos.

Un ejemplo trabajado, exposición SSH a impacto cloud:

```
Host:
  lab-web-01

Entrante:
  TCP/22 desde 0.0.0.0/0

Credencial:
  clave privada compartida usada por múltiples labs

Post-login:
  el usuario por defecto tiene sudo sin contraseña

Identidad cloud:
  el rol adjunto puede leer almacenamiento de objetos

Decisión:
  la exposición SSH es de alto impacto porque el acceso shell se convierte en acceso a credenciales de rol y alcance de almacenamiento
```

El triaje SSH en cloud siempre debería incluir la ruta de red, higiene de credenciales, privilegio local e identidad cloud adjunta.

## Técnicas / patrones

Las revisiones analizan:

- puerto 22 abierto a `0.0.0.0/0` o `::/0`
- claves privadas reutilizadas entre labs
- usuarios por defecto con acceso sudo amplio
- verificación de clave host faltante
- distribución de claves no gestionada
- SSH directo donde el acceso estilo session-manager sería más seguro
- roles de instancia alcanzables después del login

## Variantes y bypasses

El riesgo SSH cloud tiene **4 formas comunes**.

### 1. SSH abierto al mundo

El security group permite SSH entrante desde cualquier lugar.

### 2. Acceso con clave compartida

Una clave otorga acceso a muchos hosts o muchas personas.

### 3. Usuario por defecto privilegiado

El login llega a un usuario que puede convertirse inmediatamente en root.

### 4. Escalación asistida por metadatos

Después del login SSH, el usuario puede acceder a credenciales de workload a través de metadatos.

## Impacto

Ordenado aproximadamente por severidad:

- **Compromiso del host.** Una clave robada o ruta de acceso débil da acceso shell.
- **Pivoting de credenciales.** Los roles de instancia y secretos locales pueden exponer APIs cloud.
- **Movimiento lateral.** El host puede alcanzar redes privadas o bases de datos.
- **Persistencia.** Los atacantes pueden agregar claves, usuarios, servicios o cron jobs.
- **Abuso de costos.** Los hosts comprometidos pueden minar, hacer proxy o escanear.

## Detección y defensa

Ordenado por efectividad:

1.
**Restringí la alcanzabilidad SSH.**
   Limitá el SSH entrante a IPs de confianza, VPNs, bastiones o servicios de sesión gestionada.

2.
**Usá claves únicas y protegidas o acceso gestionado.**
   Las credenciales únicas reducen el blast radius y hacen la rotación realista.

3.
**Minimizá sudo y los permisos del rol de instancia.**
   El acceso shell no debería implicar automáticamente acceso cloud admin.

4.
**Logueá SSH y la actividad del plano de control cloud.**
   Los logs del host más los logs de auditoría cloud muestran tanto el login como el comportamiento API posterior.

5.
**Rotá y eliminá el acceso obsoleto.**
   Las claves y usuarios deberían tener propietarios y vencimiento.

### Qué no funciona como defensa primaria

- **Cambiar SSH a un puerto no estándar.** Reduce el ruido, no la exposición real.
- **Confiar en autenticación por clave mientras se comparte la misma clave ampliamente.** Los secretos compartidos son difíciles de revocar.
- **Asumir que una VM de lab no es interesante.** A los atacantes no les importa por qué existe el host.
- **Bloquear login por contraseña pero dejar credenciales de rol admin accesibles.** El impacto post-login sigue importando.

## Labs prácticos

Usá una VM sandbox.

### Revisá la exposición SSH entrante

```
Instancia:
IP pública:
Security group/firewall:
Fuente permitida:
IPv6 permitido:
Motivo de negocio:
Vencimiento:
```

El SSH abierto al mundo debería ser temporal y justificado, si se usa.

### Validá la higiene de claves

```
Nombre de clave:
Propietario:
Usada por hosts:
Passphrase:
Almacenada dónde:
Fecha de rotación:
```

Las claves privadas son credenciales cloud.

### Verificá el alcance cloud post-login

```
curl -sS --max-time 2 http://169.254.169.254/ || true
```

Registrá si los metadatos son alcanzables y qué protecciones aplica el provider.

### Construí un registro de excepción de exposición SSH

```
host | fuente permitida | motivo | propietario | vencimiento | controles compensatorios
```

Las excepciones temporales de SSH necesitan un vencimiento o se convierten en exposición permanente.

### Comparar SSH directo con acceso de sesión gestionada

```
Requisito:
¿SSH directo necesario?:
Opción de sesión gestionada:
Trazabilidad de auditoría:
Exposición de red eliminada:
Decisión:
```

El acceso gestionado puede eliminar la alcanzabilidad SSH pública mientras preserva la administración.

## Ejemplos prácticos

- Una instancia EC2 de lab expone SSH a todo internet.
- Una clave privada se reutiliza en todos los ejercicios cloud.
- Un usuario por defecto tiene sudo sin contraseña.
- Un host comprometido lee credenciales de rol desde los metadatos.
- Un security group permanece abierto después de que termina el lab.

## Notas relacionadas

- [[cloud-lab-infrastructure]]
- [[cloud-network-boundaries]]
- [[cloud-metadata-security]]
- [[cloud-iam-boundaries]]
- [[metadata-endpoints|Metadata Endpoints]]

### Notas atómicas futuras sugeridas

- cloud-bastion-hosts
- session-manager-access
- ssh-key-rotation
- linux-hardening-for-cloud-hosts

## Referencias

- **Docs Oficiales:** AWS EC2 key pairs and Linux instances — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
- **Docs Oficiales:** AWS EC2 security groups — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html
- **Mitigación:** Microsoft guidance for securing privileged access — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model
