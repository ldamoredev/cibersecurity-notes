#!/usr/bin/env python3
"""Build a static HTML site from an Obsidian vault.

Walks mature cybersecurity branches under VAULT, converts each .md to .html,
resolves [[wikilinks]] and relative .md links, emits a sidebar and a
client-side search index. No framework, no build step beyond running this.
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys
from datetime import date
from dataclasses import dataclass, field
from pathlib import Path

import markdown
import yaml

VAULT = Path(os.environ.get("VAULT", "/Users/lautarodamore/obsidian-vault/ldamore"))
OUT = Path(__file__).resolve().parent / "site"
STATIC = Path(__file__).resolve().parent / "static"
SECTIONS = [
    ("cybersecurity", "Cybersecurity"),
]

SITE_NAME = "ldamoredev Security Atlas"
SITE_SHORT_NAME = "Security Atlas"
SITE_AUTHOR = "ldamoredev"
SITE_URL = os.environ.get(
    "SITE_URL",
    "https://ldamoredev.github.io/cibersecurity-notes",
).rstrip("/")

SITE_DESCRIPTION = (
    "A personal cybersecurity knowledge base for web security, API security, "
    "cloud security, offensive security, DevSecOps, and practical playbooks."
)

SITE_DESCRIPTION_ES = (
    "Una base personal de conocimiento de ciberseguridad sobre seguridad web, "
    "seguridad de APIs, cloud security, offensive security, DevSecOps y playbooks prácticos."
)

SITE_KEYWORDS = [
    "cybersecurity",
    "web security",
    "API security",
    "cloud security",
    "offensive security",
    "DevSecOps",
    "security playbooks",
]

THEME_COLOR = "#16a34a"  # CyberSec Atlas green — sets the Android URL bar
                           # tint, PWA splash, and <meta name="theme-color">.

# Only publish mature cybersecurity branches and their reference registries.
# Keep private/project execution notes, templates, tooling experiments, and
# future/unpromoted branches out of the public static mirror.
BRANCHES = {
    "foundations": {
        "label": "Foundations",
        "group": "Orientation",
        "summary": "Phase 0 mental models — what cybersecurity is, the CIA triad as a decision tool, threat-modeling quickstart, and the attacker-defender duality.",
        "accent": "amber",
    },
    "cryptography": {
        "label": "Cryptography",
        "group": "Substrate",
        "summary": "Hashes, encryption, signatures, key exchange, TLS/PKI, password storage, and token correctness.",
        "accent": "emerald",
    },
    "networking": {
        "label": "Networking",
        "group": "Substrate",
        "summary": "Reachability, HTTP, proxies, DNS, TLS, and packet-level observation.",
        "accent": "sky",
    },
    "wireless-security": {
        "label": "Wireless Security",
        "group": "Specialty",
        "summary": "Wi-Fi frames, handshakes, rogue access points, and local-network MITM.",
        "accent": "teal",
    },
    "web-security": {
        "label": "Web Security",
        "group": "Substrate",
        "summary": "Browser behavior, sessions, access control, and server-side exploit patterns.",
        "accent": "blue",
    },
    "api-security": {
        "label": "API Security",
        "group": "Specialty",
        "summary": "Authorization, token trust, inventory drift, and machine-readable abuse.",
        "accent": "indigo",
    },
    "cloud-security": {
        "label": "Cloud Security",
        "group": "Specialty",
        "summary": "IAM, metadata, storage, network boundaries, secrets, and logging controls.",
        "accent": "cyan",
    },
    "attack-surface-mapping": {
        "label": "Attack Surface Mapping",
        "group": "Operator",
        "summary": "What is exposed, reachable, discoverable, and drifting from intended design.",
        "accent": "amber",
    },
    "osint": {
        "label": "OSINT",
        "group": "Operator",
        "summary": "Public-source collection, evidence quality, and ethical handling of clues.",
        "accent": "violet",
    },
    "offensive-security": {
        "label": "Offensive Security / Recon",
        "group": "Paired",
        "summary": "Discovery, validation, and handoff from recon into concrete testing.",
        "accent": "rose",
    },
    "linux-privilege-escalation": {
        "label": "Linux Privilege Escalation",
        "group": "Operator",
        "summary": "Local boundary failures, enumeration, and safe escalation hypothesis testing.",
        "accent": "orange",
    },
    "privacy-anonymity-opsec": {
        "label": "Privacy, Anonymity & OPSEC",
        "group": "Always-on",
        "summary": "VPN threat models, Tor, metadata leakage, compartmentalization, and OPSEC failure modes.",
        "accent": "purple",
    },
    "devsecops": {
        "label": "DevSecOps",
        "group": "Specialty",
        "summary": "Secure delivery, CI/CD hardening, supply chain, secrets, and release trust.",
        "accent": "green",
    },
    "detection-engineering": {
        "label": "Detection Engineering",
        "group": "Paired",
        "summary": "Telemetry, behavioral analytics, correlation, and detection tradeoffs.",
        "accent": "cyan",
    },
    "identity-and-active-directory": {
        "label": "Identity & Active Directory",
        "group": "Specialty",
        "summary": "Kerberos, BloodHound graph analysis, DCSync, and AD attack-path engineering across offense and defense.",
        "accent": "red",
    },
    "binary-exploitation": {
        "label": "Binary Exploitation",
        "group": "Specialty",
        "summary": "Memory corruption, stack and heap overflows, exploit mitigations, reverse engineering, and the modern exploitation arms race at the binary level.",
        "accent": "fuchsia",
    },
    "security-playbooks": {
        "label": "Security Playbooks",
        "group": "Operator",
        "summary": "Repeatable procedures for turning concepts into practical tests.",
        "accent": "slate",
    },
}

BRANCH_GROUPS = ("Orientation", "Substrate", "Paired", "Operator", "Specialty", "Always-on")
MATURE_CYBERSECURITY_BRANCHES = set(BRANCHES)

MATURE_CYBERSECURITY_ROOT_FILES = {
    "index.md",
    "start-here.md",
    "must-know-30.md",
    "phase-1-substrate.md",
    "phase-2-offense-defense.md",
    "phase-3-operator.md",
    "phase-4-specialty.md",
    "reference-registry.md",
    "reference-registry-api-security.md",
    "reference-registry-cryptography.md",
    "reference-registry-attack-surface-mapping.md",
    "reference-registry-cloud-security.md",
    "reference-registry-devsecops.md",
    "reference-registry-detection-engineering.md",
    "reference-registry-identity-and-active-directory.md",
    "reference-registry-binary-exploitation.md",
    "reference-registry-linux-privilege-escalation.md",
    "reference-registry-networking.md",
    "reference-registry-offensive-security.md",
    "reference-registry-osint.md",
    "reference-registry-privacy-anonymity-opsec.md",
    "reference-registry-playbooks.md",
    "reference-registry-web-security.md",
    "reference-registry-wireless-security.md",
}

# --- Internationalization (i18n) -------------------------------------------
# The vault stays canonical English. Spanish is a WEB-ONLY overlay: translated
# note bodies live in THIS repo under translations/es/<rel_path> (never in the
# vault). UI chrome is translated via UI_STRINGS below. Pages are emitted per
# locale under site/<locale>/, with hreflang alternates and a language switcher.
LOCALES = ("en", "es")
DEFAULT_LOCALE = "en"
CURRENT_LOCALE = DEFAULT_LOCALE  # rebound per build pass in main()
TRANSLATIONS_ROOT = Path(__file__).resolve().parent / "translations"
OG_LOCALE = {"en": "en_US", "es": "es_ES"}
LOCALE_LABEL = {"en": "EN", "es": "ES"}
LOCALE_NAME = {"en": "English", "es": "Español"}

# Spanish labels + summaries for branches (overlay on the English BRANCHES dict).
BRANCHES_ES = {
    "foundations": {"label": "Fundamentos", "summary": "Modelos mentales de la Fase 0 — qué es la ciberseguridad, la tríada CIA como herramienta de decisión, arranque de modelado de amenazas y la dualidad atacante-defensor."},
    "cryptography": {"label": "Criptografía", "summary": "Hashes, cifrado, firmas, intercambio de claves, TLS/PKI, almacenamiento de contraseñas y corrección de tokens."},
    "networking": {"label": "Redes", "summary": "Alcanzabilidad, HTTP, proxies, DNS, TLS y observación a nivel de paquete."},
    "wireless-security": {"label": "Seguridad Inalámbrica", "summary": "Tramas Wi-Fi, handshakes, puntos de acceso falsos y MITM en la red local."},
    "web-security": {"label": "Seguridad Web", "summary": "Comportamiento del navegador, sesiones, control de acceso y patrones de explotación del lado del servidor."},
    "api-security": {"label": "Seguridad de APIs", "summary": "Autorización, confianza en tokens, deriva de inventario y abuso legible por máquina."},
    "cloud-security": {"label": "Seguridad en la Nube", "summary": "IAM, metadata, almacenamiento, límites de red, secretos y controles de logging."},
    "attack-surface-mapping": {"label": "Mapeo de Superficie de Ataque", "summary": "Qué está expuesto, alcanzable, descubrible y desviándose del diseño previsto."},
    "osint": {"label": "OSINT", "summary": "Recolección de fuentes públicas, calidad de la evidencia y manejo ético de las pistas."},
    "offensive-security": {"label": "Seguridad Ofensiva / Recon", "summary": "Descubrimiento, validación y traspaso del recon hacia pruebas concretas."},
    "linux-privilege-escalation": {"label": "Escalada de Privilegios en Linux", "summary": "Fallas de límites locales, enumeración y prueba segura de hipótesis de escalada."},
    "privacy-anonymity-opsec": {"label": "Privacidad, Anonimato y OPSEC", "summary": "Modelos de amenaza de VPN, Tor, fuga de metadata, compartimentación y modos de falla de OPSEC."},
    "devsecops": {"label": "DevSecOps", "summary": "Entrega segura, hardening de CI/CD, cadena de suministro, secretos y confianza en releases."},
    "detection-engineering": {"label": "Ingeniería de Detección", "summary": "Telemetría, analítica de comportamiento, correlación y trade-offs de detección."},
    "identity-and-active-directory": {"label": "Identidad y Active Directory", "summary": "Kerberos, análisis de grafos con BloodHound, DCSync e ingeniería de rutas de ataque en AD entre ofensa y defensa."},
    "binary-exploitation": {"label": "Explotación de Binarios", "summary": "Corrupción de memoria, desbordamientos de stack y heap, mitigaciones de exploits, ingeniería inversa y la carrera armamentista moderna de explotación a nivel binario."},
    "security-playbooks": {"label": "Playbooks de Seguridad", "summary": "Procedimientos repetibles para convertir conceptos en pruebas prácticas."},
}

# Display names for phase groups (the internal group KEY stays English).
GROUP_LABELS = {
    "en": {g: g for g in BRANCH_GROUPS},
    "es": {
        "Orientation": "Orientación",
        "Substrate": "Sustrato",
        "Paired": "Ofensa-Defensa",
        "Operator": "Operador",
        "Specialty": "Especialidad",
        "Always-on": "Siempre activo",
    },
}

UI_STRINGS = {
    "en": {
        "brand_sub": "Knowledge Base", "theme_toggle": "Toggle theme",
        "light_mode": "Light mode", "dark_mode": "Dark mode",
        "atlas_home": "Atlas Home", "entry_layer": "Entry layer",
        "cybersecurity_index": "Cybersecurity Index", "learning_path": "Learning Path",
        "reference_system": "Reference system", "registries": "Registries",
        "overview": "Overview", "updated_short": "updated",
        "nav_toggle": "Toggle navigation", "search_placeholder": "Search notes, playbooks, tags...",
        "notifications": "Notifications", "bc_home": "Home", "bc_cyber": "Cybersecurity",
        "min_read": "min read", "reading_time_title": "Estimated reading time",
        "updated": "Updated", "last_updated_title": "Last updated",
        "on_this_page": "On This Page", "on_this_page_aria": "On this page",
        "back_to_top": "Back to top", "previous": "Previous", "next": "Next",
        "related_notes": "Related notes", "lang_switch_aria": "Language",
        "translation_pending": "This note isn't translated yet — showing the English original.",
        "search_no_matches": "No matches for", "search_result": "result",
        "search_results": "results", "search_hint": "↑↓ to navigate · ↵ to open",
        "home_title_1": "Cybersecurity", "home_title_2": "Knowledge Base",
        "home_lede": "A curated atlas of <strong>{notes} notes</strong> across <strong>{branches} branches</strong> — organized by learning phase, from foundational substrate to specialty operations. Each note is atomic, with attacker/defender duality, references, and links to <em>playbooks</em> that turn it into action.",
        "home_explore": "Explore Notes", "home_playbooks": "View Playbooks",
        "stat_notes": "Notes", "stat_branches": "Branches", "stat_playbooks": "Playbooks", "stat_registries": "Registries",
        "path_eyebrow": "The learning path",
        "path_h2": "Read it in order. Each phase is the prerequisite for the next.",
        "path_p": "Start at <strong>00 · Orientation</strong> for the vocabulary. Walk through Substrate → Paired → Operator → Specialty. <strong>★ Always-on</strong> (privacy, OPSEC) threads through everything.",
        "path_cta": "Open the Start Here guide", "phase_label": "Phase", "phase_overview": "Phase overview",
        "branch_singular": "branch", "branch_plural": "branches", "note_singular": "note", "note_plural": "notes",
        "branch_explore": "Explore", "branch_notes_suffix": "notes", "featured_label": "Featured Note",
        "ref_eyebrow": "Reference system", "ref_h2": "Reference registries",
        "ref_p": "The registries keep citations normalized behind the learning branches, so atomic notes stay compact and high-signal.",
        "footer_about": "A personal cybersecurity knowledge base, published as a static operator reference.",
        "footer_start": "Start Here", "footer_index": "Full index",
        "landing_title": "Choose your language", "landing_sub": "ldamoredev Security Atlas",
        "tag_Orientation": "Start here", "tag_Substrate": "How things work", "tag_Paired": "Offense ↔ Defense",
        "tag_Operator": "Hands-on", "tag_Specialty": "Go deep", "tag_Always-on": "Cross-cutting",
        "intent_Orientation": "Mental models, the CIA triad, and threat modeling — the language you'll use everywhere else.",
        "intent_Substrate": "Networking, cryptography, browser trust, OS behavior. The substrate that every attack and defense touches.",
        "intent_Paired": "Attack and detection as paired thinking. Every offensive primitive has a defensive signature; learn them together.",
        "intent_Operator": "Recon, exposure mapping, privilege escalation, and the practical workflows of an offensive operator.",
        "intent_Specialty": "Pick what your job demands: cloud, identity, DevSecOps, wireless, binary exploitation, API security.",
        "intent_Always-on": "Privacy, anonymity, OPSEC. Practice continuously — these aren't a phase, they're a posture.",
        "title_index": "Cybersecurity Notes Index", "title_notes": "Notes",
    },
    "es": {
        "brand_sub": "Base de Conocimiento", "theme_toggle": "Cambiar tema",
        "light_mode": "Modo claro", "dark_mode": "Modo oscuro",
        "atlas_home": "Inicio del Atlas", "entry_layer": "Capa de entrada",
        "cybersecurity_index": "Índice de Ciberseguridad", "learning_path": "Ruta de aprendizaje",
        "reference_system": "Sistema de referencia", "registries": "Registros",
        "overview": "Resumen", "updated_short": "actualizado",
        "nav_toggle": "Alternar navegación", "search_placeholder": "Buscar notas, playbooks, tags...",
        "notifications": "Notificaciones", "bc_home": "Inicio", "bc_cyber": "Ciberseguridad",
        "min_read": "min de lectura", "reading_time_title": "Tiempo estimado de lectura",
        "updated": "Actualizado", "last_updated_title": "Última actualización",
        "on_this_page": "En esta página", "on_this_page_aria": "En esta página",
        "back_to_top": "Volver arriba", "previous": "Anterior", "next": "Siguiente",
        "related_notes": "Notas relacionadas", "lang_switch_aria": "Idioma",
        "translation_pending": "Esta nota todavía no está traducida — se muestra el original en inglés.",
        "search_no_matches": "Sin coincidencias para", "search_result": "resultado",
        "search_results": "resultados", "search_hint": "↑↓ para navegar · ↵ para abrir",
        "home_title_1": "Ciberseguridad", "home_title_2": "Base de Conocimiento",
        "home_lede": "Un atlas curado de <strong>{notes} notas</strong> en <strong>{branches} ramas</strong> — organizado por fase de aprendizaje, desde el sustrato fundamental hasta operaciones de especialidad. Cada nota es atómica, con dualidad atacante/defensor, referencias y enlaces a <em>playbooks</em> que la convierten en acción.",
        "home_explore": "Explorar notas", "home_playbooks": "Ver playbooks",
        "stat_notes": "Notas", "stat_branches": "Ramas", "stat_playbooks": "Playbooks", "stat_registries": "Registros",
        "path_eyebrow": "La ruta de aprendizaje",
        "path_h2": "Leelo en orden. Cada fase es el prerrequisito de la siguiente.",
        "path_p": "Empezá en <strong>00 · Orientación</strong> para el vocabulario. Recorré Sustrato → Ofensa-Defensa → Operador → Especialidad. <strong>★ Siempre activo</strong> (privacidad, OPSEC) atraviesa todo.",
        "path_cta": "Abrir la guía Start Here", "phase_label": "Fase", "phase_overview": "Resumen de la fase",
        "branch_singular": "rama", "branch_plural": "ramas", "note_singular": "nota", "note_plural": "notas",
        "branch_explore": "Explorar", "branch_notes_suffix": "notas", "featured_label": "Nota destacada",
        "ref_eyebrow": "Sistema de referencia", "ref_h2": "Registros de referencia",
        "ref_p": "Los registros mantienen las citas normalizadas detrás de las ramas de aprendizaje, para que las notas atómicas queden compactas y de alta señal.",
        "footer_about": "Una base de conocimiento personal de ciberseguridad, publicada como referencia estática para operadores.",
        "footer_start": "Empezar acá", "footer_index": "Índice completo",
        "landing_title": "Elegí tu idioma", "landing_sub": "ldamoredev Security Atlas",
        "tag_Orientation": "Empezá acá", "tag_Substrate": "Cómo funcionan las cosas", "tag_Paired": "Ofensa ↔ Defensa",
        "tag_Operator": "Manos a la obra", "tag_Specialty": "Profundizar", "tag_Always-on": "Transversal",
        "intent_Orientation": "Modelos mentales, la tríada CIA y el modelado de amenazas — el lenguaje que vas a usar en todo lo demás.",
        "intent_Substrate": "Redes, criptografía, confianza del navegador, comportamiento del SO. El sustrato que toca cada ataque y cada defensa.",
        "intent_Paired": "Ataque y detección como pensamiento emparejado. Cada primitiva ofensiva tiene una firma defensiva; aprendelas juntas.",
        "intent_Operator": "Recon, mapeo de exposición, escalada de privilegios y los flujos prácticos de un operador ofensivo.",
        "intent_Specialty": "Elegí lo que tu trabajo exige: nube, identidad, DevSecOps, inalámbrico, explotación de binarios, seguridad de APIs.",
        "intent_Always-on": "Privacidad, anonimato, OPSEC. Practicá de forma continua — no son una fase, son una postura.",
        "title_index": "Índice de Notas de Ciberseguridad", "title_notes": "Notas",
    },
}


def t(key: str) -> str:
    """Look up a UI string for the current locale, falling back to English."""
    loc = UI_STRINGS.get(CURRENT_LOCALE, UI_STRINGS[DEFAULT_LOCALE])
    if key in loc:
        return loc[key]
    return UI_STRINGS[DEFAULT_LOCALE].get(key, key)


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
TAG_RE = re.compile(r"(?<!\w)#([A-Za-z][A-Za-z0-9_\-/]*)")


@dataclass
class Note:
    section: str           # "cybersecurity"
    rel_path: Path         # path relative to VAULT, e.g. cybersecurity/networking/foo.md
    title: str
    slug: str              # basename without extension
    body_md: str
    tags: list[str] = field(default_factory=list)
    frontmatter: dict = field(default_factory=dict)

    @property
    def out_path(self) -> Path:
        return OUT / CURRENT_LOCALE / self.rel_path.with_suffix(".html")

    @property
    def url(self) -> str:
        return str(self.rel_path.with_suffix(".html"))


def branch_slug(note: Note) -> str:
    if len(note.rel_path.parts) >= 3 and note.rel_path.parts[0] == "cybersecurity":
        return note.rel_path.parts[1]
    return ""


def page_kind(note: Note) -> str:
    if note.slug.startswith("reference-registry"):
        return "registry"
    if note.rel_path.name == "index.md":
        return "index"
    if branch_slug(note) == "security-playbooks":
        return "playbook"
    return "concept"


_TITLE_CACHE: dict[str, dict[str, str]] = {}
_DESCRIPTION_CACHE: dict[str, dict[str, str]] = {}


def localized_title(note: Note) -> str:
    """Title for `note` in the current locale: the overlay's H1 if a translation
    exists, else the canonical English title. Cached per locale so the sidebar,
    related list, and prev/next links (which render OTHER notes' titles) stay cheap."""
    base = note.title.replace(" Seed", "")
    if CURRENT_LOCALE == DEFAULT_LOCALE:
        return base
    cache = _TITLE_CACHE.setdefault(CURRENT_LOCALE, {})
    key = str(note.rel_path)
    if key not in cache:
        title = base
        overlay = TRANSLATIONS_ROOT / CURRENT_LOCALE / note.rel_path
        if overlay.exists():
            try:
                raw = overlay.read_text(encoding="utf-8")
                m = FRONTMATTER_RE.match(raw)
                if m:
                    raw = raw[m.end():]
                tm = re.search(r"^#\s+(.+)$", raw, re.MULTILINE)
                if tm:
                    title = tm.group(1).strip()
            except OSError:
                pass
        cache[key] = title
    return cache[key]


def note_label(note: Note) -> str:
    return localized_title(note)


def localized_description(note: Note) -> str:
    """Description for related cards/search snippets in the current locale.

    When an overlay exists, use its first real paragraph so generated chrome
    around translated notes does not leak English copy.
    """
    if CURRENT_LOCALE == DEFAULT_LOCALE:
        return ""
    cache = _DESCRIPTION_CACHE.setdefault(CURRENT_LOCALE, {})
    key = str(note.rel_path)
    if key not in cache:
        desc = ""
        overlay = TRANSLATIONS_ROOT / CURRENT_LOCALE / note.rel_path
        if overlay.exists():
            try:
                raw = overlay.read_text(encoding="utf-8")
                m = FRONTMATTER_RE.match(raw)
                if m:
                    raw = raw[m.end():]
                desc = first_content_paragraph(raw)
            except OSError:
                pass
        cache[key] = desc
    return cache[key]


def branch_label(slug: str) -> str:
    if CURRENT_LOCALE != DEFAULT_LOCALE:
        loc = BRANCHES_ES.get(slug) if CURRENT_LOCALE == "es" else None
        if loc and loc.get("label"):
            return loc["label"]
    return BRANCHES.get(slug, {}).get("label", slug.replace("-", " ").title())


def branch_group(slug: str) -> str:
    return BRANCHES.get(slug, {}).get("group", "Other")


def group_label(group: str) -> str:
    """Display name for a phase group in the current locale (key stays English)."""
    return GROUP_LABELS.get(CURRENT_LOCALE, GROUP_LABELS[DEFAULT_LOCALE]).get(group, group)


def branch_summary(slug: str) -> str:
    if CURRENT_LOCALE != DEFAULT_LOCALE:
        loc = BRANCHES_ES.get(slug) if CURRENT_LOCALE == "es" else None
        if loc and loc.get("summary"):
            return loc["summary"]
    return BRANCHES.get(slug, {}).get("summary", "")


def branch_accent(slug: str) -> str:
    return BRANCHES.get(slug, {}).get("accent", "blue")


def should_publish(section: str, path: Path) -> bool:
    """Return whether a vault markdown file should be published."""
    rel = path.relative_to(VAULT)
    if section != "cybersecurity":
        return True
    if len(rel.parts) == 2:
        return rel.name in MATURE_CYBERSECURITY_ROOT_FILES
    branch = rel.parts[1]
    return branch in MATURE_CYBERSECURITY_BRANCHES


def load_note(section: str, path: Path) -> Note:
    raw = path.read_text(encoding="utf-8")
    fm: dict = {}
    m = FRONTMATTER_RE.match(raw)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            fm = {}
        raw = raw[m.end():]
    if path.name.startswith("reference-registry"):
        raw = re.sub(r"^# (.+?) Seed$", r"# \1", raw, count=1, flags=re.MULTILINE)

    # Title: first H1, else frontmatter title, else humanized filename.
    title_match = re.search(r"^#\s+(.+)$", raw, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    elif isinstance(fm.get("title"), str):
        title = fm["title"]
    else:
        title = path.stem.replace("-", " ").replace("_", " ").title()

    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    tags = [str(t) for t in tags]

    rel = path.relative_to(VAULT)
    return Note(
        section=section,
        rel_path=rel,
        title=title,
        slug=path.stem,
        body_md=raw,
        tags=tags,
        frontmatter=fm,
    )


def build_slug_index(notes: list[Note]) -> tuple[dict[str, list[Note]], dict[str, Note]]:
    """Return (slug -> [Notes], full_path_without_ext -> Note).

    The slug map keeps every candidate so we can pick the closest match per
    resolution call. The path map resolves wikilinks that spell out a full path.
    """
    by_slug: dict[str, list[Note]] = {}
    by_path: dict[str, Note] = {}
    collisions: dict[str, list[Note]] = {}
    for n in notes:
        if n.slug in by_slug and n.slug != "index":
            collisions.setdefault(n.slug, list(by_slug[n.slug])).append(n)
        by_slug.setdefault(n.slug, []).append(n)
        by_slug.setdefault(n.slug.lower(), []).append(n)
        key = str(n.rel_path.with_suffix(""))
        by_path[key] = n
        by_path[key.lower()] = n
    # Also index by title-slugified form: "TCP/IP Basics" -> "tcp-ip-basics"
    for n in notes:
        t_slug = re.sub(r"[^a-z0-9]+", "-", n.title.lower()).strip("-")
        if t_slug and t_slug != n.slug.lower():
            by_slug.setdefault(t_slug, []).append(n)
    for slug, members in collisions.items():
        paths = ", ".join(str(m.rel_path) for m in members)
        print(f"[warn] slug collision '{slug}': {paths} (resolver will prefer same-folder)", file=sys.stderr)
    return by_slug, by_path


def rewrite_links(md_text: str, note: Note, by_slug: dict[str, list[Note]], by_path: dict[str, Note]) -> str:
    """Rewrite [[wikilinks]] and relative .md links to generated .html paths."""
    import os
    here = (loc_root() / note.rel_path).parent
    source_folder = "/".join(note.rel_path.parts[:-1])

    def rel_href(target: Note) -> str:
        return os.path.relpath(loc_root() / target.rel_path.with_suffix(".html"), here)

    def resolve(raw: str) -> Note | None:
        raw = raw.strip()
        if raw.endswith(".md"):
            raw = raw[:-3]
        # Path-like?
        if "/" in raw:
            key = raw.strip("/")
            return by_path.get(key) or by_path.get(key.lower())
        # Bare slug — try exact, then lowercase, then title-slug.
        candidates = by_slug.get(raw) or by_slug.get(raw.lower())
        if not candidates:
            slugged = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
            candidates = by_slug.get(slugged)
        if not candidates:
            return None
        # Deduplicate while preserving order.
        seen = set()
        unique = []
        for c in candidates:
            k = str(c.rel_path)
            if k not in seen:
                seen.add(k)
                unique.append(c)
        if len(unique) == 1:
            return unique[0]
        # Prefer same folder, then same section, else first.
        for c in unique:
            if "/".join(c.rel_path.parts[:-1]) == source_folder:
                return c
        for c in unique:
            if c.rel_path.parts[0] == note.rel_path.parts[0]:
                return c
        return unique[0]

    def wikilink_sub(m: re.Match) -> str:
        target_raw = m.group(1).strip()
        label = (m.group(2) or target_raw.split("/")[-1]).strip()
        # Drop optional heading anchor "Page#Section"
        target_slug, _, anchor = target_raw.partition("#")
        target = resolve(target_slug)
        if not target:
            return f'<span class="unresolved-link" title="Unpublished or unresolved: {html.escape(target_slug)}">{html.escape(label)}</span>'
        href = rel_href(target)
        if anchor:
            href += "#" + anchor.strip().lower().replace(" ", "-")
        return f'<a href="{html.escape(href)}">{html.escape(label)}</a>'

    def mdlink_sub(m: re.Match) -> str:
        label = m.group(1)
        href = m.group(2).strip()
        # Leave external / anchor / already-html links alone.
        if href.startswith(("http://", "https://", "mailto:", "#", "/")):
            return m.group(0)
        # Rewrite relative .md -> .html
        if href.endswith(".md") or ".md#" in href:
            new_href = href.replace(".md#", ".html#").replace(".md", ".html")
            return f"[{label}]({new_href})"
        return m.group(0)

    # Wikilinks first (they're inline so safe before markdown parse; emit raw HTML
    # that markdown will leave alone because it's on a single line).
    md_text = WIKILINK_RE.sub(wikilink_sub, md_text)
    md_text = MD_LINK_RE.sub(mdlink_sub, md_text)
    return md_text


def build_sidebar_tree(notes: list[Note]) -> dict:
    """Return nested dict: {section: {subfolder: [notes], ...}}"""
    tree: dict[str, dict[str, list[Note]]] = {}
    for n in notes:
        parts = n.rel_path.parts  # (section, [sub...], file.md)
        section = parts[0]
        sub = "/".join(parts[1:-1]) or ""
        tree.setdefault(section, {}).setdefault(sub, []).append(n)
    # Stable ordering.
    for section in tree:
        for sub in tree[section]:
            tree[section][sub].sort(key=lambda n: (n.slug != "index", n.title.lower()))
    return tree


def branch_notes(subs: dict[str, list[Note]], slug: str) -> list[Note]:
    """Return published notes for a branch, including its overview index page."""
    return subs.get(slug, [])


def branch_note_count(subs: dict[str, list[Note]], slug: str) -> int:
    """Return the published branch count used by sidebar, homepage, and indexes."""
    return len(branch_notes(subs, slug))


def render_sidebar(tree: dict, current: Note | None) -> str:
    """Render the design's sidebar: phase groups expand to reveal branch links."""
    home_href = relpath_from(current, loc_root() / "index.html")
    lines: list[str] = ['<nav class="sidebar">']
    lines.append(
        '<div class="sidebar-head">'
        f'<a class="sidebar-brand" href="{html.escape(home_href)}">'
        '<span class="brand-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg></span>'
        f'<span class="brand-text"><span class="brand-title">CyberSec Atlas</span><span class="brand-sub">{html.escape(t("brand_sub"))}</span></span>'
        '</a>'
        f'<button class="theme-toggle" id="theme-toggle" type="button" aria-label="{html.escape(t("theme_toggle"))}">'
        '<span class="theme-label">'
        f'<span class="label-light"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>{html.escape(t("light_mode"))}</span>'
        f'<span class="label-dark"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>{html.escape(t("dark_mode"))}</span>'
        '</span>'
        '<span class="toggle-pill"></span>'
        '</button>'
        '</div>'
    )
    lines.append('<div class="sidebar-body">')
    lines.append(f'<a class="sidebar-home" href="{html.escape(home_href)}">{html.escape(t("atlas_home"))}</a>')

    subs = tree.get("cybersecurity", {})
    current_branch = branch_slug(current) if current else ""
    current_group = branch_group(current_branch) if current_branch else ""

    # Entry-layer pages (start-here, must-know-30, phase pages, cybersecurity index).
    root_order = {
        "index": 0,
        "start-here": 1,
        "must-know-30": 2,
        "phase-1-substrate": 3,
        "phase-2-offense-defense": 4,
        "phase-3-operator": 5,
        "phase-4-specialty": 6,
    }
    root_notes = [n for n in subs.get("", []) if not n.slug.startswith("reference-registry")]
    root_notes.sort(key=lambda n: (root_order.get(n.slug, 99), n.title.lower()))
    if root_notes:
        lines.append(f'<div class="sidebar-section"><h3>{html.escape(t("entry_layer"))}</h3>')
        for n in root_notes:
            label = t("cybersecurity_index") if n.slug == "index" else None
            lines.append(render_sidebar_link(n, current, label=label))
        lines.append('</div>')

    # Phase groups → expand to branch leaves. Prefixed numbers make the path obvious.
    phase_num_map = {
        "Orientation": "00",
        "Substrate":   "01",
        "Paired":      "02",
        "Operator":    "03",
        "Specialty":   "04",
        "Always-on":   "★",
    }
    lines.append(f'<div class="sidebar-section"><h3>{html.escape(t("learning_path"))}</h3>')
    for group in BRANCH_GROUPS:
        group_branches = [s for s in BRANCHES if s in subs and branch_group(s) == group]
        if not group_branches:
            continue
        group_count = sum(branch_note_count(subs, s) for s in group_branches)
        is_open = (group == current_group)
        open_attr = " open" if is_open else ""
        icon_paths = GROUP_ICONS.get(group, GROUP_ICONS["_default"])
        phase_num = phase_num_map.get(group, "")
        lines.append(
            f'<details class="nav-group"{open_attr}>'
            '<summary>'
            '<span class="ns-left">'
            f'<svg class="sec-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icon_paths}</svg>'
            f'<span class="ns-name"><span class="ns-num">{html.escape(phase_num)}</span>{html.escape(group_label(group))}</span>'
            '</span>'
            '<span class="ns-right">'
            f'<span class="count">{group_count}</span>'
            '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>'
            '</span>'
            '</summary>'
            '<div class="nav-children">'
        )
        for sub in group_branches:
            notes_for_branch = branch_notes(subs, sub)
            index_note = next((n for n in notes_for_branch if n.slug == "index"), None)
            note_leaves = [n for n in notes_for_branch if n.slug != "index"]
            count = branch_note_count(subs, sub)
            is_current_branch = (sub == current_branch)
            branch_open = " open" if is_current_branch else ""
            classes = ["nav-branch", f"accent-{branch_accent(sub)}"]
            if is_current_branch:
                classes.append("active")
            b_icon = branch_icon_svg(sub)
            # Branch row — summary acts as the disclosure trigger; "Overview"
            # link below routes to the branch index (since <summary> can't be
            # both a toggle and a nav link reliably across browsers).
            lines.append(
                f'<details class="{" ".join(classes)}"{branch_open}>'
                '<summary>'
                '<span class="nb-left">'
                f'<svg class="nb-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{b_icon}</svg>'
                f'<span class="nb-name">{html.escape(branch_label(sub))}</span>'
                '</span>'
                '<span class="nb-right">'
                f'<span class="count">{count}</span>'
                '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>'
                '</span>'
                '</summary>'
                '<div class="nav-leaves">'
            )
            if index_note:
                ovr_href = relpath_from(current, loc_root() / index_note.rel_path.with_suffix(".html"))
                ovr_active = " active" if current and current.rel_path == index_note.rel_path else ""
                lines.append(
                    f'<a class="nav-leaf nav-leaf-overview{ovr_active}" href="{html.escape(ovr_href)}">{html.escape(t("overview"))}</a>'
                )
            for nt in note_leaves:
                leaf_href = relpath_from(current, loc_root() / nt.rel_path.with_suffix(".html"))
                leaf_active = " active" if current and current.rel_path == nt.rel_path else ""
                leaf_label = note_label(nt)
                if len(leaf_label) > 56:
                    leaf_label = leaf_label[:53] + "…"
                lines.append(
                    f'<a class="nav-leaf{leaf_active}" href="{html.escape(leaf_href)}" title="{html.escape(note_label(nt))}">{html.escape(leaf_label)}</a>'
                )
            lines.append('</div></details>')
        lines.append('</div></details>')  # close this phase group's nav-children + nav-group
    lines.append('</div>')

    # Reference registries — collapsed group.
    registry_notes = [n for n in subs.get("", []) if n.slug.startswith("reference-registry")]
    if registry_notes:
        open_attr = " open" if current and page_kind(current) == "registry" else ""
        lines.append(f'<div class="sidebar-section"><h3>{html.escape(t("reference_system"))}</h3>')
        lines.append(
            f'<details class="nav-group"{open_attr}>'
            '<summary>'
            '<span class="ns-left">'
            '<svg class="sec-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>'
            f'<span class="ns-name">{html.escape(t("registries"))}</span>'
            '</span>'
            '<span class="ns-right">'
            f'<span class="count">{len(registry_notes)}</span>'
            '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>'
            '</span>'
            '</summary>'
            '<div class="nav-children">'
        )
        for n in registry_notes:
            href = relpath_from(current, loc_root() / n.rel_path.with_suffix(".html"))
            active = " active" if current and current.rel_path == n.rel_path else ""
            label = note_label(n)
            lines.append(
                f'<a class="nav-child{active}" href="{html.escape(href)}">'
                '<span class="nc-left"><span class="nc-name">'
                f'{html.escape(label if len(label) < 60 else label[:57] + "...")}'
                '</span></span>'
                '</a>'
            )
        lines.append('</div></details>')
        lines.append('</div>')
    lines.append("</div>")  # /sidebar-body
    today = date.today().isoformat()
    lines.append(
        '<div class="sidebar-footer">'
        f'<span>{html.escape(t("updated_short"))} · {html.escape(today)}</span>'
        '<span class="v">v2026.05</span>'
        '</div>'
    )
    lines.append("</nav>")
    return "\n".join(lines)


def render_sidebar_link(n: Note, current: Note | None, label: str | None = None) -> str:
    target_html = loc_root() / n.rel_path.with_suffix(".html")
    here = (loc_root() / current.rel_path).parent if current else loc_root()
    import os
    href = os.path.relpath(target_html, here)
    classes = ["sidebar-link", f"kind-{page_kind(n)}"]
    if current and current.rel_path == n.rel_path:
        classes.append("active")
    visible_label = label or note_label(n)
    visible_label = visible_label if len(visible_label) < 60 else visible_label[:57] + "..."
    return f'<a class="{" ".join(classes)}" href="{html.escape(href)}">{html.escape(visible_label)}</a>'


def loc_root() -> Path:
    """Output root for the current locale (e.g. site/en)."""
    return OUT / CURRENT_LOCALE


def relpath_from(note: Note | None, target: Path) -> str:
    import os
    here = (loc_root() / note.rel_path).parent if note else loc_root()
    return os.path.relpath(target, here)


def breadcrumb_html(note: Note) -> str:
    parts = [f'<a href="{html.escape(relpath_from(note, loc_root() / "index.html"))}">{html.escape(t("bc_home"))}</a>']
    if note.rel_path.parts and note.rel_path.parts[0] == "cybersecurity":
        cyber_index = loc_root() / "cybersecurity" / "index.html"
        parts.append(f'<a href="{html.escape(relpath_from(note, cyber_index))}">{html.escape(t("bc_cyber"))}</a>')
    branch = branch_slug(note)
    if branch:
        branch_index = loc_root() / "cybersecurity" / branch / "index.html"
        parts.append(f'<a href="{html.escape(relpath_from(note, branch_index))}">{html.escape(branch_label(branch))}</a>')
    parts.append(f'<span>{html.escape(note_label(note))}</span>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">' + "<span>/</span>".join(parts) + "</nav>"


def reading_time_minutes(note: Note) -> int:
    if page_kind(note) in {"index", "registry"}:
        return 0
    text = FRONTMATTER_RE.sub("", note.body_md, count=1)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1).split("/")[-1], text)
    words = len(re.findall(r"\w+", text))
    return max(1, round(words / 220))


def format_lastmod_human(iso_date: str) -> str:
    try:
        d = date.fromisoformat(iso_date)
    except ValueError:
        return iso_date
    return d.strftime("%b %d, %Y")


def page_meta_html(note: Note) -> str:
    branch = branch_slug(note)
    chips = [f'<span class="meta-chip">{html.escape(page_kind(note))}</span>']
    if branch:
        chips.append(f'<span class="meta-chip accent-{html.escape(branch_accent(branch))}">{html.escape(branch_label(branch))}</span>')
    minutes = reading_time_minutes(note)
    if minutes:
        chips.append(f'<span class="meta-chip meta-time" title="{html.escape(t("reading_time_title"))}">~{minutes} {html.escape(t("min_read"))}</span>')
    if page_kind(note) in {"concept", "playbook"}:
        updated = format_lastmod_human(note_last_modified(note))
        chips.append(f'<span class="meta-chip meta-updated" title="{html.escape(t("last_updated_title"))}">{html.escape(t("updated"))} {html.escape(updated)}</span>')
    if note.tags:
        chips.extend(f'<span class="meta-chip tag">#{html.escape(t)}</span>' for t in note.tags)
    return f'<div class="page-meta">{"".join(chips)}</div>'


def extract_toc(html_body: str) -> list[tuple[int, str, str]]:
    headings: list[tuple[int, str, str]] = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', html_body, re.DOTALL):
        level = int(m.group(1))
        anchor = m.group(2)
        label = strip_html(m.group(3)).strip()
        if label:
            headings.append((level, anchor, html.unescape(label)))
    return headings


def render_toc(html_body: str) -> str:
    headings = extract_toc(html_body)
    if not headings:
        return ""
    lines = [f'<aside class="toc" aria-label="{html.escape(t("on_this_page_aria"))}"><div class="toc-inner"><h2>{html.escape(t("on_this_page"))}</h2>']
    for level, anchor, label in headings[:18]:
        lines.append(f'<a class="toc-level-{level}" href="#{html.escape(anchor)}">{html.escape(label)}</a>')
    lines.append(f'<a class="back-to-top" href="#top">{html.escape(t("back_to_top"))}</a></div></aside>')
    return "\n".join(lines)


def root_asset(root_href: str, path: str) -> str:
    base = root_href if root_href else "."
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def absolute_site_url(path: str) -> str:
    return f"{SITE_URL}/{path.lstrip('/')}"


def note_last_modified(note: Note) -> str:
    source = VAULT / note.rel_path
    try:
        ts = source.stat().st_mtime
    except OSError:
        ts = date.today()
        return ts.isoformat()
    return date.fromtimestamp(ts).isoformat()


def locale_url(note: Note, loc: str) -> str:
    if note.section == "" and note.rel_path == Path("index.md"):
        return f"{SITE_URL}/{loc}/"
    return f"{SITE_URL}/{loc}/{note.url}"


def canonical_url(note: Note) -> str:
    return locale_url(note, CURRENT_LOCALE)


def page_title(note: Note) -> str:
    label = note_label(note)
    branch = branch_slug(note)

    if note.section == "" and note.rel_path == Path("index.md"):
        return f"{t('title_index')} | {SITE_NAME}"
    if page_kind(note) == "index" and branch:
        return f"{branch_label(branch)} {t('title_notes')} | {SITE_NAME}"
    if page_kind(note) == "registry":
        return f"{label} | {SITE_NAME}"
    if branch:
        return f"{label} - {branch_label(branch)} | {SITE_NAME}"
    return f"{label} | {SITE_NAME}"


def normalize_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def first_content_paragraph(md_text: str) -> str:
    cleaned = FRONTMATTER_RE.sub("", md_text, count=1)
    cleaned = re.sub(r"```.*?```", " ", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", cleaned)
    cleaned = WIKILINK_RE.sub(
        lambda m: m.group(2) or m.group(1).split("/")[-1],
        cleaned,
    )
    cleaned = re.sub(r"^#{1,6}\s+.*$", "", cleaned, flags=re.MULTILINE)

    for block in re.split(r"\n\s*\n", cleaned):
        block = normalize_ws(block)
        if not block or block.startswith("#") or block.startswith("---"):
            continue
        block = re.sub(r"^[-*+]\s+", "", block)
        block = re.sub(r"^>\s*", "", block)
        block = TAG_RE.sub(r"\1", block)
        block = normalize_ws(block)
        if len(block) >= 40:
            return block
    return ""


def truncate_description(value: str, limit: int = 165) -> str:
    value = normalize_ws(strip_html(value))
    if len(value) <= limit:
        return value
    clipped = value[: limit - 1]
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    return clipped.rstrip(".,;:-") + "..."


def note_description(note: Note) -> str:
    localized = localized_description(note)
    if localized:
        return truncate_description(localized)

    fm_description = note.frontmatter.get("description") or note.frontmatter.get("summary")
    if isinstance(fm_description, str) and fm_description.strip():
        return truncate_description(fm_description)
    if note.section == "" and note.rel_path == Path("index.md"):
        return site_description()

    branch = branch_slug(note)
    if page_kind(note) == "index" and branch:
        if CURRENT_LOCALE == "es":
            return truncate_description(f"Notas de {branch_label(branch)}: {branch_summary(branch)}")
        return truncate_description(f"{branch_label(branch)} notes: {branch_summary(branch)}")

    para = first_content_paragraph(note.body_md)
    if para:
        return truncate_description(para)
    if branch:
        if CURRENT_LOCALE == "es":
            return truncate_description(
                f"{note_label(note)} en la rama {branch_label(branch)} de la base de conocimiento de ciberseguridad de ldamoredev."
            )
        return truncate_description(
            f"{note_label(note)} in the {branch_label(branch)} branch of the ldamoredev cybersecurity knowledge base."
        )
    return site_description()


def site_description() -> str:
    return SITE_DESCRIPTION_ES if CURRENT_LOCALE == "es" else SITE_DESCRIPTION


def page_keywords(note: Note) -> list[str]:
    keywords = list(SITE_KEYWORDS)
    branch = branch_slug(note)
    if branch:
        keywords.append(branch_label(branch))
    keywords.append(note_label(note))
    keywords.extend(note.tags)

    seen: set[str] = set()
    result: list[str] = []
    for k in keywords:
        k = str(k).strip().lstrip("#")
        key = k.lower()
        if k and key not in seen:
            seen.add(key)
            result.append(k)
    return result[:14]


def breadcrumb_items(note: Note) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = [(t("bc_home"), f"{SITE_URL}/{CURRENT_LOCALE}/")]
    if note.rel_path.parts and note.rel_path.parts[0] == "cybersecurity":
        items.append((t("bc_cyber"), f"{SITE_URL}/{CURRENT_LOCALE}/cybersecurity/index.html"))
    branch = branch_slug(note)
    if branch:
        items.append((branch_label(branch), f"{SITE_URL}/{CURRENT_LOCALE}/cybersecurity/{branch}/index.html"))
    if not (note.section == "" and note.rel_path == Path("index.md")):
        items.append((note_label(note), canonical_url(note)))
    return items


def json_ld_for(note: Note) -> str:
    description = note_description(note)
    canonical = canonical_url(note)
    title = page_title(note)
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": url,
            }
            for i, (name, url) in enumerate(breadcrumb_items(note))
        ],
    }

    site_ref = {"@type": "WebSite", "@id": SITE_URL + "/#website", "name": SITE_NAME, "url": SITE_URL + "/"}
    author_ref = {"@type": "Person", "@id": SITE_URL + "/#author", "name": SITE_AUTHOR}
    if note.section == "" and note.rel_path == Path("index.md"):
        page = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": SITE_URL + "/#website",
            "name": SITE_NAME,
            "url": SITE_URL + "/",
            "description": site_description(),
            "inLanguage": CURRENT_LOCALE,
            "author": author_ref,
        }
    elif page_kind(note) == "index":
        last_modified = note_last_modified(note)
        page = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "@id": canonical + "#page",
            "name": title,
            "headline": note_label(note),
            "description": description,
            "url": canonical,
            "inLanguage": CURRENT_LOCALE,
            "dateModified": last_modified,
            "isPartOf": site_ref,
            "author": author_ref,
        }
    else:
        last_modified = note_last_modified(note)
        page = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "@id": canonical + "#article",
            "name": title,
            "headline": note_label(note),
            "description": description,
            "url": canonical,
            "inLanguage": CURRENT_LOCALE,
            "datePublished": last_modified,
            "dateModified": last_modified,
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "isPartOf": site_ref,
            "author": author_ref,
            "keywords": page_keywords(note),
        }
    return json.dumps([page, breadcrumb], ensure_ascii=False, separators=(",", ":"))


def seo_head(note: Note, root_href: str) -> str:
    title = page_title(note)
    description = note_description(note)
    canonical = canonical_url(note)
    og_image = absolute_site_url("assets/og-image.png")
    kind = "article" if page_kind(note) in {"concept", "playbook", "registry"} else "website"
    last_modified = note_last_modified(note)
    lines = [
        f'<title>{html.escape(title)}</title>',
        f'<meta name="description" content="{html.escape(description)}">',
        f'<meta name="author" content="{html.escape(SITE_AUTHOR)}">',
        f'<meta name="application-name" content="{html.escape(SITE_SHORT_NAME)}">',
        f'<meta name="keywords" content="{html.escape(", ".join(page_keywords(note)))}">',
        f'<meta name="theme-color" content="{THEME_COLOR}">',
        '<meta name="color-scheme" content="light dark">',
        '<meta name="referrer" content="strict-origin-when-cross-origin">',
        '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">',
        '<meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">',
        f'<link rel="canonical" href="{html.escape(canonical)}">',
        f'<link rel="icon" href="{html.escape(root_asset(root_href, "favicon.ico"))}" sizes="any">',
        f'<link rel="icon" href="{html.escape(root_asset(root_href, "favicon.svg"))}" type="image/svg+xml">',
        f'<link rel="apple-touch-icon" href="{html.escape(root_asset(root_href, "apple-touch-icon.png"))}">',
        f'<link rel="manifest" href="{html.escape(root_asset(root_href, "site.webmanifest"))}">',
        f'<meta property="og:site_name" content="{html.escape(SITE_NAME)}">',
        f'<meta property="og:locale" content="{OG_LOCALE.get(CURRENT_LOCALE, "en_US")}">',
        *[f'<meta property="og:locale:alternate" content="{OG_LOCALE[l]}">' for l in LOCALES if l != CURRENT_LOCALE],
        f'<meta property="og:type" content="{kind}">',
        f'<meta property="og:title" content="{html.escape(title)}">',
        f'<meta property="og:description" content="{html.escape(description)}">',
        f'<meta property="og:url" content="{html.escape(canonical)}">',
        f'<meta property="og:image" content="{html.escape(og_image)}">',
        '<meta property="og:image:type" content="image/png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{html.escape(SITE_NAME)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{html.escape(title)}">',
        f'<meta name="twitter:description" content="{html.escape(description)}">',
        f'<meta name="twitter:image" content="{html.escape(og_image)}">',
        f'<script type="application/ld+json">{json_ld_for(note).replace("</", "<\\/")}</script>',
    ]
    if kind == "article":
        branch = branch_slug(note)
        if branch:
            lines.append(f'<meta property="article:section" content="{html.escape(branch_label(branch))}">')
        lines.append(f'<meta property="article:published_time" content="{html.escape(last_modified)}">')
        lines.append(f'<meta property="article:modified_time" content="{html.escape(last_modified)}">')
    for loc in LOCALES:
        lines.append(f'<link rel="alternate" hreflang="{loc}" href="{html.escape(locale_url(note, loc))}">')
    x_default = SITE_URL + "/" if note.section == "" and note.rel_path == Path("index.md") else locale_url(note, DEFAULT_LOCALE)
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{html.escape(x_default)}">')
    return "\n".join(lines)


def branch_nav_html(note: Note, all_notes: list[Note]) -> str:
    if page_kind(note) not in {"concept", "playbook"}:
        return ""
    branch = branch_slug(note)
    if not branch:
        return ""
    here = note.out_path.parent

    siblings = sorted(
        [
            n for n in all_notes
            if branch_slug(n) == branch and page_kind(n) in {"concept", "playbook"}
        ],
        key=lambda n: n.title.lower(),
    )
    try:
        idx = next(i for i, n in enumerate(siblings) if n.rel_path == note.rel_path)
    except StopIteration:
        return ""

    prev_note = siblings[idx - 1] if idx > 0 else None
    next_note = siblings[idx + 1] if idx + 1 < len(siblings) else None
    if not prev_note and not next_note:
        return ""

    parts = ['<nav class="branch-nav" aria-label="Within this branch">']
    if prev_note:
        href = os.path.relpath(prev_note.out_path, here)
        parts.append(
            f'<a class="branch-nav-link prev" href="{html.escape(href)}">'
            '<span class="nav-dir">← Previous</span>'
            f'<strong>{html.escape(note_label(prev_note))}</strong>'
            '</a>'
        )
    else:
        parts.append('<span class="branch-nav-spacer"></span>')
    if next_note:
        href = os.path.relpath(next_note.out_path, here)
        parts.append(
            f'<a class="branch-nav-link next" href="{html.escape(href)}">'
            '<span class="nav-dir">Next →</span>'
            f'<strong>{html.escape(note_label(next_note))}</strong>'
            '</a>'
        )
    parts.append('</nav>')
    return "".join(parts)


def related_notes_html(note: Note, all_notes: list[Note]) -> str:
    if page_kind(note) not in {"concept", "playbook"}:
        return ""

    branch = branch_slug(note)
    here = note.out_path.parent
    note_tags = set(t.lower() for t in note.tags)
    candidates: list[tuple[int, str, Note]] = []

    for other in all_notes:
        if other.rel_path == note.rel_path or page_kind(other) in {"index", "registry"}:
            continue
        score = 0
        if branch and branch_slug(other) == branch:
            score += 5
        if branch and branch_group(branch_slug(other)) == branch_group(branch):
            score += 1
        shared_tags = note_tags.intersection(t.lower() for t in other.tags)
        score += len(shared_tags) * 3
        if score:
            candidates.append((score, other.title.lower(), other))
    if not candidates:
        return ""

    related_label = html.escape(t("related_notes"))
    lines = [
        f'<section class="related-notes" aria-label="{related_label}">',
        f"<h2>{related_label}</h2>",
        '<div class="related-grid">',
    ]
    for _, _, other in sorted(candidates, key=lambda x: (-x[0], x[1]))[:6]:
        href = os.path.relpath(other.out_path, here)
        branch_name = branch_label(branch_slug(other)) if branch_slug(other) else t("bc_cyber")
        desc = note_description(other)
        lines.append(
            f'<a class="related-card" href="{html.escape(href)}">'
            f'<span>{html.escape(branch_name)}</span>'
            f'<strong>{html.escape(note_label(other))}</strong>'
            f'<small>{html.escape(desc)}</small>'
            "</a>"
        )
    lines.append("</div></section>")
    return "\n".join(lines)


def xml_escape(value: str) -> str:
    return html.escape(value, quote=True)


def write_sitemap(notes: list[Note]) -> None:
    today = date.today().isoformat()

    def page_url(note: Note | None, loc: str) -> str:
        return f"{SITE_URL}/{loc}/" if note is None else locale_url(note, loc)

    # Keep the submitted sitemap deliberately simple for Search Console:
    # one URL per localized page, with hreflang handled in each page <head>.
    pages: list[tuple[str, str]] = [(SITE_URL + "/", today)]
    pages.extend((page_url(None, loc), today) for loc in LOCALES)
    for n in notes:
        lastmod = note_last_modified(n)
        pages.extend((locale_url(n, loc), lastmod) for loc in LOCALES)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, lastmod in pages:
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(url)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>\n")
    sitemap_body = "\n".join(lines)
    (OUT / "sitemap.xml").write_text(sitemap_body, encoding="utf-8")
    # Alternate filename for Search Console cache-busting on GitHub Pages.
    (OUT / "sitemap-notes.xml").write_text(sitemap_body, encoding="utf-8")


def write_robots() -> None:
    (OUT / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {absolute_site_url('sitemap.xml')}\n",
        encoding="utf-8",
    )


def write_manifest() -> None:
    manifest = {
        "name": SITE_NAME,
        "short_name": SITE_SHORT_NAME,
        "description": SITE_DESCRIPTION,
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#0f1117",  # matches the new dark-mode --bg
        "theme_color": THEME_COLOR,
        "icons": [
            {"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    (OUT / "site.webmanifest").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def copy_static_assets() -> None:
    if not STATIC.exists():
        return
    for path in STATIC.rglob("*"):
        if path.is_dir():
            continue
        target = OUT / path.relative_to(STATIC)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


PAGE_TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{seo_head}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap">
<script>(function(){{try{{var t=localStorage.getItem('theme');if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
<link rel="stylesheet" href="{css_href}?v={asset_ver}">
<link rel="stylesheet" href="{pygments_href}?v={asset_ver}">
</head>
<body id="top" data-root="{root_href}" data-locale-root="{locale_root}">
<div class="app {layout_class}">
{sidebar}
<div class="main-col">
<header class="topbar">
  <button id="sidebar-toggle" class="icon-btn menu-toggle" title="{nav_toggle}" aria-label="{nav_toggle}"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2 4h12M2 8h12M2 12h12"/></svg></button>
  <div class="topbar-search search-shell">
    <svg class="search-ico" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
    <input id="search" type="search" placeholder="{search_placeholder}" autocomplete="off">
    <kbd>⌘K</kbd>
  </div>
  <div class="topbar-actions">
    {lang_switcher}
    <button class="icon-btn" aria-label="{notifications}" title="{notifications}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg></button>
    <a class="github-link" href="https://github.com/ldamoredev/cibersecurity-notes" target="_blank" rel="noopener" aria-label="GitHub"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.69-1.28-1.69-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.71 1.26 3.37.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.79 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.42-2.69 5.4-5.25 5.68.41.36.78 1.06.78 2.13v3.16c0 .31.21.67.8.56C20.21 21.39 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z"/></svg><span class="gh-label">GitHub</span></a>
  </div>
</header>
<div id="search-results" hidden></div>
<div class="main-row">
<main class="content">
{breadcrumbs}
<header class="page-hero">
{page_meta}
</header>
<article class="{article_class}">
{body}
</article>
</main>
{toc}
</div>
</div>
</div>
<script src="{search_js_href}?v={asset_ver}"></script>
</body>
</html>
"""


def render_lang_switcher(note: Note, here: Path) -> str:
    """Header control linking the current page to its other-locale equivalent."""
    links = []
    for loc in LOCALES:
        target = OUT / loc / note.rel_path.with_suffix(".html")
        href = os.path.relpath(target, here)
        active = loc == CURRENT_LOCALE
        cls = "lang-link active" if active else "lang-link"
        links.append(
            f'<a class="{cls}" hreflang="{loc}" href="{html.escape(href)}" '
            f'aria-current="{"page" if active else "false"}">{html.escape(LOCALE_LABEL[loc])}</a>'
        )
    return f'<div class="lang-switch" role="group" aria-label="{html.escape(t("lang_switch_aria"))}">{"".join(links)}</div>'


def render_page(
    note: Note,
    html_body: str,
    sidebar_html: str,
    tree: dict,
    all_notes: list[Note] | None = None,
) -> str:
    here = note.out_path.parent
    css_href = os.path.relpath(OUT / "assets" / "style.css", here)
    pyg_href = os.path.relpath(OUT / "assets" / "pygments.css", here)
    search_js = os.path.relpath(OUT / "assets" / "search.js", here)
    home_href = os.path.relpath(loc_root() / "index.html", here)
    root_href = os.path.relpath(OUT, here) or "."
    locale_root = os.path.relpath(loc_root(), here) or "."

    is_home = note.section == "" and note.rel_path == Path("index.md")
    toc_html = "" if note.section == "" else render_toc(html_body)
    nav_html = branch_nav_html(note, all_notes or [])
    related_html = related_notes_html(note, all_notes or [])
    article_body = html_body
    if nav_html:
        article_body += "\n" + nav_html
    if related_html:
        article_body += "\n" + related_html
    return PAGE_TEMPLATE.format(
        seo_head=seo_head(note, root_href),
        css_href=html.escape(css_href),
        pygments_href=html.escape(pyg_href),
        asset_ver=ASSET_VER,
        search_js_href=html.escape(search_js),
        home_href=html.escape(home_href),
        root_href=html.escape(root_href),
        locale_root=html.escape(locale_root),
        lang=CURRENT_LOCALE,
        lang_switcher=render_lang_switcher(note, here),
        nav_toggle=html.escape(t("nav_toggle")),
        search_placeholder=html.escape(t("search_placeholder")),
        notifications=html.escape(t("notifications")),
        sidebar=sidebar_html,
        layout_class="no-toc" if not toc_html else "with-toc",
        breadcrumbs="" if is_home else breadcrumb_html(note),
        page_meta="" if is_home else page_meta_html(note),
        article_class="article-home" if note.rel_path == Path("index.md") else "article-note",
        body=article_body,
        toc=toc_html,
    )


def md_to_html(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=[
            "extra",
            "tables",
            "fenced_code",
            "codehilite",
            "sane_lists",
            "toc",
        ],
        extension_configs={
            "codehilite": {"guess_lang": False, "noclasses": False},
            "toc": {"permalink": False},
        },
    )
    return md.convert(md_text)


def write_pygments_css(path: Path) -> None:
    from pygments.formatters import HtmlFormatter
    path.write_text(HtmlFormatter().get_style_defs(".codehilite"), encoding="utf-8")


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s)


GROUP_ICONS = {
    "Orientation": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "Substrate":   '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "Paired":      '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 8a4 4 0 0 0-4 4v3"/><line x1="6" y1="9" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/>',
    "Operator":    '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>',
    "Specialty":   '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "Always-on":   '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "_default":    '<rect x="3" y="4" width="18" height="16" rx="2"/>',
}

BRANCH_ICON_MAP = {
    "foundations": "shield",
    "cryptography": "lock",
    "networking": "globe",
    "wireless-security": "wifi",
    "web-security": "globe",
    "api-security": "plug",
    "cloud-security": "cloud",
    "attack-surface-mapping": "target",
    "osint": "search",
    "offensive-security": "flag",
    "linux-privilege-escalation": "terminal",
    "privacy-anonymity-opsec": "eye",
    "devsecops": "wrench",
    "detection-engineering": "radar",
    "identity-and-active-directory": "users",
    "binary-exploitation": "bug",
    "security-playbooks": "book",
}

BRANCH_ICON_SVG = {
    "shield":   '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "lock":     '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "globe":    '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "wifi":     '<path d="M5 12.55a11 11 0 0 1 14 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/>',
    "plug":     '<path d="M9 2v4"/><path d="M15 2v4"/><path d="M5 10h14v4a7 7 0 0 1-14 0z"/><path d="M12 18v4"/>',
    "cloud":    '<path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>',
    "target":   '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "search":   '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "flag":     '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>',
    "terminal": '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>',
    "eye":      '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "wrench":   '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "radar":    '<circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 1 10 10"/><line x1="12" y1="12" x2="20" y2="6"/>',
    "users":    '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "bug":      '<rect x="8" y="6" width="8" height="14" rx="4"/><path d="M19 7l-3 2"/><path d="M5 7l3 2"/><path d="M19 13h-3"/><path d="M8 13H5"/><path d="M19 19l-3-2"/><path d="M5 19l3-2"/><path d="M12 6V3"/>',
    "book":     '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
}


def branch_icon_svg(slug: str) -> str:
    return BRANCH_ICON_SVG.get(BRANCH_ICON_MAP.get(slug, "shield"), BRANCH_ICON_SVG["shield"])


def find_featured_note(notes: list[Note], by_path: dict | None = None) -> Note | None:
    for slug in ("xss", "cross-site-scripting", "owasp-top-10"):
        for n in notes:
            if n.slug == slug and n.section == "cybersecurity":
                return n
    for n in notes:
        if n.section == "cybersecurity" and branch_slug(n) == "web-security" and n.slug != "index":
            return n
    return None


def count_label(count: int, singular_key: str, plural_key: str) -> str:
    """'3 notes' / '1 note' with locale-aware singular/plural."""
    return f'{count} {t(singular_key) if count == 1 else t(plural_key)}'


def build_home(tree: dict, notes: list[Note]) -> str:
    subs = tree.get("cybersecurity", {})
    published_notes = sum(len(v) for v in subs.values())
    registry_count = len([n for n in subs.get("", []) if n.slug.startswith("reference-registry")])
    playbook_count = branch_note_count(subs, "security-playbooks") if "security-playbooks" in subs else 0
    repo_url = "https://github.com/ldamoredev/cibersecurity-notes"

    lines: list[str] = []

    # --- HERO ---
    lines.append('<section class="hero home-hero">')
    lines.append('<div class="hero-crumb">&gt;_ ~/cybersecurity-atlas<span class="blink"></span></div>')
    lines.append(f'<h1 class="hero-title">{html.escape(t("home_title_1"))}<br><span class="accent">{html.escape(t("home_title_2"))}</span></h1>')
    lines.append(
        f'<p class="lede">{t("home_lede").format(notes=published_notes, branches=len(BRANCHES))}</p>'
    )
    lines.append('<div class="cta-row">')
    lines.append(
        '<a class="btn btn-primary" href="cybersecurity/start-here.html">'
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>'
        f'{html.escape(t("home_explore"))}</a>'
    )
    if playbook_count:
        lines.append(
            '<a class="btn btn-ghost" href="cybersecurity/security-playbooks/index.html">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>'
            f'{html.escape(t("home_playbooks"))}</a>'
        )
    lines.append('</div>')
    lines.append('<div class="hero-stats">')
    stats = [
        (published_notes, t("stat_notes"), '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'),
        (len(BRANCHES), t("stat_branches"), '<line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>'),
        (playbook_count, t("stat_playbooks"), '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>'),
    ]
    if registry_count:
        stats.append((registry_count, t("stat_registries"), '<path d="M4 4h16v4H4z"/><path d="M4 10h16v4H4z"/><path d="M4 16h16v4H4z"/>'))
    for value, label, svg_paths in stats:
        lines.append(
            '<div class="hero-stat">'
            f'<div class="stat-ico"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{svg_paths}</svg></div>'
            f'<div><div class="v">{value}</div><div class="l">{html.escape(label)}</div></div>'
            '</div>'
        )
    lines.append('</div>')
    lines.append('</section>')

    # --- LEARNING PATH ----------------------------------------------------
    # Pedagogical metadata: numbered phases with intent + per-phase index/landing page.
    phase_meta = {
        group: {
            "num": num,
            "tag": t(f"tag_{group}"),
            "intent": t(f"intent_{group}"),
            "href": href,
        }
        for group, num, href in (
            ("Orientation", "00", "cybersecurity/start-here.html"),
            ("Substrate", "01", "cybersecurity/phase-1-substrate.html"),
            ("Paired", "02", "cybersecurity/phase-2-offense-defense.html"),
            ("Operator", "03", "cybersecurity/phase-3-operator.html"),
            ("Specialty", "04", "cybersecurity/phase-4-specialty.html"),
            ("Always-on", "★", "cybersecurity/start-here.html"),
        )
    }

    # Guidance band — explains the path in one sentence.
    lines.append('<section class="path-intro">')
    lines.append(f'<div class="path-intro-head"><div class="section-eyebrow">{html.escape(t("path_eyebrow"))}</div>'
                 f'<h2>{html.escape(t("path_h2"))}</h2>'
                 f'<p>{t("path_p")}</p></div>')
    lines.append('<a class="path-intro-cta" href="cybersecurity/start-here.html">'
                 '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'
                 f'{html.escape(t("path_cta"))}</a>')
    lines.append('</section>')

    # Phase track — numbered horizontal stepper (compact summary, then full sections below).
    lines.append('<section class="phase-track" aria-label="Learning phases">')
    for group in BRANCH_GROUPS:
        meta = phase_meta.get(group)
        if not meta:
            continue
        group_branches = [s for s in BRANCHES if s in subs and branch_group(s) == group]
        group_count = sum(branch_note_count(subs, s) for s in group_branches)
        if not group_branches:
            continue
        anchor = "phase-" + group.lower().replace(" ", "-")
        always_on = ' phase-step-always' if group == "Always-on" else ''
        lines.append(
            f'<a class="phase-step{always_on}" href="#{anchor}">'
            f'<div class="ps-num">{html.escape(meta["num"])}</div>'
            '<div class="ps-body">'
            f'<div class="ps-tag">{html.escape(meta["tag"])}</div>'
            f'<div class="ps-name">{html.escape(group_label(group))}</div>'
            f'<div class="ps-meta">{count_label(len(group_branches), "branch_singular", "branch_plural")} · {count_label(group_count, "note_singular", "note_plural")}</div>'
            '</div>'
            '</a>'
        )
    lines.append('</section>')

    # --- BRANCHES, ORGANIZED BY PHASE ------------------------------------
    for group in BRANCH_GROUPS:
        meta = phase_meta.get(group)
        group_branches = [s for s in BRANCHES if s in subs and branch_group(s) == group]
        if not group_branches or not meta:
            continue
        group_count = sum(branch_note_count(subs, s) for s in group_branches)
        anchor = "phase-" + group.lower().replace(" ", "-")
        always_on = ' phase-section-always' if group == "Always-on" else ''
        lines.append(f'<section class="phase-section{always_on}" id="{anchor}">')
        lines.append(
            '<header class="phase-section-head">'
            f'<div class="phs-num">{html.escape(meta["num"])}</div>'
            '<div class="phs-titles">'
            f'<div class="phs-eyebrow">{html.escape(t("phase_label"))} {html.escape(meta["num"])} · {html.escape(meta["tag"])}</div>'
            f'<h2 class="phs-name">{html.escape(group_label(group))}</h2>'
            f'<p class="phs-intent">{html.escape(meta["intent"])}</p>'
            '</div>'
            '<div class="phs-meta">'
            f'<a class="phs-open" href="{html.escape(meta["href"])}">{html.escape(t("phase_overview"))} '
            '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>'
            f'<div class="phs-count">{count_label(len(group_branches), "branch_singular", "branch_plural")} · {count_label(group_count, "note_singular", "note_plural")}</div>'
            '</div>'
            '</header>'
        )
        lines.append('<div class="branch-grid">')
        for slug in group_branches:
            notes_for_branch = branch_notes(subs, slug)
            index_note = next((n for n in notes_for_branch if n.slug == "index"), notes_for_branch[0])
            href = index_note.url
            accent = branch_accent(slug)
            published_count = branch_note_count(subs, slug)
            icon_paths = branch_icon_svg(slug)
            lines.append(
                f'<a class="branch-card accent-{html.escape(accent)}" href="{html.escape(href)}">'
                '<div class="bc-head">'
                f'<div class="bc-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icon_paths}</svg></div>'
                f'<span class="bc-count">{published_count} {html.escape(t("branch_notes_suffix"))}</span>'
                '</div>'
                f'<h3 class="bc-title">{html.escape(branch_label(slug))}</h3>'
                f'<p class="bc-desc">{html.escape(branch_summary(slug))}</p>'
                f'<span class="bc-link">{html.escape(t("branch_explore"))}'
                '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'
                '</span>'
                '</a>'
            )
        lines.append('</div>')
        lines.append('</section>')

    # --- FEATURED NOTE (closing flourish) ---
    featured = find_featured_note(notes)
    if featured:
        f_branch = branch_slug(featured) or "web-security"
        f_branch_label = branch_label(f_branch)
        f_minutes = max(3, reading_time_minutes(featured))
        f_desc = note_description(featured)
        f_tags = featured.tags[:4] if featured.tags else []
        tags_html = "".join(
            f'<span class="tag">#{html.escape(str(t).lstrip("#"))}</span>' for t in f_tags
        )
        lines.append('<section class="section">')
        lines.append(
            '<div class="feat-label">'
            '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M13 2 3 14h7l-1 8 10-12h-7z"/></svg>'
            f'{html.escape(t("featured_label"))}</div>'
        )
        lines.append(f'<a class="featured-card" href="{html.escape(featured.url)}">')
        lines.append('<div>')
        lines.append('<div class="feat-meta">')
        lines.append(f'<span class="pill green">{html.escape(f_branch_label)}</span>')
        lines.append(
            '<span class="pill-time">'
            '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
            f'{f_minutes} {html.escape(t("min_read"))}</span>'
        )
        lines.append('</div>')
        lines.append(f'<h2 class="feat-title">{html.escape(note_label(featured))}</h2>')
        lines.append(f'<p class="feat-desc">{html.escape(f_desc)}</p>')
        if tags_html:
            lines.append(f'<div class="tag-row">{tags_html}</div>')
        lines.append('</div>')
        lines.append(
            '<div class="arrow-btn">'
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'
            '</div>'
        )
        lines.append('</a>')
        lines.append('</section>')

    # --- REFERENCE REGISTRIES ---
    registry_notes = [n for n in subs.get("", []) if n.slug.startswith("reference-registry")]
    if registry_notes:
        lines.append('<section class="reference-panel" id="registries">')
        lines.append(f'<div class="section-eyebrow">{html.escape(t("ref_eyebrow"))}</div>')
        lines.append(f'<h2>{html.escape(t("ref_h2"))}</h2>')
        lines.append(f'<p>{html.escape(t("ref_p"))}</p>')
        lines.append('<div class="reference-list">')
        for n in registry_notes:
            lines.append(f'<a href="{html.escape(n.url)}">{html.escape(note_label(n))}</a>')
        lines.append('</div></section>')

    # --- FOOTER ---
    lines.append('<footer class="home-footer">')
    lines.append(f'<div class="footer-about"><strong>ldamoredev/atlas</strong><p>{html.escape(t("footer_about"))}</p></div>')
    lines.append('<div class="footer-links">')
    lines.append(f'<a href="{repo_url}" rel="noopener" target="_blank">GitHub</a>')
    lines.append(f'<a href="cybersecurity/start-here.html">{html.escape(t("footer_start"))}</a>')
    lines.append(f'<a href="cybersecurity/index.html">{html.escape(t("footer_index"))}</a>')
    lines.append('</div></footer>')

    return "\n".join(lines)


ASSET_VER = "0"  # populated by main() before any page renders


def compute_asset_version() -> str:
    """Hash of all rendered/static stylesheets + search.js. Each CSS edit
    bumps the URL query param so returning visitors don't see a transitional
    render against a stale cached stylesheet."""
    import hashlib
    h = hashlib.sha1()
    h.update(STYLE_CSS.encode("utf-8"))
    h.update(SEARCH_JS.encode("utf-8"))
    atlas_path = STATIC / "assets" / "atlas.css"
    if atlas_path.exists():
        h.update(atlas_path.read_bytes())
    return h.hexdigest()[:10]


def localized_note(note: Note) -> tuple[Note, bool]:
    """Return (note-for-current-locale, is_fallback).

    English is canonical and comes straight from the vault. For other locales we
    look for a WEB-ONLY overlay at translations/<locale>/<rel_path> in this repo.
    If it's missing we fall back to the English body (is_fallback=True) so every
    page still exists in every locale.
    """
    if CURRENT_LOCALE == DEFAULT_LOCALE:
        return note, False
    overlay = TRANSLATIONS_ROOT / CURRENT_LOCALE / note.rel_path
    if not overlay.exists():
        return note, True
    raw = overlay.read_text(encoding="utf-8")
    fm = dict(note.frontmatter)
    m = FRONTMATTER_RE.match(raw)
    if m:
        try:
            fm.update(yaml.safe_load(m.group(1)) or {})
        except yaml.YAMLError:
            pass
        raw = raw[m.end():]
    title_match = re.search(r"^#\s+(.+)$", raw, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else note.title
    localized = Note(
        section=note.section,
        rel_path=note.rel_path,
        title=title,
        slug=note.slug,
        body_md=raw,
        tags=note.tags,
        frontmatter=fm,
    )
    return localized, False


def translation_pending_banner() -> str:
    return f'<div class="translation-pending" role="note">{html.escape(t("translation_pending"))}</div>\n'


def write_language_landing() -> None:
    """Root /index.html: a tiny language chooser that auto-redirects by locale."""
    links = "".join(
        f'<a class="lang-choice" href="{loc}/" hreflang="{loc}">{html.escape(LOCALE_NAME[loc])}</a>'
        for loc in LOCALES
    )
    description = site_description()
    og_locale = OG_LOCALE.get(DEFAULT_LOCALE, "en_US")
    og_image = absolute_site_url("assets/og-image.png")
    alts = "".join(f'<link rel="alternate" hreflang="{loc}" href="{SITE_URL}/{loc}/">\n' for loc in LOCALES)
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/">'
    locale_list = ",".join(f'"{l}"' for l in LOCALES)

    head = (
        "<!doctype html>\n"
        f'<html lang="{DEFAULT_LOCALE}">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>{html.escape(SITE_NAME)}</title>\n"
        f'<meta name="description" content="{html.escape(description)}">\n'
        f'<meta name="author" content="{html.escape(SITE_AUTHOR)}">\n'
        f'<meta name="application-name" content="{html.escape(SITE_SHORT_NAME)}">\n'
        '<meta name="robots" content="index, follow">\n'
        f'<link rel="canonical" href="{SITE_URL}/">\n'
        f"{alts}\n"
        f'<meta name="theme-color" content="{THEME_COLOR}">\n'
        '<meta name="color-scheme" content="dark light">\n'
        f'<meta property="og:site_name" content="{html.escape(SITE_NAME)}">\n'
        f'<meta property="og:locale" content="{og_locale}">\n'
        '<meta property="og:type" content="website">\n'
        f'<meta property="og:title" content="{html.escape(SITE_NAME)}">\n'
        f'<meta property="og:description" content="{html.escape(description)}">\n'
        f'<meta property="og:url" content="{SITE_URL}/">\n'
        f'<meta property="og:image" content="{html.escape(og_image)}">\n'
        '<meta property="og:image:type" content="image/png">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{html.escape(SITE_NAME)}">\n'
        f'<meta name="twitter:description" content="{html.escape(description)}">\n'
        f'<meta name="twitter:image" content="{html.escape(og_image)}">\n'
        '<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
        '<link rel="manifest" href="site.webmanifest">\n'
    )
    # Plain (non-f) strings below so CSS/JS braces stay literal.
    style = (
        "<style>\n"
        "html,body{height:100%;margin:0}\n"
        "body{display:flex;flex-direction:column;align-items:center;justify-content:center;"
        "gap:1.2rem;font-family:Inter,system-ui,sans-serif;background:#0f1117;color:#e6e8ee;"
        "text-align:center;padding:2rem}\n"
        ".landing-sub{color:#16a34a;font-weight:700;letter-spacing:.02em}\n"
        "h1{margin:0;font-size:clamp(1.4rem,4vw,2.2rem)}\n"
        ".lang-choices{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center}\n"
        ".lang-choice{padding:.7rem 1.6rem;border:1px solid #2a2f3a;border-radius:10px;"
        "color:#e6e8ee;text-decoration:none;font-weight:600;background:#161a23}\n"
        ".lang-choice:hover{border-color:#16a34a;color:#16a34a}\n"
        "</style>\n"
    )
    script = (
        "<script>\n(function(){\n"
        f"  var locales=[{locale_list}];\n"
        "  var saved=null;try{saved=localStorage.getItem('preferred-locale');}catch(e){}\n"
        "  var nav=(navigator.language||'en').slice(0,2).toLowerCase();\n"
        f"  var pick=(saved&&locales.indexOf(saved)>=0)?saved:(locales.indexOf(nav)>=0?nav:'{DEFAULT_LOCALE}');\n"
        "  location.replace(pick+'/');\n})();\n</script>\n"
    )
    body = (
        "</head>\n<body>\n"
        f'<div class="landing-sub">{html.escape(t("landing_sub"))}</div>\n'
        f"<h1>{html.escape(t('landing_title'))}</h1>\n"
        f'<div class="lang-choices">{links}</div>\n'
        "</body>\n</html>\n"
    )
    (OUT / "index.html").write_text(head + style + script + body, encoding="utf-8")


def redirect_html(target: str) -> str:
    """A noindex meta-refresh + JS redirect page pointing at `target`."""
    attr = html.escape(target, quote=True)
    js = json.dumps(target)
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
        "<title>Redirecting…</title>\n"
        f'<link rel="canonical" href="{attr}">\n'
        '<meta name="robots" content="noindex, follow">\n'
        f'<meta http-equiv="refresh" content="0; url={attr}">\n'
        f"<script>location.replace({js});</script>\n"
        f'</head><body>Redirecting to <a href="{attr}">{attr}</a>.</body></html>\n'
    )


def write_redirect_stubs(notes: list[Note]) -> None:
    """Preserve pre-i18n URLs: the old flat /<rel_path>.html paths now 301-style
    redirect to their /<DEFAULT_LOCALE>/ equivalents so indexed links don't 404."""
    count = 0
    for n in notes:
        old_path = OUT / n.rel_path.with_suffix(".html")
        if old_path.exists():  # never clobber a real (locale) page
            continue
        target = f"{SITE_URL}/{DEFAULT_LOCALE}/{n.url}"
        old_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.write_text(redirect_html(target), encoding="utf-8")
        count += 1
    print(f"Wrote {count} legacy-URL redirect stubs -> /{DEFAULT_LOCALE}/")


def main() -> int:
    global ASSET_VER, CURRENT_LOCALE
    ASSET_VER = compute_asset_version()

    # Load notes once — the vault is the canonical English source.
    notes: list[Note] = []
    for section_key, _ in SECTIONS:
        root = VAULT / section_key
        if not root.exists():
            print(f"[warn] missing: {root}", file=sys.stderr)
            continue
        for p in sorted(root.rglob("*.md")):
            if not should_publish(section_key, p):
                continue
            notes.append(load_note(section_key, p))

    if not notes:
        print(
            f"[error] loaded 0 notes from {VAULT}; refusing to delete or rebuild {OUT}.",
            file=sys.stderr,
        )
        return 1

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)

    print(f"Loaded {len(notes)} notes.")
    by_slug, by_path = build_slug_index(notes)
    tree = build_sidebar_tree(notes)

    total_pages = 0
    broken_total = 0
    translated_total = 0
    # Build the full site once per locale, into site/<locale>/.
    for loc in LOCALES:
        CURRENT_LOCALE = loc
        search_entries: list[dict] = []
        for n in notes:
            render_note, is_fallback = localized_note(n)
            if not is_fallback and loc != DEFAULT_LOCALE:
                translated_total += 1
            rewritten = rewrite_links(render_note.body_md, render_note, by_slug, by_path)
            broken_total += rewritten.count('class="unresolved-link"')
            body_html = md_to_html(rewritten)
            if is_fallback and loc != DEFAULT_LOCALE:
                body_html = translation_pending_banner() + body_html
            sidebar_html = render_sidebar(tree, render_note)
            page = render_page(render_note, body_html, sidebar_html, tree, notes)
            render_note.out_path.parent.mkdir(parents=True, exist_ok=True)
            render_note.out_path.write_text(page, encoding="utf-8")

            br = branch_slug(render_note)
            search_entries.append({
                "title": note_label(render_note),
                "url": render_note.url,
                "section": render_note.section,
                "branch": branch_label(br) if br else t("bc_cyber"),
                "group": group_label(branch_group(br)) if br else t("reference_system"),
                "kind": page_kind(render_note),
                "tags": render_note.tags,
                "description": note_description(render_note),
                "keywords": page_keywords(render_note),
                "text": strip_html(body_html)[:2000],
            })

        # Per-locale home page.
        home_note = Note(section="", rel_path=Path("index.md"), title="ldamoredev notes", slug="index", body_md="")
        home_body = build_home(tree, notes)
        sidebar_html = render_sidebar(tree, home_note)
        home_note.out_path.parent.mkdir(parents=True, exist_ok=True)
        home_note.out_path.write_text(
            render_page(home_note, home_body, sidebar_html, tree, notes),
            encoding="utf-8",
        )

        # Per-locale search index (titles + body text differ by language).
        (loc_root() / "search.json").write_text(
            json.dumps(search_entries, ensure_ascii=False),
            encoding="utf-8",
        )
        total_pages += len(notes) + 1

    # Shared, language-neutral assets (written once at site root).
    CURRENT_LOCALE = DEFAULT_LOCALE
    write_pygments_css(OUT / "assets" / "pygments.css")
    (OUT / "assets" / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (OUT / "assets" / "search.js").write_text(SEARCH_JS, encoding="utf-8")
    copy_static_assets()
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    write_manifest()
    write_sitemap(notes)
    write_robots()
    write_language_landing()
    write_redirect_stubs(notes)

    print(
        f"Wrote {total_pages} pages across {len(LOCALES)} locales to {OUT} "
        f"(unresolved wikilinks: {broken_total}; non-default translated notes: {translated_total})"
    )
    return 0


STYLE_CSS = r"""
@import url("atlas.css");

/* --- i18n: language switcher + translation-pending banner --- */
.lang-switch { display: inline-flex; gap: 2px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.lang-switch .lang-link { padding: .32rem .6rem; font-size: .78rem; font-weight: 700; letter-spacing: .03em; color: var(--muted); text-decoration: none; line-height: 1; display: inline-flex; align-items: center; }
.lang-switch .lang-link:hover { color: var(--fg); background: var(--panel); }
.lang-switch .lang-link.active { color: var(--accent, #16a34a); background: var(--panel); }
.translation-pending { margin: 0 0 1.2rem; padding: .7rem 1rem; border: 1px solid var(--border); border-left: 3px solid #d97706; border-radius: 8px; background: var(--panel); color: var(--muted); font-size: .9rem; }

/* --- generated-page extras layered on top of atlas.css --- */
.related-notes, .branch-nav {
  margin-top: 3rem;
  padding-top: 1.4rem;
  border-top: 1px solid var(--border);
}
.related-grid, .branch-nav {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: .85rem;
}
.related-card, .branch-nav-link {
  display: block;
  padding: .95rem 1rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--panel);
  color: var(--fg);
  box-shadow: var(--shadow-card);
  transition: transform .12s, border-color .12s, box-shadow .12s;
  text-decoration: none;
}
.related-card:hover, .branch-nav-link:hover {
  transform: translateY(-1px);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-hover);
  text-decoration: none;
}
.branch-nav-link { display: flex; flex-direction: column; gap: .25rem; line-height: 1.35; }
.branch-nav-link.next { text-align: right; align-items: flex-end; }
.nav-dir, .related-card span {
  display: block;
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
}

/* search results dropdown — overrides the basic atlas.css version */
#search-results {
  position: fixed;
  top: calc(var(--topbar-h) + 10px);
  left: 50%;
  transform: translateX(-50%);
  width: min(720px, calc(100vw - 2rem));
  max-height: min(68vh, 760px);
  overflow: auto;
  padding: .45rem;
  z-index: 60;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow-hover);
}
#search-results[hidden] { display: none !important; }
#search-results .results-meta {
  padding: .55rem .85rem .65rem;
  margin-bottom: .25rem;
  border-bottom: 1px solid var(--border);
  color: var(--muted-2);
  font-family: var(--font-mono);
  font-size: .72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .08em;
}
#search-results .hit {
  display: block;
  padding: .7rem .85rem;
  border-radius: 8px;
  color: var(--fg);
  text-decoration: none;
}
#search-results .hit:hover,
#search-results .hit.active {
  background: var(--bg);
  text-decoration: none;
}
#search-results .hit.active { outline: 1px solid var(--accent-line); }
#search-results .hit-title { color: var(--fg); font-weight: 700; }
#search-results .meta {
  margin-top: .15rem;
  color: var(--muted);
  font-size: .82rem;
}
#search-results .empty { padding: .8rem; color: var(--muted); }
#search-results mark {
  background: var(--accent-soft);
  color: var(--accent-2);
  border-radius: 2px;
  padding: 0 1px;
}
#search-results .hit p { margin: .25rem 0 0; color: var(--muted); font-size: .86rem; line-height: 1.45; }

.gh-label { display: inline; }
@media (max-width: 860px) {
  .related-grid, .branch-nav { grid-template-columns: 1fr; }
  .branch-nav-link.next { text-align: left; align-items: flex-start; }
  .gh-label { display: none; }
  .github-link { padding: 0; width: 36px; justify-content: center; }
}
@media (max-width: 780px) {
  #search-results { top: 96px; width: calc(100vw - 1.5rem); max-height: 70vh; }
}
"""

SEARCH_JS = r"""
(function () {
  const root = document.body.dataset.root || ".";
  const localeRoot = document.body.dataset.localeRoot || ".";
  const LANG = document.documentElement.lang || "en";
  const I18N = {
    en: { noMatches: "No matches for", result: "result", results: "results", hint: "↑↓ to navigate · ↵ to open" },
    es: { noMatches: "Sin coincidencias para", result: "resultado", results: "resultados", hint: "↑↓ para navegar · ↵ para abrir" },
  };
  const S = I18N[LANG] || I18N.en;
  const input = document.getElementById("search");
  const results = document.getElementById("search-results");
  const toggle = document.getElementById("theme-toggle");
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const sidebar = document.querySelector(".sidebar");

  // Theme toggle — null-guarded so a missing button can't kill the rest of the script.
  const saved = localStorage.getItem("theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  if (toggle) {
    toggle.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", cur);
      localStorage.setItem("theme", cur);
    });
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      document.body.classList.toggle("nav-open");
    });
    // Tap any nav link on mobile → close the drawer so the user lands on the page.
    document.querySelectorAll(".sidebar a").forEach(a => {
      a.addEventListener("click", () => {
        if (window.matchMedia("(max-width: 780px)").matches) {
          document.body.classList.remove("nav-open");
        }
      });
    });
  }

  // Scroll the current page's nav row into view if it's offscreen.
  const activeLink = document.querySelector(
    ".sidebar .nav-leaf.active, .sidebar .nav-child.active, .sidebar .sidebar-link.active"
  );
  if (activeLink) {
    const rect = activeLink.getBoundingClientRect();
    if (rect.top < 80 || rect.bottom > window.innerHeight - 40) {
      activeLink.scrollIntoView({ block: "center" });
    }
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
    if (e.key === "Escape") {
      results.hidden = true;
      document.body.classList.remove("nav-open");
      input.blur();
    }
  });

  let index = null;
  async function loadIndex() {
    if (index) return index;
    const res = await fetch(localeRoot + "/search.json");
    index = await res.json();
    return index;
  }

  function score(entry, terms) {
    const keywords = (entry.keywords || []).join(" ");
    const description = entry.description || "";
    const title = entry.title.toLowerCase();
    const branch = entry.branch.toLowerCase();
    const tags = entry.tags.join(" ").toLowerCase();
    const hay = (
      entry.title + " " +
      keywords + " " +
      description + " " +
      entry.branch + " " +
      entry.group + " " +
      entry.kind + " " +
      entry.tags.join(" ") + " " +
      entry.text
    ).toLowerCase();
    let s = 0;
    for (const t of terms) {
      if (!t) continue;
      if (title.includes(t)) s += 10;
      if (keywords.toLowerCase().includes(t)) s += 8;
      if (tags.includes(t)) s += 6;
      if (branch.includes(t)) s += 4;
      if (entry.kind.toLowerCase().includes(t)) s += 2;
      const occurrences = hay.split(t).length - 1;
      if (!occurrences) return 0;
      s += occurrences;
    }
    return s;
  }

  let debounce;
  let activeIndex = -1;
  let currentHits = [];

  input.addEventListener("focus", () => { loadIndex(); });
  input.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(runSearch, 120);
  });
  input.addEventListener("keydown", (e) => {
    if (results.hidden || !currentHits.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      activeIndex = (activeIndex + 1) % currentHits.length;
      updateActive();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      activeIndex = (activeIndex - 1 + currentHits.length) % currentHits.length;
      updateActive();
    } else if (e.key === "Enter" && activeIndex >= 0) {
      const nodes = results.querySelectorAll(".hit");
      if (nodes[activeIndex]) {
        e.preventDefault();
        window.location.href = nodes[activeIndex].href;
      }
    }
  });

  function updateActive() {
    const nodes = results.querySelectorAll(".hit");
    nodes.forEach((n, i) => n.classList.toggle("active", i === activeIndex));
    if (activeIndex >= 0 && nodes[activeIndex]) {
      nodes[activeIndex].scrollIntoView({ block: "nearest" });
    }
  }

  async function runSearch() {
    const q = input.value.trim().toLowerCase();
    if (!q) { results.hidden = true; results.innerHTML = ""; currentHits = []; activeIndex = -1; return; }
    const terms = q.split(/\s+/).filter(Boolean);
    const idx = await loadIndex();
    const hits = idx.map(e => ({ e, s: score(e, terms) }))
                    .filter(x => x.s > 0)
                    .sort((a, b) => b.s - a.s)
                    .slice(0, 20);
    currentHits = hits;
    activeIndex = hits.length ? 0 : -1;
    if (!hits.length) {
      results.innerHTML = '<div class="empty">' + S.noMatches + ' "' + escapeHtml(q) + '"</div>';
    } else {
      const count = `<div class="results-meta">${hits.length} ${hits.length === 1 ? S.result : S.results} · ${S.hint}</div>`;
      results.innerHTML = count + hits.map((h, i) =>
        `<a class="hit${i === 0 ? " active" : ""}" href="${localeRoot}/${h.e.url}"><div class="hit-title">${highlight(h.e.title, terms)}</div><div class="meta">${escapeHtml(h.e.branch)} · ${escapeHtml(h.e.kind)}</div><p>${highlight(h.e.description || "", terms)}</p></a>`
      ).join("");
    }
    results.hidden = false;
  }

  document.addEventListener("click", (e) => {
    const toggleHit = sidebarToggle && sidebarToggle.contains(e.target);
    const sidebarHit = sidebar && sidebar.contains(e.target);
    if (document.body.classList.contains("nav-open") && !toggleHit && !sidebarHit) {
      document.body.classList.remove("nav-open");
    }
    if (e.target === input) return;
    if (toggleHit) return;
    if (!results.contains(e.target)) results.hidden = true;
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  }

  function highlight(text, terms) {
    const safe = escapeHtml(text);
    const pattern = terms
      .map(t => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
      .filter(Boolean)
      .join("|");
    if (!pattern) return safe;
    return safe.replace(new RegExp("(" + pattern + ")", "gi"), "<mark>$1</mark>");
  }

})();
"""


if __name__ == "__main__":
    sys.exit(main())
