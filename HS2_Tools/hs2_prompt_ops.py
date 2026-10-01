#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hs2_prompt_ops.py — pilotage par prompt des renforts (support) et des délais
d'arrivée (scripts2) pour le Mission Editor.

Principe : le LLM ne touche jamais aux fichiers. Il traduit une demande en
français/anglais en une liste d'OPÉRATIONS JSON bornées. Ce module les valide,
les applique sur les objets déjà parsés par l'éditeur (donc round-trip
octet-pour-octet des lignes non modifiées, taille des scripts recalculée,
backup horodaté à la sauvegarde) et produit un aperçu avant écriture.

Opérations :
  set_unit_fields {blocks, unit_id?, level?, fields{hp,ammo,expa,morale,lives,grp,crew}}
  add_unit        {block, unit_id, count?, fields?}      (clone une ligne existante si possible)
  remove_unit     {block, unit_id, count|"all"}
  set_timing      {script?, kind?, block?, line?, seconds | shift_seconds}

Stdlib uniquement. Fournisseurs LLM : "openai" (API compatible OpenAI : Ollama,
llama.cpp, LM Studio, vLLM… en local) ou "anthropic".
"""

import copy
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "llm_config.json"

FIELD_RANGE = {
    "hp": (-1, 100),
    "ammo": (-1, 100),
    "expa": (-1, 100),
    "morale": (-1, 100),
    "lives": (0, 100),
    "grp": (-1, 99),
    "crew": (0, 31),
}
DEFAULT_UNIT = {"hp": 100, "ammo": 100, "expa": -1, "morale": -1, "lives": 0, "grp": -1}


# ---------------------------------------------------------------------------
# timings (miroir de parseTimings() côté JS : "$T" suivi de "#chiffres inversés")
# ---------------------------------------------------------------------------


def rev_digits(d):
    """Nombre stocké chiffres inversés ; vide -> 0 ; non numérique -> None."""
    d = d.strip()
    if not d:
        return 0
    return int(d[::-1]) if d.isdigit() else None


def to_rev(n):
    return str(int(n))[::-1]


def parse_timings(text):
    lines = text.split("\n")
    out = []
    for i in range(len(lines) - 1):
        if lines[i].strip() != "$T" or not lines[i + 1].startswith("#"):
            continue
        digits = lines[i + 1][1:].strip()
        if digits and not digits.isdigit():
            continue
        prev = lines[i - 1].strip() if i > 0 else ""
        kind, slots, mask = "trigger", None, None
        if prev in ("$sres5", "$fres5"):
            kind = "timed" if prev == "$sres5" else "flag"
            slots = []
            for j in range(i - 2, max(0, i - 30) - 1, -1):
                t = lines[j].strip()
                if t.startswith("#") and j > 0 and lines[j - 1].strip() == "$resv":
                    slots.insert(0, rev_digits(t[1:]))
                if t == "$Fmask" and j + 1 < len(lines) and lines[j + 1].startswith("#"):
                    mask = rev_digits(lines[j + 1][1:])
                if t in ("$sres", "$fres"):
                    break
        out.append(
            {"line": i + 1, "secs": rev_digits(digits), "kind": kind, "slots": slots, "mask": mask}
        )
    return out


# ---------------------------------------------------------------------------
# contexte compact envoyé au LLM (aucun fichier du jeu, juste le résumé)
# ---------------------------------------------------------------------------


def _unit_sig(u):
    return (u["id"], u["hp"], u["ammo"], u["expa"], u["morale"], u["grp"], u.get("crew"), len(u.get("passengers", [])))


def build_context(support, scripts, unit_names):
    blocks = []
    for bi, b in enumerate(support["blocks"]):
        groups, order = {}, []
        for u in b["units"]:
            s = _unit_sig(u)
            if s not in groups:
                groups[s] = 0
                order.append(s)
            groups[s] += 1
        blocks.append(
            {
                "block": bi,
                "name": b["name"],
                "units": [
                    {"id": s[0], "n": groups[s], "hp": s[1], "ammo": s[2], "expa": s[3],
                     "morale": s[4], "grp": s[5], "crew": s[6], "passengers": s[7]}
                    for s in order
                ],
            }
        )
    timings = []
    if scripts:
        for si, sc in enumerate(scripts["scripts"]):
            for t in parse_timings(sc["text"]):
                timings.append(
                    {"script": sc["name"], "line": t["line"], "kind": t["kind"],
                     "seconds": t["secs"], "support_blocks": t["slots"], "flag_mask": t["mask"]}
                )
    used = {u["id"] for b in support["blocks"] for u in b["units"]}
    catalog = {k: v for k, v in unit_names.items()}
    return {"support_blocks": blocks, "arrival_timings": timings,
            "known_unit_ids": {k: (v[0] or "")[:32] for k, v in catalog.items()} if catalog else sorted(used)}


OPS_DOC = """Opérations autorisées (rien d'autre) :
- {"op":"set_unit_fields","blocks":"all"|<int>|[<int>...],"unit_id":<id|null>,"level":"top"|"passengers"|"all","fields":{"hp":..,"ammo":..,"expa":..,"morale":..,"lives":..,"grp":..,"crew":..}}
- {"op":"add_unit","block":<int>,"unit_id":<id>,"count":<int>,"fields":{...}}
- {"op":"remove_unit","block":<int>,"unit_id":<id>,"count":<int>|"all"}
- {"op":"set_timing","script":<nom|null>,"kind":"timed"|"flag"|"trigger"|null,"block":<int|null>,"line":<int|null>,"seconds":<int>}  ou  "shift_seconds":<int> (relatif, peut être négatif)
"""

OPS_RULES = """Règles :
- "block" = indice 0-based du bloc support. "set_timing" avec "block" cible les arrivées qui livrent ce bloc.
- Les délais sont en SECONDES (10 min = 600). Plage 0..86400.
- Plages : hp/ammo/expa/morale -1..100 (-1 = défaut), lives 0..100, grp -1..99, crew 0..31.
- unit_id doit exister dans known_unit_ids. Si tu n'es pas sûr, ne l'invente pas : renvoie ops=[] et explique.
- Ne fais que ce qui est demandé. Demande ambiguë : ops=[] et explication courte de ce qu'il manque.
"""

SYSTEM_PROMPT = """Tu pilotes l'éditeur de missions de Hidden Stroke II / Sudden Strike.
Tu reçois l'état d'une mission (blocs de renforts "support", délais d'arrivée en secondes)
et une demande en langage naturel. Tu réponds UNIQUEMENT par un objet JSON :
{"explanation": "<une phrase>", "ops": [ ... ]}
Aucun texte hors JSON, aucun bloc markdown.

""" + OPS_DOC + "\n" + OPS_RULES


# ---------------------------------------------------------------------------
# client LLM (stdlib)
# ---------------------------------------------------------------------------


def load_config():
    cfg = {
        "provider": "openai",
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:14b-instruct",
        "api_key_env": "HS2_LLM_API_KEY",
        "timeout": 180,
    }
    if CONFIG_PATH.is_file():
        try:
            cfg.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return cfg


def public_config():
    c = load_config()
    key = os.environ.get(c.get("api_key_env", ""), "") or c.get("api_key", "")
    return {"provider": c["provider"], "model": c["model"],
            "base_url": c.get("base_url") if c["provider"] == "openai" else "https://api.anthropic.com",
            "has_key": bool(key), "config_file": str(CONFIG_PATH), "config_exists": CONFIG_PATH.is_file()}


def _http_json(url, headers, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                 headers=dict(headers, **{"Content-Type": "application/json"}))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("LLM HTTP %d : %s" % (e.code, e.read().decode("utf-8", "replace")[:400]))
    except urllib.error.URLError as e:
        raise RuntimeError("LLM injoignable (%s). Vérifie llm_config.json / le serveur local." % e.reason)


def call_llm(system, user):
    c = load_config()
    key = os.environ.get(c.get("api_key_env", ""), "") or c.get("api_key", "")
    if c["provider"] == "anthropic":
        if not key:
            raise RuntimeError("Clé API absente : exporte %s." % c.get("api_key_env", "HS2_LLM_API_KEY"))
        j = _http_json(
            "https://api.anthropic.com/v1/messages",
            {"x-api-key": key, "anthropic-version": "2023-06-01"},
            {"model": c["model"], "max_tokens": 4000, "system": system,
             "messages": [{"role": "user", "content": user}]},
            c["timeout"],
        )
        return "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text")
    headers = {"Authorization": "Bearer " + key} if key else {}
    j = _http_json(
        c["base_url"].rstrip("/") + "/chat/completions", headers,
        {"model": c["model"], "temperature": 0,
         "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
        c["timeout"],
    )
    return j["choices"][0]["message"]["content"]


def extract_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    a, b = text.find("{"), text.rfind("}")
    if a < 0 or b < a:
        raise ValueError("réponse LLM sans JSON")
    return json.loads(text[a : b + 1])


def plan(prompt, support, scripts, unit_names):
    ctx = build_context(support, scripts, unit_names)
    user = "ÉTAT DE LA MISSION :\n%s\n\nDEMANDE :\n%s" % (json.dumps(ctx, ensure_ascii=False), prompt)
    out = extract_json(call_llm(SYSTEM_PROMPT, user))
    return {"explanation": str(out.get("explanation", "")), "ops": out.get("ops", [])}


# ---------------------------------------------------------------------------
# application des opérations (validation stricte : une erreur = rien n'est appliqué)
# ---------------------------------------------------------------------------


def _resolve_blocks(sel, support, errors):
    n = len(support["blocks"])
    if sel in ("all", None):
        return list(range(n))
    items = sel if isinstance(sel, list) else [sel]
    out = []
    for it in items:
        if isinstance(it, int) and 0 <= it < n:
            out.append(it)
        elif isinstance(it, str) and it.strip().lstrip("-").isdigit() and 0 <= int(it) < n:
            out.append(int(it))
        elif isinstance(it, str):
            hit = [i for i, b in enumerate(support["blocks"]) if b["name"] == it]
            if hit:
                out.extend(hit)
            else:
                errors.append("bloc inconnu : %r" % (it,))
        else:
            errors.append("bloc hors plage : %r (0..%d)" % (it, n - 1))
    return out


def _check_fields(fields, errors, top_only=False):
    clean = {}
    if not isinstance(fields, dict) or not fields:
        errors.append("fields vide ou invalide")
        return clean
    for k, v in fields.items():
        k = k.lower()
        if k not in FIELD_RANGE:
            errors.append("champ inconnu : %s" % k)
        elif not isinstance(v, int) or isinstance(v, bool):
            errors.append("%s : entier attendu" % k)
        elif not FIELD_RANGE[k][0] <= v <= FIELD_RANGE[k][1]:
            errors.append("%s=%d hors plage %s" % (k, v, FIELD_RANGE[k]))
        else:
            clean[k] = v
    return clean


def apply_ops(support, scripts, ops, unit_ids=None):
    """Retourne (support', scripts', changes, warnings, errors). Objets d'entrée non modifiés."""
    support = copy.deepcopy(support)
    scripts = copy.deepcopy(scripts)
    changes, warnings, errors = [], [], []
    if not isinstance(ops, list):
        return support, scripts, [], [], ["ops doit être une liste"]

    def known(uid):
        if not unit_ids:
            return True
        return uid in unit_ids

    for n, op in enumerate(ops, 1):
        tag = "op %d (%s)" % (n, op.get("op") if isinstance(op, dict) else "?")
        e0 = len(errors)
        if not isinstance(op, dict):
            errors.append("%s : objet attendu" % tag)
            continue
        kind = op.get("op")

        if kind == "set_unit_fields":
            level = op.get("level") or "top"
            if level not in ("top", "passengers", "all"):
                errors.append("%s : level invalide" % tag)
            fields = _check_fields(op.get("fields"), errors)
            blocks = _resolve_blocks(op.get("blocks"), support, errors)
            uid = op.get("unit_id")
            if uid and not known(uid):
                errors.append("%s : unit_id inconnu %r" % (tag, uid))
            if len(errors) > e0:
                errors[e0:] = ["%s : %s" % (tag, x) if not x.startswith("op ") else x for x in errors[e0:]]
                continue
            touched = 0
            for bi in blocks:
                for u in support["blocks"][bi]["units"]:
                    targets = []
                    if level in ("top", "all"):
                        targets.append((u, True))
                    if level in ("passengers", "all"):
                        targets += [(p, False) for p in u.get("passengers", [])]
                    for t, is_top in targets:
                        if uid and t["id"] != uid:
                            continue
                        mod = False
                        for k, v in fields.items():
                            if k == "crew":
                                if not is_top or t.get("crew") is None:
                                    continue
                            if t.get(k) != v:
                                t[k] = v
                                mod = True
                        if mod:
                            t["dirty"] = True
                            touched += 1
            if touched == 0:
                warnings.append("%s : aucune unité modifiée (déjà à la valeur, ou filtre sans résultat)" % tag)
            else:
                changes.append("%s : %d ligne(s) → %s%s" % (
                    tag, touched, ", ".join("%s=%d" % kv for kv in fields.items()),
                    " [unit_id=%s]" % uid if uid else ""))

        elif kind == "add_unit":
            blocks = _resolve_blocks(op.get("block"), support, errors)
            uid = op.get("unit_id")
            count = op.get("count", 1)
            if len(blocks) != 1:
                errors.append("%s : un seul bloc attendu" % tag)
            if not uid or not known(uid):
                errors.append("%s : unit_id inconnu %r" % (tag, uid))
            if not isinstance(count, int) or not 1 <= count <= 50:
                errors.append("%s : count 1..50" % tag)
            fields = _check_fields(op["fields"], errors) if op.get("fields") else {}
            if len(errors) > e0:
                continue
            blk = support["blocks"][blocks[0]]
            # modèle : une ligne existante du même id (dans le bloc, sinon dans la mission)
            tpl = next((u for u in blk["units"] if u["id"] == uid), None) or next(
                (u for b in support["blocks"] for u in b["units"] if u["id"] == uid), None)
            for _ in range(count):
                if tpl:
                    nu = copy.deepcopy(tpl)
                else:
                    nu = dict(DEFAULT_UNIT, id=uid, crew=None, inn=None, passengers=[])
                nu.update(fields)
                nu["dirty"] = True
                nu.pop("raw", None)
                for p in nu.get("passengers", []):
                    p["dirty"] = True
                    p.pop("raw", None)
                blk["units"].append(nu)
            if not tpl:
                warnings.append("%s : %s absent de la mission, créé avec les valeurs par défaut "
                                "(Crew/In non renseignés — vérifie en jeu pour un véhicule)." % (tag, uid))
            changes.append("%s : +%d × %s dans le bloc %d (%s)" % (tag, count, uid, blocks[0], blk["name"]))

        elif kind == "remove_unit":
            blocks = _resolve_blocks(op.get("block"), support, errors)
            uid, count = op.get("unit_id"), op.get("count", 1)
            if len(blocks) != 1:
                errors.append("%s : un seul bloc attendu" % tag)
            if not uid:
                errors.append("%s : unit_id requis" % tag)
            if count != "all" and (not isinstance(count, int) or count < 1):
                errors.append("%s : count entier>=1 ou \"all\"" % tag)
            if len(errors) > e0:
                continue
            blk = support["blocks"][blocks[0]]
            idxs = [i for i, u in enumerate(blk["units"]) if u["id"] == uid]
            if not idxs:
                warnings.append("%s : aucun %s dans le bloc %d" % (tag, uid, blocks[0]))
                continue
            drop = idxs if count == "all" else idxs[-count:]
            blk["units"] = [u for i, u in enumerate(blk["units"]) if i not in drop]
            changes.append("%s : −%d × %s du bloc %d" % (tag, len(drop), uid, blocks[0]))

        elif kind == "set_timing":
            if scripts is None:
                errors.append("%s : pas de fichier scripts2 structuré" % tag)
                continue
            has_abs, has_rel = "seconds" in op, "shift_seconds" in op
            if has_abs == has_rel:
                errors.append("%s : seconds OU shift_seconds" % tag)
                continue
            val = op["seconds"] if has_abs else op["shift_seconds"]
            if not isinstance(val, int) or isinstance(val, bool):
                errors.append("%s : entier attendu" % tag)
                continue
            if has_abs and not 0 <= val <= 86400:
                errors.append("%s : seconds=%d hors 0..86400" % (tag, val))
                continue
            want_kind, want_script, want_line = op.get("kind"), op.get("script"), op.get("line")
            want_block = op.get("block")
            if want_kind not in (None, "timed", "flag", "trigger"):
                errors.append("%s : kind invalide" % tag)
                continue
            done = 0
            for si, sc in enumerate(scripts["scripts"]):
                if want_script is not None and want_script not in (sc["name"], si):
                    continue
                lines = sc["text"].split("\n")
                for t in parse_timings(sc["text"]):
                    if want_kind and t["kind"] != want_kind:
                        continue
                    if want_line is not None and t["line"] != want_line:
                        continue
                    if want_block is not None and (t["slots"] is None or want_block not in t["slots"]):
                        continue
                    new = val if has_abs else t["secs"] + val
                    if not 0 <= new <= 86400:
                        warnings.append("%s : %s l.%d : %d s ramené dans 0..86400" % (tag, sc["name"], t["line"], new))
                        new = min(max(new, 0), 86400)
                    if new != t["secs"]:
                        lines[t["line"]] = "#" + to_rev(new)  # "line" = index 0-based de la ligne "#chiffres" (juste après "$T")
                        changes.append("%s : %s l.%d (%s) %d s → %d s" % (
                            tag, sc["name"], t["line"], t["kind"], t["secs"], new))
                    done += 1
                sc["text"] = "\n".join(lines)
            if done == 0 and len(errors) == e0:
                warnings.append("%s : aucun délai ne correspond au filtre" % tag)
        else:
            errors.append("%s : opération inconnue" % tag)

    return support, scripts, changes, warnings, errors
