#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hs2_mcp_server.py — serveur MCP (stdio, stdlib uniquement) pour piloter le Mission Editor
depuis Claude Desktop (ou tout client MCP). Claude fait office de LLM : pas d'Ollama, pas de clé.

Outils :
  list_missions       cartes/missions disponibles (filtre texte)
  get_mission_context résumé compact : blocs de renforts, délais d'arrivée, ids d'unités
  search_units        recherche d'identifiants d'unités
  preview_ops         valide + montre les changements, renvoie un `token`
  apply_ops           écrit (backup horodaté) UNIQUEMENT avec le token d'un aperçu identique

Config : variable HS2_GAME_ROOT (racine du jeu) ou HS2_MAPS_DIR (maps_ap.src directement).
Sauvegardes : <dossier du script>/backups, ou HS2_BACKUP_DIR.
"""
import json
import os
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.argv = sys.argv[:1]  # le module éditeur lit argv[1] à l'import

import hs2_mission_editor as E  # noqa: E402
import hs2_prompt_ops as P  # noqa: E402

if os.environ.get("HS2_MAPS_DIR"):
    E.MAPS_DIR = Path(os.environ["HS2_MAPS_DIR"])
if os.environ.get("HS2_BACKUP_DIR"):
    E.BACKUP_DIR = Path(os.environ["HS2_BACKUP_DIR"])

SUPPORTED = ["2025-06-18", "2025-03-26", "2024-11-05"]
MAPREF = {"map": {"type": "string", "description": "id de la carte, ex. map.023"},
          "mis": {"type": "string", "description": "id de la mission, ex. mis.000"}}
OPS_PROP = {"type": "array", "items": {"type": "object"},
            "description": "Liste d'opérations JSON. Format :\n" + P.OPS_DOC + "\n" + P.OPS_RULES}

TOOLS = [
    {"name": "list_missions", "description": "Liste les cartes et missions éditables. Filtre texte optionnel.",
     "inputSchema": {"type": "object", "properties": {"filter": {"type": "string"}, "limit": {"type": "integer", "default": 60}}},
     "annotations": {"readOnlyHint": True}},
    {"name": "get_mission_context",
     "description": "État compact d'une mission : blocs support (unités regroupées avec hp/ammo/expa/morale/grp), "
                    "délais d'arrivée des renforts (secondes), ids d'unités. À appeler AVANT de proposer des opérations.",
     "inputSchema": {"type": "object", "properties": MAPREF, "required": ["map", "mis"]},
     "annotations": {"readOnlyHint": True}},
    {"name": "search_units", "description": "Cherche des identifiants d'unités (id ou nom).",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 40}}},
     "annotations": {"readOnlyHint": True}},
    {"name": "preview_ops",
     "description": "Valide les opérations et liste les changements SANS rien écrire. Renvoie errors/warnings/changes et un "
                    "`token` à passer à apply_ops. Montre toujours cet aperçu à l'utilisateur et attends son accord.",
     "inputSchema": {"type": "object", "properties": dict(MAPREF, ops=OPS_PROP), "required": ["map", "mis", "ops"]},
     "annotations": {"readOnlyHint": True}},
    {"name": "apply_ops",
     "description": "Écrit les modifications (backup horodaté automatique). Refusé sans le `token` d'un preview_ops portant sur "
                    "exactement les mêmes opérations et la mission inchangée. À n'appeler qu'après accord explicite de l'utilisateur.",
     "inputSchema": {"type": "object", "properties": dict(MAPREF, ops=OPS_PROP, token={"type": "string"}),
                     "required": ["map", "mis", "ops", "token"]},
     "annotations": {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False}},
]


def call_tool(name, a):
    if not E.MAPS_DIR.is_dir():
        raise ValueError("dossier des cartes introuvable : %s — définis HS2_GAME_ROOT ou HS2_MAPS_DIR" % E.MAPS_DIR)
    if name == "list_missions":
        f = (a.get("filter") or "").lower()
        rows = [m for m in E.list_maps() if not f or f in json.dumps(m, ensure_ascii=False).lower()]
        return {"total": len(rows), "maps": rows[: int(a.get("limit", 60))]}
    if name == "get_mission_context":
        return E.ai_context(a["map"], a["mis"])
    if name == "search_units":
        return E.search_units(a.get("query", ""), int(a.get("limit", 40)))
    if name == "preview_ops":
        return E.ai_preview(a["map"], a["mis"], a["ops"])
    if name == "apply_ops":
        return E.ai_apply(a["map"], a["mis"], a["ops"], a.get("token"))
    raise ValueError("outil inconnu : %s" % name)


def reply(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    msg["error" if error else "result"] = error or result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(req):
    method, id_, params = req.get("method"), req.get("id"), req.get("params") or {}
    if id_ is None:  # notification (initialized, cancelled…) : pas de réponse
        return
    if method == "initialize":
        want = params.get("protocolVersion")
        reply(id_, {"protocolVersion": want if want in SUPPORTED else SUPPORTED[0],
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "hs2-mission-editor", "version": "1.0.0"}})
    elif method == "ping":
        reply(id_, {})
    elif method == "tools/list":
        reply(id_, {"tools": TOOLS})
    elif method == "tools/call":
        try:
            out = call_tool(params.get("name"), params.get("arguments") or {})
            reply(id_, {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False, separators=(",", ":"))}]})
        except (ValueError, KeyError, OSError) as e:
            reply(id_, {"isError": True, "content": [{"type": "text", "text": "Erreur : %s" % e}]})
        except Exception as e:  # bug interne : on le dit, on ne plante pas le serveur
            sys.stderr.write(traceback.format_exc())
            reply(id_, {"isError": True, "content": [{"type": "text", "text": "Erreur interne : %r" % e}]})
    elif method in ("resources/list", "prompts/list"):
        reply(id_, {method.split("/")[0]: []})
    else:
        reply(id_, error={"code": -32601, "message": "méthode inconnue : %s" % method})


def main():
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            handle(json.loads(line))
        except json.JSONDecodeError:
            reply(None, error={"code": -32700, "message": "JSON invalide"})


if __name__ == "__main__":
    main()
