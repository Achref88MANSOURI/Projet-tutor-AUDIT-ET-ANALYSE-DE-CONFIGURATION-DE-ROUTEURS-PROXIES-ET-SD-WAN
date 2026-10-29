# Parser — du texte CLI aux captures structurées

[Guide général](../README.md) · [Templates](../templates/README.md) · [Normalisation](../normalizer/README.md)

## Responsabilité

Ce package prépare le texte de configuration et extrait les paramètres reconnus.
Il conserve les contextes nécessaires au mapping : interface, processus, famille
d'adresses, VRF, groupe AAA, aire ou niveau selon la commande.

Sa sortie est une structure intermédiaire. Le parser ne décide pas seul de la
forme finale des objets métier et n'écrit pas `normalized.json`.

## Organisation

| Module | Rôle |
|---|---|
| `inventory.py` | Représentation des lignes, indentation, parents, blocs racines, familles et limites de blocs |
| `run_ttp.py` | Chargement des templates, exécution TTP, filtres de contexte et sélection des captures |
| `validation.py` | Validation des valeurs capturées et suivi des champs validés |
| `platform.py` | Détection de certaines signatures de plateformes hors périmètre |
| `routing_secrets.py` | Masquage des credentials de routage reconnus |
| `admin_secrets.py` | Masquage des credentials administratifs reconnus, dont les communautés SNMP |
| `admin_context.py` | Restrictions de contexte spécifiques à AAA, aux serveurs et à SSH |

## Déroulement

1. **Masquage préalable.** Les credentials reconnus sont remplacés par des marqueurs
   constants, avant leur passage à l'inventaire et à TTP. Aucune empreinte n'est
   calculée à partir du secret.
2. **Inventaire.** Chaque ligne utile reçoit un numéro, un parent éventuel, un bloc
   racine et une famille de parsing. Les bannières et certains contenus de certificats
   sont traités comme des blocs opaques.
3. **Chargement des règles.** Les groupes TTP et les métadonnées sont contrôlés :
   identifiants uniques, structure attendue et familles connues.
4. **Extraction.** Les lignes numérotées sont regroupées par famille, puis soumises
   aux templates correspondants.
5. **Filtrage.** Le parser vérifie les valeurs fermées, le contexte et la reconnaissance
   de la ligne entière. Un suffixe non reconnu ne doit pas être perdu au profit
   d'une simple correspondance de préfixe.
6. **Sélection.** En cas de plusieurs correspondances, les formes les plus spécifiques
   sont privilégiées. Les ambiguïtés restantes sont signalées au moteur.
7. **Templates amont.** Par défaut, les quatre templates figés sont également exécutés.

Le contexte ne dépend pas uniquement du fichier de template. Une commande ne devient
pas globale parce qu'elle ressemble à une règle globale lorsqu'elle est placée sous
un bloc inconnu.

## Structure de sortie interne

La fonction `extract` renvoie notamment :

| Clé | Contenu |
|---|---|
| `nodes` | Objets `Node` décrivant les lignes et leurs relations |
| `records` | Captures retenues, indexées par numéro de ligne |
| `official` | Résultats des templates amont |
| `ambiguous_lines` | Lignes dont les meilleures captures restent ambiguës |

Un record comporte `rule`, `values`, `source_line`, `root_line`, `family` et
`context_lines`. Ces références sont internes au traitement ; elles ne constituent
pas des champs du contrat canonique.

## Exemple de lecture

```python
from parser.run_ttp import extract

text = 'interface GigabitEthernet0/0\n shutdown\n'
extracted = extract(text)
capture = extracted['records'][2]
assert capture['rule'] == 'if_shutdown'
assert capture['values']['enabled'] is False
```

Le mapping transforme ensuite cette capture en état administratif configuré de
l'interface. Elle ne décrit pas l'état opérationnel réel du port.

## Validation et erreurs

`validate_record` distingue la validité globale d'une capture de l'état de chacun
de ses champs. Certains paramètres textuels exigent une validation métier ultérieure.
Une extraction réussie ne garantit donc pas une normalisation complète.

Les erreurs de templates amont sont identifiées par `OfficialTemplateError` :
chargement, snapshot absent ou différent, exécution ou résultat invalide. Les
templates interfaces et VRF sont requis. Pour les deux autres, une erreur peut
être conservée comme limite interne et leur résultat devenir indéterminé.

## Évolution

Une modification de syntaxe doit être cohérente avec les templates, les restrictions
de contexte, la validation des valeurs et le domaine de mapping. Le nom d'une règle
ne suffit pas à prouver sa couverture métier. Éviter de journaliser les entrées,
captures ou exceptions avec des valeurs sensibles.

## EIGRP

`eigrp_context.py` contrôle les portées immédiates classique/nommée, AF/VRF, af-interface
et topologie. `eigrp_commands.py` valide les opérandes et les options composites
reconnues sans perdre de suffixe. Les mots de passe HMAC-SHA-256 sont masqués par le
filtre de routage avant inventaire et TTP. Voir [la couverture EIGRP](../docs/eigrp/README.md).
