# Dépendances d'exécution hors ligne

[Installation du projet](../README.md#installation) · [Notices tierces](../THIRD_PARTY_NOTICES.md)

## Contenu

Ce dossier contient les archives Python nécessaires à l'exécution du mécanisme,
aux versions figées dans `requirements.lock`. Les dépendances des tests du dépôt
de développement, telles que pytest, ne sont pas incluses.

| Ensemble | Fonction |
|---|---|
| `ttp`, `ttp_templates` | Moteur de parsing et accès aux templates amont |
| `pydantic`, `pydantic_core` | Modèles et validation typée |
| `annotated_types`, `typing_extensions`, `typing_inspection` | Dépendances du typage et de Pydantic |
| `jsonschema`, `jsonschema_specifications` | Validation JSON Schema et spécifications |
| `attrs`, `referencing`, `rpds_py` | Dépendances de la validation JSON Schema |

Les archives sont conservées telles quelles, avec leurs métadonnées et licences.
Elles ne doivent pas être extraites manuellement dans les packages du projet.

## Installation

Depuis la racine du dépôt :

```powershell
.\setup.ps1
```

Le script crée `.venv`, puis appelle pip avec `--no-index`, ce dossier comme source
d'archives et `requirements.lock` comme liste de versions. Aucun téléchargement
Internet n'est nécessaire pour cette installation.

## Compatibilité

La distribution fournie est validée pour **Windows x64 / Python 3.12**. Certaines
archives sont universelles ; `pydantic_core` et `rpds_py` contiennent des composants
binaires spécifiques à cette plateforme et version de Python.

Une autre plateforme nécessite ses propres archives compatibles ; copier ces
fichiers binaires dans un autre environnement ne suffit pas.

## Mise à jour

Le paquet `ttp_templates` est lié aux quatre fichiers de `templates/upstream/`.
Le parser vérifie leur cohérence à l'exécution. Une mise à jour des bibliothèques
doit donc être préparée et validée dans le dépôt de développement, avec mise à
jour cohérente des versions et snapshots si nécessaire.

Le dossier fournit une installation reproductible du mécanisme actuel ; il ne
constitue pas un historique de toutes les versions des dépendances.
