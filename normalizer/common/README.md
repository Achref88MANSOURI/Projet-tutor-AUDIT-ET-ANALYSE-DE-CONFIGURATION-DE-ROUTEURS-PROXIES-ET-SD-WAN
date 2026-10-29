# Utilitaires communs de normalisation

[Normalisation](../README.md) · [Domaines](../domains/README.md)

## Rôle

Ce package rassemble les opérations partagées par les domaines. Il évite de
dupliquer les règles d'adressage, l'accès aux contextes et la sélection des valeurs
configurées. Il ne constitue pas un second moteur métier.

| Module | Fonction |
|---|---|
| `addresses.py` | Conversion et validation des masques, ASN, identifiants d'aires et lectures amont utiles |
| `contexts.py` | Recherche du contexte racine, des familles d'adresses et accès aux objets imbriqués |
| `collections.py` | Gestion des collections dans les modèles en cours de construction |
| `configured.py` | Parcours des champs, liaisons source-champ et projection des faits exportables |
| `absence.py` | Autorisation explicite des collections confirmées vides |
| `validation.py` | Validation de booléens et validation finale Pydantic/JSON Schema |

## Collection de travail et collection exportée

Un mapping peut avoir besoin d'une liste pour construire plusieurs objets. La
création de cette liste dans le modèle de travail n'est pas une preuve que la
configuration contient explicitement une collection vide.

La sélection finale examine les liaisons et preuves disponibles. Une collection
inconnue reste `null` même si un helper a utilisé temporairement une liste Python.

## Liaisons entre captures et champs

Un `Binding` relie un chemin canonique à une capture. Les opérations du moteur
enregistrent ainsi quels champs ont été alimentés. Avant l'export :

1. les chemins liés sont contrôlés ;
2. les valeurs provenant de captures admissibles sont sélectionnées ;
3. les objets bloqués sont écartés de la publication ;
4. les champs inconnus restent indéterminés dans la structure canonique.

Ce mécanisme préserve un `false` ou un zéro explicite. Il ne suffit pas de tester
la « vérité » Python d'une valeur pour décider de son export.

## Preuves de collection vide

`AbsenceResolver.confirm` accepte une preuve locale explicite, ou la combinaison
`source_complete=True` et `domain_covered=True`. Une seule de ces deux confirmations
ne suffit pas.

Exemple conceptuel : `no ip address` peut établir le vide local des adresses IPv4
d'une interface. L'absence de lignes IPv4 dans un fragment de configuration ne
fournit pas la même preuve.

La complétude globale d'une source et de la couverture d'un domaine n'est pas
déduite automatiquement de la simple présence d'un marqueur de fin de configuration.
Les preuves et liaisons restent internes au normaliseur.
