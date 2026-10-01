#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hs2_cli.py — pilotage en ligne de commande du Mission Editor (pour Claude Code ou un script).

Sorties : JSON sur stdout. Aucune dépendance, aucun serveur HTTP, aucun LLM externe.

  python3 hs2_cli.py maps [--filter TXT] [--limit N]
  python3 hs2_cli.py context MAP MIS
  python3 hs2_cli.py units [QUERY] [--limit N]
  python3 hs2_cli.py preview MAP MIS --ops ops.json        (ou --ops - pour stdin)
  python3 hs2_cli.py apply   MAP MIS --ops ops.json --token TOKEN

`apply` refuse d'écrire sans le token renvoyé par `preview` pour EXACTEMENT les mêmes opérations
sur la mission telle qu'elle est maintenant. Dossier des cartes : HS2_GAME_ROOT, ou --maps CHEMIN.
Format des opérations : voir OPS_DOC dans hs2_prompt_ops.py (ou CLAUDE.md).
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _load_ops(arg):
    raw = sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8")
    data = json.loads(raw)
    if isinstance(data, dict) and "ops" in data:
        data = data["ops"]
    if not isinstance(data, list):
        raise ValueError("le fichier doit contenir une liste d'opérations (ou {\"ops\": [...]})")
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--maps", help="chemin de maps_ap.src (sinon HS2_GAME_ROOT / détection auto)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("maps"); s.add_argument("--filter", default=""); s.add_argument("--limit", type=int, default=60)
    s = sub.add_parser("context"); s.add_argument("map"); s.add_argument("mis")
    s = sub.add_parser("units"); s.add_argument("query", nargs="?", default=""); s.add_argument("--limit", type=int, default=40)
    s = sub.add_parser("preview"); s.add_argument("map"); s.add_argument("mis"); s.add_argument("--ops", required=True)
    s = sub.add_parser("apply"); s.add_argument("map"); s.add_argument("mis"); s.add_argument("--ops", required=True); s.add_argument("--token", required=True)
    a = ap.parse_args(argv)

    sys.argv = sys.argv[:1]  # le module éditeur lit argv[1] à l'import
    import hs2_mission_editor as E

    if a.maps:
        E.MAPS_DIR = Path(a.maps)
    if not E.MAPS_DIR.is_dir():
        print(json.dumps({"error": "dossier des cartes introuvable : %s (HS2_GAME_ROOT ou --maps)" % E.MAPS_DIR}))
        return 2
    try:
        if a.cmd == "maps":
            f = a.filter.lower()
            rows = [m for m in E.list_maps() if not f or f in json.dumps(m, ensure_ascii=False).lower()]
            out = {"total": len(rows), "maps": rows[: a.limit]}
        elif a.cmd == "context":
            out = E.ai_context(a.map, a.mis)
        elif a.cmd == "units":
            out = E.search_units(a.query, a.limit)
        elif a.cmd == "preview":
            out = E.ai_preview(a.map, a.mis, _load_ops(a.ops))
        else:
            out = E.ai_apply(a.map, a.mis, _load_ops(a.ops), a.token)
    except (ValueError, KeyError, OSError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1
    try:
        print(json.dumps(out, ensure_ascii=False, indent=1 if sys.stdout.isatty() else None, separators=None if sys.stdout.isatty() else (",", ":")))
    except BrokenPipeError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
