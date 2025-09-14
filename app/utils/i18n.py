# utils/i18n.py
# Simple JSON-based i18n for Streamlit (Py 3.9+)
import os, json
from typing import Dict, Any, Optional
import streamlit as st

_LOCALES_DIR = "data/i18n"
_FALLBACK = "en-US"

# ---- caching (works on older/newer Streamlit) ----
try:
    cache_data = st.cache_data
except AttributeError:
    cache_data = st.cache

def _nested_get(d: Dict[str, Any], key: str) -> Optional[Any]:
    cur = d
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur

@cache_data(show_spinner=False)
def _load_locale(lang: str) -> Dict[str, Any]:
    os.makedirs(_LOCALES_DIR, exist_ok=True)
    path = os.path.join(_LOCALES_DIR, f"{lang}.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def set_language(lang: str):
    """Store current UI language."""
    st.session_state["i18n_lang"] = lang or _FALLBACK

def get_language() -> str:
    return st.session_state.get("i18n_lang", _FALLBACK)

def t(key: str, default: Optional[str] = None, **fmt) -> str:
    """
    Translate a dotted key using current language, fallback to en-US, then to default/key.
    Use Python str.format(**fmt) for variables.
    """
    lang = get_language()
    cur = _load_locale(lang)
    val = _nested_get(cur, key)

    if val is None and lang != _FALLBACK:
        fb = _load_locale(_FALLBACK)
        val = _nested_get(fb, key)

    if val is None:
        val = default if default is not None else key

    try:
        return str(val).format(**fmt) if fmt else str(val)
    except Exception:
        return str(val)

# ---------- seeding & merging ----------

def _deep_merge_missing(dst: Dict[str, Any], src: Dict[str, Any]) -> bool:
    """
    Merge keys that are missing in dst from src (recursive).
    Returns True if dst was modified.
    """
    changed = False
    for k, v in src.items():
        if k not in dst:
            dst[k] = v
            changed = True
        else:
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                if _deep_merge_missing(dst[k], v):
                    changed = True
            # if key exists and is not a dict, we DO NOT overwrite
    return changed

def ensure_seed_files():
    """Create or MERGE minimal locale files on first run. Never overwrites existing keys."""
    os.makedirs(_LOCALES_DIR, exist_ok=True)

    seeds = {
        "en-US.json": {
            "home": {
                "title": "STEMverse Together",
                "subtitle": "Co-op STEM mini-games with accessibility built-in.",
                "quick_start": "Quick Start",
                "demo_checklist": "Demo checklist: Create a profile → Toggle accessibility → Try AR Scanner → Earn coins → Play Heads Up → Clear Treasure Hunt levels → Explore careers."
            },
            "sidebar": {
                "accessibility": "Accessibility Center",
                "tts": "Screen Reader (Read Aloud)",
                "high_contrast": "High Contrast",
                "large_text": "Large Text",
                "reduced_motion": "Reduced Motion",
                "captions": "Captions",
                "transcript": "Transcript panel",
                "language": "Language",
                "wallet": "Wallet",
                "coins": "Coins"
            },
            "profile": {
                "nickname": "Nickname",
                "grade": "Grade",
                "save": "Save Profile",
                "saved": "Profile saved!"
            },
            "nav": {
                "ar": "AR Scanner",
                "heads_up": "Heads Up",
                "treasure": "Treasure Hunt 3D",
                "tutor": "AI Tutor",
                "careers": "Career Explorer",
                "buddy": "Buddy Program",
                "admin": "Admin Content"
            },
            "buddy": {
                "title": "Buddy Program",
                "enter_code": "Enter / Create room code",
                "create_join": "Create/Join Room",
                "generate": "Generate code",
                "room": "Room",
                "invite_link": "Invite link",
                "members": "Members",
                "mentor_ping": "Mentor Ping",
                "chat_placeholder": "Type and press Enter…",
                "chat": "Chat",
                "coop": "Co-op Launchers"
            },
            "ar": {
                "title": "AI AR Scanner",
                "hint": "Upload an image (circuit, plant, code screenshot, bicycle). AI analyzes it and explains what it sees. If AI is unavailable, we fall back to the offline detector.",
                "upload": "Upload image",
                "capture": "Or capture from camera",
                "no_text": "No textual response.",
                "no_concept": "No mapped concept content yet.",
                "explainer": "Explainer Video",
                "tts_intro": "Here are key ideas related to the detected concept.",
                "concept_error": "Concept content not available (check data/concepts.json).",
                "input": "Input",
                "ai_analysis": "AI Analysis",
                "domain": "Domain",
                "tags": "Tags",
                "summary": "Summary",
                "explanation": "Explanation",
                "language": "Language",
                "fallback": "AI analysis unavailable; using offline detector.",
                "detected_qr": "QR code detected.",
                "detected_template": "Template detected.",
                "detected_heur": "Heuristic match",
                "no_match": "No detection.",
                "no_match2": "No QR/marker/heuristic match.",
                "score": "Detection score",
                "tip": "Tip: try a circuit diagram, plant photo, code screenshot, or the bicycle marker."
            },
            "heads": {
                "title": "Heads Up",
                "solo": "Solo",
                "buddy": "Buddy",
                "mode": "Mode",
                "difficulty": "Difficulty",
                "start": "Start / Restart",
                "score": "Score",
                "correct": "Correct",
                "skip": "Skip",
                "complete": "Round complete!",
                "buddy_tip": "Buddy mode: join or create a room on the Buddy Program page, then return here.",
                "buddy_tip_with_room": "Buddy mode: you’re in room **{room}**. Use the same page together."
            }
        },
        "es-ES.json": {
            "home": {
                "title": "STEMverse Juntos",
                "subtitle": "Minijuegos STEM en cooperativo con accesibilidad integrada.",
                "quick_start": "Inicio rápido",
                "demo_checklist": "Guía: Crea un perfil → Ajusta accesibilidad → Prueba el escáner AR → Gana monedas → Juega Heads Up → Completa el tesoro → Explora carreras."
            },
            "sidebar": {
                "accessibility": "Centro de Accesibilidad",
                "tts": "Lector (Leer en voz alta)",
                "high_contrast": "Alto contraste",
                "large_text": "Texto grande",
                "reduced_motion": "Movimiento reducido",
                "captions": "Subtítulos",
                "transcript": "Panel de transcripción",
                "language": "Idioma",
                "wallet": "Monedero",
                "coins": "Monedas"
            },
            "profile": {
                "nickname": "Apodo",
                "grade": "Curso",
                "save": "Guardar perfil",
                "saved": "¡Perfil guardado!"
            },
            "nav": {
                "ar": "Escáner AR",
                "heads_up": "Heads Up",
                "treasure": "Búsqueda del Tesoro 3D",
                "tutor": "Tutor IA",
                "careers": "Explorador de Carreras",
                "buddy": "Programa de Compañeros",
                "admin": "Contenido Admin"
            },
            "buddy": {
                "title": "Programa de Compañeros",
                "enter_code": "Introduce / Crea código de sala",
                "create_join": "Crear/Unirse",
                "generate": "Generar código",
                "room": "Sala",
                "invite_link": "Enlace de invitación",
                "members": "Miembros",
                "mentor_ping": "Llamar mentor",
                "chat_placeholder": "Escribe y pulsa Enter…",
                "chat": "Chat",
                "coop": "Lanzadores co-op"
            },
            "ar": {
                "title": "Escáner AR con IA",
                "hint": "Sube una imagen (circuito, planta, captura de código, bicicleta). La IA la analiza y explica lo que ve. Si la IA no está disponible, usamos el detector sin conexión.",
                "upload": "Subir imagen",
                "capture": "O capturar con la cámara",
                "no_text": "Sin respuesta textual.",
                "no_concept": "Aún no hay contenido mapeado para este concepto.",
                "explainer": "Vídeo explicativo",
                "tts_intro": "Aquí tienes ideas clave relacionadas con el concepto detectado.",
                "concept_error": "Contenido no disponible (revisa data/concepts.json).",
                "input": "Entrada",
                "ai_analysis": "Análisis con IA",
                "domain": "Dominio",
                "tags": "Etiquetas",
                "summary": "Resumen",
                "explanation": "Explicación",
                "language": "Lenguaje",
                "fallback": "Análisis con IA no disponible; usando detector sin conexión.",
                "detected_qr": "Código QR detectado.",
                "detected_template": "Plantilla detectada.",
                "detected_heur": "Coincidencia heurística",
                "no_match": "Sin detección.",
                "no_match2": "Sin coincidencia de QR/marcador/heurística.",
                "score": "Puntuación de detección",
                "tip": "Consejo: prueba un diagrama de circuito, foto de una planta, captura de código o el marcador de bicicleta."
            },
            "heads": {
                "title": "Heads Up",
                "solo": "Individual",
                "buddy": "Compañero",
                "mode": "Modo",
                "difficulty": "Dificultad",
                "start": "Iniciar / Reiniciar",
                "score": "Puntos",
                "correct": "Correcto",
                "skip": "Saltar",
                "complete": "¡Ronda completada!",
                "buddy_tip": "Modo compañero: crea o únete a una sala en la página Programa de Compañeros y vuelve aquí.",
                "buddy_tip_with_room": "Modo compañero: estás en la sala **{room}**. Usen esta página juntos."
            }
        },
        "fr-FR.json": {
            "home": {
                "title": "STEMverse Ensemble",
                "subtitle": "Mini-jeux STEM en coopération avec accessibilité intégrée.",
                "quick_start": "Démarrage rapide",
                "demo_checklist": "Parcours : Créer un profil → Régler l’accessibilité → Essayer le scanner AR → Gagner des pièces → Jouer à Heads Up → Finir la chasse au trésor → Explorer les métiers."
            },
            "sidebar": {
                "accessibility": "Centre d’Accessibilité",
                "tts": "Lecteur vocal",
                "high_contrast": "Haut contraste",
                "large_text": "Texte large",
                "reduced_motion": "Mouvements réduits",
                "captions": "Sous-titres",
                "transcript": "Panneau de transcription",
                "language": "Langue",
                "wallet": "Portefeuille",
                "coins": "Pièces"
            },
            "profile": {
                "nickname": "Surnom",
                "grade": "Niveau",
                "save": "Enregistrer le profil",
                "saved": "Profil enregistré !"
            },
            "nav": {
                "ar": "Scanner AR",
                "heads_up": "Heads Up",
                "treasure": "Chasse au trésor 3D",
                "tutor": "Tuteur IA",
                "careers": "Explorateur de métiers",
                "buddy": "Programme binôme",
                "admin": "Contenu Admin"
            },
            "buddy": {
                "title": "Programme binôme",
                "enter_code": "Entrer / Créer un code de salle",
                "create_join": "Créer/Rejoindre",
                "generate": "Générer un code",
                "room": "Salle",
                "invite_link": "Lien d’invitation",
                "members": "Membres",
                "mentor_ping": "Appel mentor",
                "chat_placeholder": "Écrivez et appuyez sur Entrée…",
                "chat": "Chat",
                "coop": "Lanceurs co-op"
            },
            "ar": {
                "title": "Scanner AR avec IA",
                "hint": "Importez une image (circuit, plante, capture de code, vélo). L’IA l’analyse et explique ce qu’elle voit. Si l’IA est indisponible, on utilise le détecteur hors ligne.",
                "upload": "Téléverser une image",
                "capture": "Ou prendre une photo",
                "no_text": "Aucune réponse textuelle.",
                "no_concept": "Pas encore de contenu associé à ce concept.",
                "explainer": "Vidéo explicative",
                "tts_intro": "Voici des idées clés liées au concept détecté.",
                "concept_error": "Contenu indisponible (vérifiez data/concepts.json).",
                "input": "Entrée",
                "ai_analysis": "Analyse IA",
                "domain": "Domaine",
                "tags": "Étiquettes",
                "summary": "Résumé",
                "explanation": "Explication",
                "language": "Langue",
                "fallback": "Analyse IA indisponible ; utilisation du détecteur hors ligne.",
                "detected_qr": "Code QR détecté.",
                "detected_template": "Gabarit détecté.",
                "detected_heur": "Correspondance heuristique",
                "no_match": "Aucune détection.",
                "no_match2": "Aucune correspondance QR/marqueur/heuristique.",
                "score": "Score de détection",
                "tip": "Astuce : essayez un schéma de circuit, une photo de plante, une capture de code ou le marqueur vélo."
            },
            "heads": {
                "title": "Heads Up",
                "solo": "Solo",
                "buddy": "Binôme",
                "mode": "Mode",
                "difficulty": "Difficulté",
                "start": "Démarrer / Recommencer",
                "score": "Score",
                "correct": "Correct",
                "skip": "Passer",
                "complete": "Manche terminée !",
                "buddy_tip": "Mode binôme : créez ou rejoignez une salle sur la page Programme binôme, puis revenez ici.",
                "buddy_tip_with_room": "Mode binôme : vous êtes dans la salle **{room}**. Utilisez cette page ensemble."
            }
        }
    }

    updated_any = False
    for fname, seed_data in seeds.items():
        path = os.path.join(_LOCALES_DIR, fname)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    current = json.load(f)
            except Exception:
                current = {}
            if _deep_merge_missing(current, seed_data):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(current, f, ensure_ascii=False, indent=2)
                updated_any = True
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(seed_data, f, ensure_ascii=False, indent=2)
            updated_any = True

    # Clear cache so future t(...) calls see new/merged content
    try:
        _load_locale.clear()
    except Exception:
        pass

# --- Simple bootstrap so every page loads the chosen language ---
def init_from_session_or_db(default: str = "en-US", db_path: str = "", uid: str = "") -> str:
    """
    Ensure i18n has a language set on this page:
      1) Use st.session_state["a11y_lang"] if present,
      2) else (optionally) read from DB user prefs if available,
      3) else fall back to `default`.
    Returns the language code used.
    """
    import importlib
    lang = st.session_state.get("a11y_lang")

    if not lang and db_path and uid:
        try:
            db = importlib.import_module("utils.db")
            if hasattr(db, "get_prefs"):
                prefs = db.get_prefs(db_path, uid)
                if isinstance(prefs, dict):
                    lang = prefs.get("lang") or lang
        except Exception:
            pass

    if not lang:
        lang = default

    st.session_state["a11y_lang"] = lang
    set_language(lang)
    return lang
