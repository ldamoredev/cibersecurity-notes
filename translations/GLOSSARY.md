# Guía de traducción ES — glosario y convenciones

Anchor de estilo y terminología para traducir las notas al español. Derivado de
las 53 traducciones ya hechas (analizadas, no inventadas). Leé esto antes de
traducir y respetalo en todos los archivos para mantener consistencia.

## Flujo de trabajo

1. Ver qué falta en una rama:
   `python3 scripts/extract_article.py --list <rama>`   (sin arg = todas)
2. Sacar el texto inglés limpio de una nota (≈7% del peso de la página):
   `python3 scripts/extract_article.py cybersecurity/<rama>/<slug>`
   Imprime la ruta del overlay a escribir y el markdown fuente sin el chrome
   (sidebar, prev/next, related-cards) — eso lo regenera el build, **no se traduce**.
3. Traducir y escribir el overlay en `translations/es/cybersecurity/<rama>/<slug>.md`.
   El build (`build.py`) lo toma como overlay; si falta, cae al inglés con banner.

## Registro

- **Español rioplatense / voseo.** Imperativos en vos: `Usá`, `Buscá`, `Validá`,
  `Hacé`, `Vigilá`, `Tené en cuenta`, `Evitá`, `Poné`, `Entendé`, `Asegurate`.
- 2ª persona: `podés`, `tenés`, `querés`, `sabés` (nunca "puedes/tienes").
- Tono técnico, directo y conciso, como notas de estudio de un operador. Sin
  relleno; espejá la densidad del original.
- No traduzcas de más: si una frase queda más natural con el término inglés
  (abajo), dejalo en inglés.

## Formato del overlay

- **Frontmatter YAML**: opcional (el build mergea el del inglés). Si lo incluís,
  copialo tal cual del inglés — `tags`, `created`, `updated`, `sources` no se traducen.
- **`# H1`**: dejalo en **inglés** cuando es un término propio/canónico
  ("Cross-Site Request Forgery (CSRF)", "JWT Attacks"). Para títulos genéricos
  (índices) sí se traduce ("Índice de Redes").
- **`## H2` / `### H3`**: se traducen ("Definición", "Por qué importa", "Cómo
  funciona", "Técnicas / patrones", "Impacto", "Detección y defensa", "Ejemplos
  prácticos", "Notas relacionadas", "Referencias").
- **Wikilinks**: el **target queda en inglés**, el **label se traduce**:
  `[[cookies-and-sessions|Cookies y sesiones]]`. Cross-branch con ruta completa:
  `[[cybersecurity/security-playbooks/inspect-session-handling|Inspeccionar el manejo de sesiones]]`.
  El extractor ya te da `[[slug|Label-inglés]]`: traducí solo el label.
- **Code blocks, comandos, rutas, URLs**: NO se tocan.
- **Referencias** (sección References): traducí solo las etiquetas tipo
  `Foundational:` → `Fundamental:`, `Testing / Lab:` → `Testing / Lab:` (o dejalo);
  los títulos de fuentes y URLs quedan igual.

## Se deja en INGLÉS (no traducir)

Términos que el corpus mantiene en inglés inline:

`endpoint` · `request` · `response` · `header` · `cookie` · `token` · `payload`
· `exploit` · `hash` · `rate limit(ing)` · `buffer overflow` · `heap` · `stack`
· `byte` · `shell` · `hardening` · `threat model` · `firmware` · `hook`
· nombres de protocolos/estándares y siglas: `CSRF`, `CORS`, `SameSite`, `XSS`,
`SSRF`, `IDOR`, `JWT`, `OAuth`, `TLS`, `HTTP(S)`, `DNS`, `TCP/IP`, `MFA`, `IAM`,
`BOLA`, `OWASP`, etc.
· flujos/acciones: `login`, `logout`, `preflight`, `content type`, `same-origin`,
`same-site`, `state-changing`, `binding`.
· nombres de herramientas y comandos: `nmap`, `Wireshark`, `BloodHound`, etc.

Regla práctica: si es jerga que en español se diría igual en inglés en una charla
técnica real, dejalo en inglés. Se puede pluralizar con "s" español (`los tokens`,
`las cookies`, `los endpoints`).

## Se TRADUCE (forma canónica)

| Inglés | Español |
|---|---|
| browser | navegador |
| attacker | atacante |
| victim | víctima |
| credentials | credenciales |
| session | sesión |
| key (cripto) | clave |
| password | contraseña |
| encryption / encrypted | cifrado |
| threat | amenaza |
| (attack) surface | superficie (de ataque) |
| layer | capa |
| flaw / weakness | falla / debilidad |
| account | cuenta |
| network | red |
| trust | confianza |
| boundary | límite / frontera |
| state | estado |
| settings | configuración |
| misconfiguration | mala configuración |
| disclosure | divulgación / exposición |
| bypass | bypass (subst.) / saltear (verbo) |
| request (verbo "to request") | solicitar |

`payload` admite `carga útil` o `payload` (el corpus usa ambos) — preferí
`payload` salvo que el contexto pida el español.

## Qué NO traducir / NO tocar

- El sidebar, breadcrumbs, prev/next, "Explore nearby notes" y las related-cards:
  los genera el build desde el grafo, no viven en el overlay (el extractor ya los corta).
- Slugs de archivo, anclas de heading, `tags`, fechas, URLs, código.
- La UI chrome (botones, labels de rama): ya está traducida en `build.py`
  (`UI_STRINGS`, `BRANCHES_ES`).
