# HS2 Tools — consignes pour Claude Code

Ce dossier contient le **Mission Editor** de Hidden Stroke II (Python, stdlib). Quand l'utilisateur demande d'ajuster une
carte (renforts, expérience des convois, délais d'arrivée…), tu **pilotes l'éditeur avec `hs2_cli.py`**. Tu es le LLM :
n'utilise pas l'onglet Prompt ni `llm_config.json`.

## Règles non négociables

1. **N'édite jamais `support` ni `scripts2` à la main** (ni sed, ni script ad hoc). Ces fichiers ont un format strict
   (tailles recalculées, chiffres des délais inversés). Passe uniquement par `hs2_cli.py`.
2. **Toujours : contexte → opérations → `preview` → montrer l'aperçu → accord de l'utilisateur → `apply`.**
   Ne lance jamais `apply` sans accord explicite sur l'aperçu que tu viens de montrer.
3. `apply` exige le `token` du `preview` portant sur **exactement les mêmes opérations**. Si l'utilisateur change quoi
   que ce soit, refais un `preview`.
4. N'invente pas d'identifiant d'unité : cherche-le avec `units`. Demande ambiguë (quel convoi ? quelle équipe ?) :
   pose une question courte plutôt que de deviner.
5. Ne fais que ce qui est demandé. Signale les `warnings` (valeurs ramenées dans la plage, unité créée sans modèle…).
6. Travaille sur une copie des cartes si l'utilisateur ne l'a pas dit explicitement. Chaque `apply` crée un backup
   horodaté (dossier `backups/`, ou `HS2_BACKUP_DIR`).

## Commandes

Dossier des cartes : variable `HS2_GAME_ROOT` (racine du jeu) ou `HS2_MAPS_DIR`, sinon `--maps CHEMIN` (avant la commande).

```bash
python3 hs2_cli.py maps --filter 023            # cartes / missions
python3 hs2_cli.py context map.023 mis.000      # état compact : blocs support, délais, ids d'unités
python3 hs2_cli.py units lancia                 # recherche d'identifiants d'unités
python3 hs2_cli.py preview map.023 mis.000 --ops /tmp/ops.json    # valide, liste les changements, renvoie un token
python3 hs2_cli.py apply   map.023 mis.000 --ops /tmp/ops.json --token <TOKEN>
```

Écris les opérations dans un fichier temporaire (`/tmp/ops.json`, hors du dépôt) : une liste JSON, ou `{"ops": [...]}`.
Sortie en JSON ; une erreur donne `{"error": "..."}` et un code de sortie non nul.

## Lire le contexte

- `support_blocks[]` : un bloc = un convoi/groupe de renforts (indice **0-based** = `block`). Les unités identiques sont
  regroupées (`n`), avec `hp, ammo, expa, morale, grp, crew, passengers`.
- `arrival_timings[]` : délais d'arrivée en **secondes**. `kind` = `timed` (minuteur), `flag` (déclenché par flag) ou
  `trigger`. `support_blocks` = blocs livrés par cette arrivée : c'est ce qui permet de relier « les renforts du convoi 3 »
  à un délai. `line` identifie le délai dans son script.
- **Attention :** une arrivée peut livrer jusqu'à 5 blocs à la fois (liste `support_blocks`). Décaler « le délai du bloc 0 »
  décale aussi les autres blocs de la même arrivée. Dis-le à l'utilisateur dans l'aperçu.
- « 2 minutes plus tôt » = `shift_seconds: -120` ; « arrive à 10 min » = `seconds: 600`.
- Un délai `flag` n'est pas un temps d'attente simple : dis-le à l'utilisateur avant de le modifier.

## Format des opérations

Opérations autorisées (rien d'autre) :
- {"op":"set_unit_fields","blocks":"all"|<int>|[<int>...],"unit_id":<id|null>,"level":"top"|"passengers"|"all","fields":{"hp":..,"ammo":..,"expa":..,"morale":..,"lives":..,"grp":..,"crew":..}}
- {"op":"add_unit","block":<int>,"unit_id":<id>,"count":<int>,"fields":{...}}
- {"op":"remove_unit","block":<int>,"unit_id":<id>,"count":<int>|"all"}
- {"op":"set_timing","script":<nom|null>,"kind":"timed"|"flag"|"trigger"|null,"block":<int|null>,"line":<int|null>,"seconds":<int>}  ou  "shift_seconds":<int> (relatif, peut être négatif)

Règles :
- "block" = indice 0-based du bloc support. "set_timing" avec "block" cible les arrivées qui livrent ce bloc.
- Les délais sont en SECONDES (10 min = 600). Plage 0..86400.
- Plages : hp/ammo/expa/morale -1..100 (-1 = défaut), lives 0..100, grp -1..99, crew 0..31.
- unit_id doit exister dans known_unit_ids. Si tu n'es pas sûr, ne l'invente pas : renvoie ops=[] et explique.
- Ne fais que ce qui est demandé. Demande ambiguë : ops=[] et explication courte de ce qu'il manque.

## Exemples

- « renforts alliés 2 minutes plus tôt » → repère dans `arrival_timings` les arrivées dont `support_blocks` correspondent aux
  blocs alliés (demande à l'utilisateur lesquels si ce n'est pas évident), puis un `set_timing` avec `block` et `shift_seconds: -120`
  par bloc concerné.
- « expérience des convois 3 et 4 à 70 » → `{"op":"set_unit_fields","blocks":[3,4],"fields":{"expa":70}}`.
- « 2 chars lourds de plus dans le convoi 5 » → `units` pour trouver l'id, puis `{"op":"add_unit","block":5,"unit_id":"<id>","count":2}`.

## Variante MCP

Le même moteur est exposé par `hs2_mcp_server.py` (5 outils). Dans Claude Code :
`claude mcp add hs2 -e HS2_GAME_ROOT=/chemin/jeu -- python3 /chemin/HS2_Tools/hs2_mcp_server.py`.
Le CLI suffit : le MCP sert surtout à Claude Desktop.
