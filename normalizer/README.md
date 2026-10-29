# Normalisation métier — construction du contrat canonique

[Guide général](../README.md) · [Domaines](domains/README.md) · [Utilitaires](common/README.md) · [Contrat](../schemas/README.md)

## Responsabilité

Le normaliseur transforme les captures du parser en objets `RouterContractV1`.
Il interprète les valeurs, préserve leurs portées et établit les relations entre
interfaces, processus, contextes et politiques.

Il existe un moteur unique. Les domaines alimentent directement le contrat V1,
sans passage par un ancien modèle métier ou par un convertisseur intermédiaire.

## Organisation

| Élément | Rôle |
|---|---|
| `engine.py` | Coordination, état du traitement et enchaînement des phases |
| `domains/__init__.py` | Attribution des captures aux domaines propriétaires |
| `domains/` | Mappings métier spécialisés |
| `common/` | Fonctions partagées, sélection des faits et preuves de vide |
| `serialization.py` | Revalidation et conversion du contrat en dictionnaire ou JSON |

## Cycle du moteur

### 1. Préparation

`NormalizationEngine` reçoit l'inventaire et les captures, valide les records,
identifie certaines déclarations dupliquées et propage l'invalidité des parents.
Il prépare un modèle V1 avec sa structure fixe et des valeurs indéterminées.

### 2. Déclarations

Un premier passage crée les objets structurants dont les règles sont déclaratives :
interfaces, certains processus, VRF, statements de route-map, lignes administratives,
serveurs et groupes AAA. Les identités peuvent ainsi être référencées ensuite.
D'autres objets sont créés dans leurs handlers lors de l'application des règles.

### 3. Mapping par domaine

Chaque capture est dirigée vers un handler propriétaire. Les fonctions de mapping
construisent ou modifient les sous-modèles Pydantic et enregistrent les champs
effectivement alimentés depuis la capture.

### 4. Résolution différée

Les traitements exigeant une résolution ultérieure sont placés dans `pending`.
Un passage distinct les applique après les déclarations et mappings ordinaires.
Une référence peut rester littérale lorsque sa cible n'est pas établie.

### 5. Sélection des faits publiables

Les liaisons internes entre captures et champs sont vérifiées. La sélection retient
les valeurs admissibles et écarte les propriétés créées uniquement par défaut.
Les politiques ordonnées partiellement reconnues et certaines dépendances concernées
sont bloquées afin d'éviter une représentation trompeuse.

Une collection vide exige une preuve du résolveur d'absences. La structure fixe du
contrat et les champs inconnus sont ensuite restaurés par les modèles canoniques.

### 6. Validation et export

Le document est validé avec Pydantic et JSON Schema. La sérialisation revalide
également le graphe imbriqué avant de produire le JSON.

## État interne important

| Élément | Fonction |
|---|---|
| `c` | Modèle canonique en cours de construction |
| `validation` | Validité des captures et des champs |
| `entities` | Correspondance entre déclarations et objets |
| `bindings` | Champs canoniques liés à des captures sources |
| `consumed` | Paramètres pris en compte par les mappings |
| `pending` | Traitements différés |
| `failed`, `ambiguous` | Captures rejetées ou ambiguës |
| `absences` | Preuves de collections confirmées vides |

Ces éléments servent au contrôle interne. Ils ne sont pas des résultats d'audit
et ne sont pas publiés comme sections de `normalized.json`.

## Gestion des erreurs

Chaque application de règle dispose d'un état précédent. Certaines erreurs de
mapping provoquent le rétablissement de cet état et marquent la capture comme
échouée, sans inventer une valeur de remplacement. Les erreurs Pydantic sont
propagées : un objet canonique invalide ne doit pas être supprimé pour forcer l'export.

Une commande non prise en charge ou partielle se distingue donc d'une erreur
structurelle empêchant la validation du contrat.

## Utilisation et sérialisation

Le point d'entrée recommandé reste `cli.normalize` ou `cli.convert_file`.
Pour examiner le modèle directement dans un programme Python :

```python
from parser.run_ttp import extract
from normalizer.engine import normalize_captures
from normalizer.serialization import to_dict, to_json

captures = extract('interface GigabitEthernet0/0\n shutdown\n')
model = normalize_captures(captures, os_family='ios')
document = to_dict(model)
encoded = to_json(model)
```

`to_dict` et `to_json` exigent `RouterContractV1`. Les `null`, `false`, valeurs
zéro et collections vides justifiées sont conservés. Le sérialiseur ne reconstruit
pas les relations métier et ne réinterprète pas les commandes CLI.

## Domaine EIGRP

Le dispatch confie les règles EIGRP au module `domains/routing/eigrp.py`. Celui-ci
construit directement les modèles V1, en distinguant processus, AF/VRF, topologies
et af-interface. Les réglages classiques d'interface conservent leur référence AS
sans création d'un processus manquant. Les métriques d'interface bandwidth/delay
et la métrique composite des politiques restent des objets ou champs distincts.
Voir [la documentation EIGRP](../docs/eigrp/README.md).
