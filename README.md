# Sudden Strike – Modding Tools

Collection d’outils historiques destinés au **modding, au mapping et à l’édition des ressources de Sudden Strike**, notamment **Sudden Strike 1, Sudden Strike Forever (SS1/SSF)** et **Sudden Strike: Resource War (SSRW)**.

Cette collection rassemble des utilitaires autrefois distribués principalement via le forum [Sudden-Strike-Maps.de](https://www.sudden-strike-maps.de/phpBB2/viewtopic.php?t=9956). Elle a pour objectif de centraliser des outils devenus difficiles à retrouver et de conserver les tutoriels et informations nécessaires à leur utilisation.

> **Important :** ces outils sont anciens et certains n’ont plus été maintenus depuis de nombreuses années. Leur compatibilité avec les systèmes modernes peut varier. Faites toujours une sauvegarde des fichiers originaux avant toute modification.

## Contenu de la collection

### Animation et effets

| Outil               | Description                                                                                                                             |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Ani-Maker**       | Création et édition d’animations utilisées par le jeu.                                                                                  |
| **Anied**           | Éditeur d’animations destiné notamment à l’éditeur de cartes.                                                                           |
| **Explosion-Maker** | Création et édition d’effets d’explosion. Une version complète, `Exp_Maker-Vollversion`, est également mentionnée dans les discussions. |

### Compression, archives et ressources

| Outil                      | Description                                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Packer / Unpacker**      | Ensemble d'utilitaires pour emballer et extraire différentes ressources du jeu : `.sue`, `.unsue`, `._aps`, `._unaps`, `._pak` et `._unpak`.                                   |
| **Pck Explorer**           | Permet de packer et dépacker les fichiers `.pck`. Offre notamment des fonctions de zoom et un _Color Boost_ permettant d’obtenir un rendu plus proche de celui affiché en jeu. |
| **Pak + Unpak**            | Utilitaires spécialisés dans le package et le dépackage des fichiers `.pak`, notamment ceux rencontrés dans certains mods.                                                     |
| **SuSt Universe for Mods** | Utilitaire permettant de restaurer la structure originale des dossiers pour **SSRW** et **Sudden Strike 2**.                                                                   |

### Graphismes, palettes et ressources `.res`

| Outil                  | Description                                                                                                                                                    |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sust Graph 2.04**    | Visualisation de fichiers `.pck`, `.res` et `.ani`. Permet également certaines modifications ou corrections des fichiers `.hot` et `.inf`.                     |
| **SustResExporter**    | Transfert d’éléments graphiques entre fichiers `.res`. Permet par exemple de récupérer des objets graphiques d’un jeu ou mod et de les intégrer dans un autre. |
| **Res Converter 0.14** | Outil de conversion de fichiers `.res`.                                                                                                                        |
| **Colman**             | Outil destiné à l’édition et à la manipulation des palettes de couleurs.                                                                                       |
| **Icon Tool v1.1**     | Création d’icônes personnalisées pour le jeu ou les mods.                                                                                                      |

#### À propos de `SustResExporter`

`SustResExporter` est particulièrement utile pour modifier les bibliothèques graphiques du jeu.

Le principe consiste à travailler avec deux ensembles :

```text
Source/
    tree.res
    tree.edt
    tree.pl

Target/
    tree.res
    tree.edt
    tree.pl
```

Les éléments graphiques de `Source` peuvent ensuite être transférés vers des emplacements disponibles dans `Target`.

L'option **`use edt`** est importante : lorsqu'elle est activée, l'outil génère également le fichier `.edt` associé au `.res`. Cela permet de conserver la cohérence entre les ressources utilisées par le jeu et celles référencées par l'éditeur de cartes.

> Il est recommandé d'activer `use edt` lors de la modification d'un `.res`, afin d'éviter des incohérences entre le jeu et l'éditeur, pouvant notamment provoquer des objets absents ou des plantages.

Le programme fonctionne avec la plupart des fichiers `.res`, à l'exception de `most.res` et, dans certains cas, de `Dom.res` lorsqu'ils sont trop chargés. `Icon.res` peut également être traité.

### Mapping et édition de cartes

| Outil / document                      | Description                                                                                                   |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Irrläufers Editorfibel**            | Guide destiné aux mappeurs et aux utilisateurs de l’éditeur de cartes.                                        |
| **SSRW Editor User Guide**            | Guide utilisateur de l’éditeur de cartes de **Sudden Strike: Resource War**.                                  |
| **PlMaker**                           | Utilitaire lié aux fichiers `.pl`. Fonction exacte non documentée dans le message d’origine.                  |
| **PlView**                            | Utilitaire de visualisation lié aux fichiers `.pl`. Fonction exacte non documentée dans le message d’origine. |
| **Object Editor – Community Release** | Éditeur d’objets pour la création ou la modification d’objets du jeu.                                         |
| **OBR Compiler**                      | Compilateur utilisé avec l’Object Editor.                                                                     |
| **OBR Sample**                        | Exemple de fichier/projet destiné à l’Object Editor et à l’OBR Compiler.                                      |

### Sons

| Outil                           | Description                                                                |
| ------------------------------- | -------------------------------------------------------------------------- |
| **Sound Programs**              | Ensemble d'utilitaires destinés à la manipulation et à l'édition des sons. |
| **Tutorial – Sounds Editieren** | Tutoriel expliquant comment ajouter de nouveaux sons au jeu.               |

Le tutoriel accompagne les outils audio et décrit notamment le processus d’intégration de nouveaux fichiers sonores.

### Édition technique

| Outil               | Description                                                                                                                                           |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **RS2Manager**      | Outil de gestion/édition de ressources de Sudden Strike. Le forum le présente comme un outil suffisamment complexe pour nécessiter un tutoriel dédié. |
| **SuSt Hot Editor** | Éditeur des fichiers `.hot`.                                                                                                                          |
| **SuSt Splitter**   | Utilitaire de découpage de ressources. Fonction exacte non détaillée dans les messages fournis.                                                       |
| **SuSt Sticker**    | Utilitaire associé aux ressources graphiques. Fonction exacte non détaillée dans les messages fournis.                                                |
| **SuSt Stuff**      | Collection/utilitaire de manipulation de ressources Sudden Strike. Fonction exacte non détaillée dans les messages fournis.                           |
| **SuSt Gext**       | Utilitaire de manipulation de ressources Sudden Strike. Fonction exacte non détaillée dans les messages fournis.                                      |
| **Soldiers**        | Outil associé aux unités/soldats. Sa fonction précise n'est pas documentée dans le message d'origine.                                                 |

### Missions et traduction

| Outil              | Description                                                                                                                                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **TranslateTOOLS** | Utilitaire de traduction des missions **multijoueur (MP)** et **solo (SP)**.                                                                                                                                                                                             |
| **entLoc.exe**     | Outil recherché dans le forum pour ouvrir les missions originales de **Sudden Strike 1** et **Sudden Strike Forever**. Il est mentionné comme faisant partie des anciens outils « SUDDEN TOOLs », mais son fonctionnement n'est pas documenté dans les messages fournis. |

### Textures

| Outil        | Description                                                                                                                         |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **TileTool** | Ancien outil de texturing, développé par **Brian / Sardaukar**. Destiné à la manipulation des textures/tuiles utilisées par le jeu. |

### Hidden Stroke II / Sudden Strike 2 (outils récents)

Contrairement au reste de la collection, ces outils sont **récents et maintenus**. Ils ciblent **Hidden Stroke II** et le moteur **Sudden Strike 2**, pas SS1/SSF/SSRW. Python 3.8+, sans dépendance, interface dans le navigateur (macOS et Windows). Dossier : [`HS2_Tools/`](HS2_Tools/README.md), licence MIT.

| Outil                  | Description                                                                                                                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **HS2 Mission Editor** | Édite les convois de renfort, l'expérience, les joueurs et les scripts de chaque carte. L'onglet **Prompt** ajuste les renforts en langage naturel, avec aperçu et sauvegarde avant écriture.   |
| **HS2 APS Tool**       | Décompacte et recompacte `lang.aps` et toute archive FZFF.                                                                                                                                       |
| **HS2 Unit Comparator** | Comparateur d'unités, page HTML autonome.                                                                                                                                                       |
| **decompile_aps.py**   | Décompression brute d'une archive `.aps` en ligne de commande.                                                                                                                                   |

## Documentation incluse

L’un des objectifs principaux de la collection originale était de ne pas simplement distribuer les exécutables, mais de fournir également les explications nécessaires à leur utilisation.

Les documents mentionnés dans les archives comprennent notamment :

- **Irrläufers Editorfibel**
- **SSRW Editor User Guide**
- **Tutoriel d’édition des sons**
- Tutoriel **SustResExporter**
- Descriptions et instructions associées aux outils de compression/décompression
- Tutoriels supplémentaires annoncés pour le **RS2Manager**, l’éditeur d’objets et l’édition des fichiers `.hot`

Lorsque plusieurs versions d'un outil existent, la documentation correspondante doit idéalement être conservée avec la version concernée.

## À quoi sert cette collection ?

Ces outils couvrent une grande partie de la chaîne de création d’un mod ou d’une carte :

```text
                    SUDDEN STRIKE MODDING
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
     CARTES              GRAPHISMES           AUDIO
        │                   │                   │
  Editor / OBR         .res / .pck           Sons
  .pl / objets         Animations            Effets
        │                   │
        └─────────────┬─────┘
                      │
                   MISSIONS
                      │
                Traduction / édition
                      │
                      ▼
                 PACKAGING
                      │
               .pak / .pck / etc.
                      │
                      ▼
                    MOD
```

La collection permet ainsi notamment de :

- créer et modifier des **cartes**
- éditer les **objets** utilisés par les cartes
- manipuler les fichiers `.res`, `.edt`, `.pl`, `.pck` et `.pak`
- créer ou modifier des **animations et effets**
- importer des éléments graphiques provenant d’autres versions ou mods
- modifier les **palettes et textures**
- ajouter ou modifier des **sons**
- traduire des **missions solo et multijoueur**
- empaqueter et extraire les ressources nécessaires à un mod
- restaurer ou préserver la structure de fichiers originale des jeux.

## Précautions

### Sauvegarder les fichiers originaux

Avant de modifier une ressource du jeu :

1. créer une copie du fichier original
2. travailler sur une copie
3. tester la modification dans une installation séparée lorsque cela est possible.

Ceci est particulièrement important pour les fichiers `.res` et `.edt`, car une modification incohérente peut rendre certains objets invisibles dans le jeu ou provoquer des problèmes dans l’éditeur.

### Compatibilité

Les outils proviennent pour la plupart de la communauté de modding de **Sudden Strike** et datent principalement des années 2000–2020. Ils peuvent donc nécessiter :

- une ancienne version de Windows
- des paramètres de compatibilité
- une installation spécifique de Sudden Strike
- des chemins de fichiers adaptés à l’environnement local.

La collection ne garantit pas leur fonctionnement sur les systèmes modernes.

### Documentation

Lorsqu’un outil est accompagné d’un tutoriel dans son archive originale, celui-ci doit être conservé. Pour certains outils, notamment ceux dont la fonction est complexe, le tutoriel est indispensable pour comprendre les formats manipulés.

## Origine de la collection

Une partie importante de cette collection provient du sujet **« Modding Tool-Archiv »** publié sur le forum **Sudden-Strike-Maps.de** à partir de 2013.

L’objectif initial était de réunir les outils nécessaires aux moddeurs et aux mappeurs, tout en ajoutant des tutoriels afin que les débutants puissent comprendre à quoi servent les programmes et comment les utiliser.

La collection a ensuite été enrichie au fil des années avec de nouveaux outils, notamment :

- **Colman**, pour les palettes
- **Pck Explorer**, pour les fichiers `.pck`
- **TileTool**, pour le texturing
- **Pak + Unpak**, pour les fichiers `.pak`
- **Res Converter**, pour les fichiers `.res`

Source historique : [forum Sudden-Strike-Maps.de – Modding Tool-Archiv](https://www.sudden-strike-maps.de/phpBB2/viewtopic.php?t=9956)

## Inventaire synthétique

| Domaine                  | Outils / documents                                           |
| ------------------------ | ------------------------------------------------------------ |
| Animations               | Ani-Maker, Anied                                             |
| Explosions / effets      | Explosion-Maker                                              |
| Archives                 | Packer/Unpacker, Pck Explorer, Pak/Unpak                     |
| Ressources               | Sust Graph, SustResExporter, Res Converter                   |
| Palettes                 | Colman                                                       |
| Icônes                   | Icon Tool                                                    |
| Mapping                  | Editorfibel, SSRW Editor User Guide                          |
| Objets                   | Object Editor, OBR Compiler, OBR Sample                      |
| Fichiers `.pl`           | PlMaker, PlView                                              |
| Audio                    | Sound Programs, Sound Editing Tutorial                       |
| Missions                 | TranslateTOOLS, entLoc                                       |
| Fichiers `.hot`          | SuSt Hot Editor                                              |
| Autres ressources        | Soldiers, SuSt Splitter, SuSt Sticker, SuSt Stuff, SuSt Gext |
| Textures                 | TileTool                                                     |
| Installation / structure | SuSt Universe for Mods                                       |

## Statut

Cette collection est avant tout une **archive de conservation d’outils historiques de modding**.

Les descriptions présentes dans ce README sont basées sur les informations disponibles dans les discussions originales. Lorsqu’un outil était mentionné sans explication détaillée, sa fonction n’est volontairement pas présentée comme certaine.

Si des informations supplémentaires sont retrouvées — documentation, sources, versions plus récentes, exemples d’utilisation ou corrections — elles peuvent être ajoutées progressivement à ce dépôt.
