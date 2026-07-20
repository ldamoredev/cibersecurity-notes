# BloodHound and Attack Path Analysis

## Definición

BloodHound es una herramienta de análisis de grafos open-source que modela **Active Directory como un grafo dirigido de principales** (usuarios, grupos, computadoras, GPOs, OUs, dominios) **y las relaciones entre ellos** (`MemberOf`, `AdminTo`, `CanRDP`, `WriteDACL`, `GenericAll`, `ForceChangePassword`, `Owns`, `DCSync`, `AllowedToDelegate`, etc.). Las rutas de ataque son entonces *consultas de grafo* — típicamente "encontrar la ruta más corta desde cualquier principal sin privilegios hasta uno privilegiado". La herramienta es idéntica para ofensiva y defensiva; lo que difiere es qué consultas ejecutás y qué hacés con la respuesta.

## Por qué importa

La mayoría de los compromisos AD no son exploits de un solo paso. Son **relaciones encadenadas**: usuario bajo privilegio es miembro del grupo A → el grupo A tiene `GenericAll` sobre el usuario B → el usuario B está en `Backup Operators` → `Backup Operators` puede leer `ntds.dit` → hash krbtgt → compromiso del dominio. Ninguna arista individual de esa cadena es obviamente peligrosa; la *combinación* es lo que importa. Sin análisis de grafo, los defensores auditan un principal a la vez y se pierden la cadena por construcción.

BloodHound es el artefacto que convirtió la seguridad de AD de "auditar cada ACL" a "computar el cierre transitivo de aristas peligrosas". Dominarlo es el puente de "sé que existe Kerberoasting" a "puedo razonar sobre qué objetivo de Kerberoasting *realmente importa* en este dominio".

El framing senior es la dualidad ofensiva/defensiva aplicada a la misma herramienta:

- **Ofensiva:** BloodHound dice al operador qué foothold único produce el mayor blast radius.
- **Defensiva:** BloodHound dice al defensor qué 5 ACLs deberían corregir este trimestre para eliminar las 20 rutas de ataque principales.

## Cómo funciona

BloodHound se reduce a **3 etapas**:

1. **Colección.** Un colector (SharpHound en Windows, `bloodhound-python` en Linux, AzureHound para Entra ID) consulta AD vía LDAP y SMB para enumerar principales y sus relaciones. La salida son archivos JSON.
2. **Ingesta.** El JSON se carga en una base de datos Neo4j vía la UI de BloodHound. Cada principal se convierte en un nodo; cada relación en una arista tipada y dirigida.
3. **Consulta.** La UI expone tanto consultas pre-construidas ("Find shortest paths to Domain Admins", "Find principals with DCSync rights", "Find Kerberoastable users") como una interfaz de consulta Cypher para análisis personalizado.

Secuencia representativa de punta a punta desde un foothold Linux:

```
# Etapa 1: recolectar desde cualquier host de dominio o alcanzable al dominio con una credencial válida.
bloodhound-python -u lowpriv -p 'Password1' -ns 10.0.0.1 -d LAB.LOCAL -c All
# Produce 20240510*_users.json, _groups.json, _computers.json, _domains.json, etc.

# Etapa 2: levantar BloodHound CE (Community Edition) localmente e importar.
docker compose -f bloodhound-cli.yaml up -d
# Abrir la UI en http://localhost:8080, cargar los archivos JSON.

# Etapa 3: consultar.
MATCH (n {kerberoastable: true})-[*1..]->(g:Group {name: 'DOMAIN ADMINS@LAB.LOCAL'})
RETURN n.name, length(shortestPath((n)-[*..]->(g))) AS path_length
ORDER BY path_length ASC
```

## Técnicas / patrones

- **Recolectar con `-c All` en el primer pase.** `All` ejecuta todos los métodos de colección. Para colecciones repetidas, ejecutar `Session` y `LoggedOn` por separado porque capturan *quién está logueado dónde* y decaen rápido.
- **Cypher supera a las consultas pre-construidas para el scope de engagement.** Aprendé suficiente Cypher para escribir tus propias consultas dirigidas.
- **`MarkOwned` tu foothold inmediatamente.** La UI permite marcar principales como "owned" (comprometidos). Las consultas de ruta desde `(:User {owned: true})` hasta objetivos de alto valor muestran tu *ruta real* hacia adelante.
- **Buscá derechos `DCSync` temprano.** Cualquier principal con `DS-Replication-Get-Changes-All` puede replicar toda la base de datos AD incluyendo todos los hashes de contraseñas. Consulta: `MATCH (n)-[:DCSync]->(d:Domain) RETURN n.name`.
- **Tratá las rutas hacia DCSync como rutas hacia capacidad de Golden Ticket.** Si una ruta de grafo alcanza un principal que puede replicar `krbtgt`, alcanza [[golden-ticket-and-krbtgt-compromise|compromiso de la raíz de confianza Kerberos del dominio]].
- **Emparejá con salidas de [[kerberoasting|Kerberoasting]] y [[as-rep-roasting|AS-REP Roasting]].** BloodHound sabe qué cuentas son kerberoastables y AS-REP-roastables. Después de roastear, marcá las cuentas crackeadas como owned y volvé a ejecutar consultas de ruta.
- **Defensores: ejecutá BloodHound *en tu propio AD*, mensualmente.** La consulta "Shortest Paths to Domain Admins" es la misma en ambos lados; el trabajo del defensor es hacer esas rutas más largas o eliminarlas.
- **OPSEC: la colección es ruidosa.** `bloodhound-python -c All` contra un dominio grande emite miles de consultas LDAP y enumeraciones de sesiones SMB en minutos.

## Variantes y bypasses

El ecosistema de BloodHound tiene **4 variantes de colector** que vale distinguir.

### 1. SharpHound (Windows, .NET)

El colector original. Corre in-process en un host Windows unido al dominio. Mayor cobertura de colección pero dispara AMSI y la mayoría de EDRs modernos.

### 2. bloodhound-python

Nativo de Linux. Se conecta a AD sobre LDAP (puerto 389/636) y SMB (445) con credenciales explícitas. Sin unión al dominio, sin .NET. La elección estándar desde un host de pentest Linux.

### 3. AzureHound

Apunta a Entra ID / Microsoft 365 / Azure AD en lugar de AD on-prem. Diferentes tipos de nodos y aristas. Esencial para entornos híbridos.

### 4. BloodHound Enterprise (BHE / comercial)

El producto comercial de SpecterOps. Colección continua, dashboards de gestión de rutas de ataque. En el lado ofensivo todos usan BloodHound CE (gratuito, open-source).

## Impacto

Ordenado por severidad real típica:

- **El tiempo de engagement hasta DA colapsa de días a horas.** Un operador red-team con BloodHound y un foothold puede identificar la ruta óptima en 30 minutos de colección.
- **La priorización del defensor se vuelve basada en datos.** "Tenemos 12.000 ACLs en este dominio" se convierte en "5 ACEs específicas representan el 80% de las rutas hacia DA, y corregirlas este trimestre elimina 200 rutas de ataque".
- **La pregunta del blast-radius finalmente tiene respuesta.** "Si la cuenta X es comprometida, ¿qué puede alcanzar el atacante?" antes requería traversal manual de ACLs. Ahora es `MATCH (n {name:'X'})-[*1..5]->(target) RETURN target`.
- **Las rutas de compromiso híbrido (on-prem + Azure) se vuelven visibles.** Los conectores que hacen de puente entre AD on-prem y Entra ID crean rutas cross-boundary que la auditoría tradicional se pierde completamente.

## Detección y defensa

Ordenado por efectividad:

1.
**Usá BloodHound defensivamente, mensualmente.**
   Ejecutar colección en tu propio AD, identificar las 10 rutas más cortas hacia Domain Admins y remediar las aristas más baratas. Repetir.

2.
**Detección de comportamiento sobre patrones de enumeración LDAP.**
   Firma de colección BloodHound: una IP fuente emite miles de consultas LDAP contra muchos OUs y objetos distintos en minutos, más enumeración de sesiones SMB.

3.
**Reducir la cantidad de principales `Tier 0`.**
   Tier 0 = cualquiera con autoridad efectiva de Domain Admin. Cuantos menos principales en Tier 0, menor la superficie de ataque para la traversal de grafos.

4.
**Auditar y podar ACEs peligrosas.**
   `WriteDACL`, `GenericAll`, `GenericWrite`, `WriteOwner`, `ForceChangePassword`, `AllExtendedRights`, y DS-Replication-Get-Changes-* son las aristas de alto leverage que BloodHound consulta.

5.
**Aislamiento de Tier 0.**
   Ningún admin Tier 0 debería nunca loguearse a un host Tier 1 o Tier 2. Privileged Access Workstations (PAWs) aplican esto físicamente.

6.
**Principales honeypot altos en el grafo.**
   Plantar una cuenta deceptivamente atractiva con ACLs de apariencia impactante. Cualquier consulta BloodHound que la presente como un "gran objetivo" indica que un colector corrió.

### Qué no funciona como defensa primaria

- **"No tenemos Domain Admins fuera del equipo SOC."** Casi siempre incorrecto en la inspección.
- **Deshabilitar la enumeración SMB.** Reduce levemente la fidelidad de colección pero no previene la construcción del grafo solo desde LDAP.
- **Bloquear binarios de BloodHound.** La firma es el *patrón de enumeración*, no el binario.

## Labs prácticos

Ejecutar solo contra entornos lab propios o engagements autorizados.

```
# Lab 1 — Levantar BloodHound CE localmente con Docker.
git clone https://github.com/SpecterOps/BloodHound.git
cd BloodHound/examples/docker-compose
docker compose up -d
```

```
# Lab 2 — Recolectar desde un host de pentest Linux contra un DC lab autorizado.
bloodhound-python -u lowpriv -p 'Password1' -ns 10.0.0.1 -d LAB.LOCAL -c All
# Arrastrar los archivos JSON a la UI de BloodHound para ingestarlos.
```

```
// Lab 3 — Consulta pre-construida: rutas más cortas hacia Domain Admins.
MATCH p=shortestPath((n:User)-[*1..]->(g:Group {name: 'DOMAIN ADMINS@LAB.LOCAL'}))
WHERE n.enabled = true
RETURN p LIMIT 25
```

```
// Lab 4 — Custom: usuarios kerberoastables con ruta hacia DA en ≤ 3 hops.
MATCH (u:User {hasspn: true})
MATCH p=shortestPath((u)-[*1..3]->(:Group {name: 'DOMAIN ADMINS@LAB.LOCAL'}))
RETURN u.name AS account, length(p) AS hops
ORDER BY hops ASC
```

```
// Lab 5 — Consulta de alto leverage del defensor: principales con derechos DCSync.
MATCH (n)-[r:GetChanges|GetChangesAll|DCSync]->(:Domain)
RETURN DISTINCT n.name AS principal, labels(n) AS type
// Los Domain Controllers deberían aparecer aquí. Cualquier otra cosa es un hallazgo.
```

```
# Lab 6 — Diseño de regla de detección del lado defensor.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4662} -MaxEvents 200 |
    Where-Object { $_.Properties[7].Value -match 'DS-Replication-Get-Changes' }
```

## Ejemplos prácticos

- **Post-foothold en engagement red-team.** Phish inicial con usuario bajo privilegio. Colección BloodHound en 30 minutos; la consulta de ruta más corta muestra que el usuario está en `IT Support` que tiene `GenericAll` sobre `Backup Service` que está en `Backup Operators`. Dos aristas ACE del phish hasta DA. Tiempo total de engagement: 4 horas.
- **Revisión defensiva trimestral.** El equipo de seguridad ejecuta BloodHound en AD de producción, identifica que el grupo `IT Helpdesk` tiene `ForceChangePassword` sobre 47 cuentas privilegiadas vía una delegación legacy de 2014. Remover la delegación elimina 312 rutas de ataque de la noche a la mañana.

## Notas relacionadas

- [[kerberoasting]] — BloodHound muestra qué cuentas kerberoastables valen la pena atacar.
- [[as-rep-roasting]] — BloodHound muestra qué cuentas AS-REP-roastables tienen rutas hacia adelante.
- [[golden-ticket-and-krbtgt-compromise]] — la consecuencia downstream de las rutas de ataque que llegan a DCSync de `krbtgt`.
- [[tier-zero-administration-and-paw]] — la defensa estructural que la salida de BloodHound suele motivar.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — el framing correcto para capturar la colección de BloodHound.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — el concepto de contraparte defensiva; las rutas son la unidad de análisis en ambos lados.

## Referencias

- **Docs Oficiales:** BloodHound Community Edition documentation (SpecterOps) — https://bloodhound.specterops.io/
- **Investigación / Deep Dive:** Robbins, Schroeder, Vazarkar — "An ACE Up The Sleeve: Designing Active Directory DACL Backdoors" (Black Hat USA 2017) — https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf
- **Investigación / Deep Dive:** Robbins & Schroeder — "Six Degrees of Domain Admin" (DEF CON 24) — https://www.youtube.com/watch?v=lxd2rerVsLo
