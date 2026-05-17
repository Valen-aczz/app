"""
string_api.py
─────────────────────────────────────────────────────────────────────
Módulo para conectar con la STRING Database API en tiempo real.
No requiere API key para uso académico.

Cómo usar:
    from string_api import enriquecer_par, regenerar_conocimiento_biologico
"""

import requests
import time

# ── Configuración STRING API ──────────────────────────────────────────
STRING_BASE    = "https://string-db.org/api"
FORMATO        = "json"
ESPECIE_HUMANA = 9606
CALLER_ID      = "ppi_explorer"


# ── Carga del diccionario de traducción desde traducciones.tsv ───────
import os as _os

def _cargar_traducciones() -> dict:
    """
    Lee traducciones.tsv (mismo directorio que string_api.py).
    Formato por línea: término_inglés [TAB] traducción_español
    Líneas vacías y que empiecen con # se ignoran.
    """
    ruta = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "traducciones.tsv")
    tabla = {}
    try:
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                partes = linea.split("\t", 1)
                if len(partes) == 2:
                    clave, valor = partes
                    tabla[clave.strip().lower()] = valor.strip()
    except FileNotFoundError:
        pass
    return tabla

_TRADUCCIONES = _cargar_traducciones()

# BLOQUE ELIMINADO — diccionario hardcodeado reemplazado por TSV
def _traducir(texto: str) -> str:
    """Traduce un término usando el diccionario local. Case-insensitive."""
    return _TRADUCCIONES.get(texto.strip().lower(), texto)


def _traducir_lista(textos: list) -> list:
    return [_traducir(t) for t in textos]


# ── Función principal ─────────────────────────────────────────────────
def enriquecer_par(proteina_a: str, proteina_b: str) -> dict:
    ids = _resolver_ids([proteina_a, proteina_b])
    if not ids or len(ids) < 2:
        return _fallback(proteina_a, proteina_b, "No se encontraron IDs en STRING")

    id_a = ids.get(proteina_a.upper())
    id_b = ids.get(proteina_b.upper())

    if not id_a or not id_b:
        return _fallback(proteina_a, proteina_b, "Proteína no encontrada en STRING")

    score_info = _obtener_interaccion(id_a, id_b)
    func_a     = _obtener_funcion(id_a, proteina_a)
    func_b     = _obtener_funcion(id_b, proteina_b)

    return _construir_anotacion(proteina_a, proteina_b, func_a, func_b, score_info)


# ── Regenerar diccionario completo ────────────────────────────────────
def regenerar_conocimiento_biologico(pares: list, callback=None) -> dict:
    resultado = {}
    total = len(pares)
    for i, (a, b) in enumerate(pares):
        if callback:
            callback(i, total, (a, b))
        resultado[frozenset({a, b})] = enriquecer_par(a, b)
        time.sleep(0.3)
    return resultado


# ── Helpers ───────────────────────────────────────────────────────────

def _resolver_ids(nombres: list) -> dict:
    try:
        resp = requests.get(
            f"{STRING_BASE}/{FORMATO}/get_string_ids",
            params={"identifiers": "%0d".join(nombres), "species": ESPECIE_HUMANA,
                    "limit": 1, "caller_identity": CALLER_ID},
            timeout=10,
        )
        resp.raise_for_status()
        return {
            item.get("queryItem", "").upper(): item.get("stringId", "")
            for item in resp.json()
            if item.get("queryItem") and item.get("stringId")
        }
    except Exception:
        return {}


def _obtener_interaccion(id_a: str, id_b: str) -> dict:
    try:
        resp = requests.get(
            f"{STRING_BASE}/{FORMATO}/network",
            params={"identifiers": f"{id_a}%0d{id_b}", "species": ESPECIE_HUMANA,
                    "caller_identity": CALLER_ID},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            item = data[0]
            return {
                "score":  item.get("score",  0),
                "escore": item.get("escore", 0),
                "dscore": item.get("dscore", 0),
                "tscore": item.get("tscore", 0),
            }
    except Exception:
        pass
    return {}


def _obtener_funcion(string_id: str, nombre: str) -> dict:
    try:
        resp = requests.get(
            f"{STRING_BASE}/{FORMATO}/functional_annotation",
            params={"identifiers": string_id, "species": ESPECIE_HUMANA,
                    "caller_identity": CALLER_ID},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        procesos = _traducir_lista(
            [d["description"] for d in data if d.get("category") == "Process"][:3])
        kegg = _traducir_lista(
            [d["description"] for d in data if d.get("category") == "KEGG"][:3])
        return {"nombre": nombre, "procesos": procesos, "kegg": kegg}
    except Exception:
        return {"nombre": nombre, "procesos": [], "kegg": []}


def _construir_anotacion(a, b, func_a, func_b, score_info):
    texto_a = "; ".join(func_a.get("procesos", [])) or "No disponible en STRING"
    texto_b = "; ".join(func_b.get("procesos", [])) or "No disponible en STRING"
    funcion = f"{a}: {texto_a} | {b}: {texto_b}"

    kegg_a = set(func_a.get("kegg", []))
    kegg_b = set(func_b.get("kegg", []))
    vias   = kegg_a & kegg_b

    escore = score_info.get("escore", 0)
    dscore = score_info.get("dscore", 0)
    tscore = score_info.get("tscore", 0)

    mecanismo = (
        f"Vías compartidas (KEGG): {', '.join(vias)}. " if vias
        else "Sin vías KEGG compartidas detectadas en STRING. "
    )
    mecanismo += (
        f"Evidencia experimental: {escore:.3f} | "
        f"Bases de datos curadas: {dscore:.3f} | "
        f"Minería de texto: {tscore:.3f}."
    )

    tipo = _inferir_tipo(escore, dscore, tscore)

    kegg_todos = list(kegg_a | kegg_b)
    palabras_cancer = ["cáncer", "cancer", "carcinoma", "tumor",
                       "oncogénesis", "leucemia", "melanoma", "glioma"]
    cancer_terms = [k for k in kegg_todos
                    if any(w in k.lower() for w in palabras_cancer)]
    cancer_info = (
        f"Presente en vías de cáncer (STRING): {', '.join(cancer_terms)}."
        if cancer_terms
        else "No se encontraron vías de cáncer directas en STRING para este par."
    )

    return {
        "funcion":         funcion,
        "mecanismo":       mecanismo,
        "cancer":          cancer_info,
        "tipo":            tipo,
        "escore":          escore,
        "dscore":          dscore,
        "tscore":          tscore,
        "score_combinado": score_info.get("score", 0),
    }


def _inferir_tipo(escore, dscore, tscore):
    scores = {
        "Evidencia experimental directa":                 escore,
        "Interacción curada en bases de datos":           dscore,
        "Co-ocurrencia en literatura (minería de texto)": tscore,
    }
    if max(scores.values()) == 0:
        return "Desconocido"
    return max(scores, key=scores.get)


def _fallback(a, b, razon):
    return {
        "funcion":         f"No disponible — {razon}",
        "mecanismo":       "Consulta STRING manualmente en https://string-db.org",
        "cancer":          "Sin datos disponibles",
        "tipo":            "Desconocido",
        "escore":          0,
        "dscore":          0,
        "tscore":          0,
        "score_combinado": 0,
    }