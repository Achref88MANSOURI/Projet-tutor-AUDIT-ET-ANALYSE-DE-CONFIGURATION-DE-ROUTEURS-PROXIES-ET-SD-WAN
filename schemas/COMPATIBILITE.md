# Identifier le schéma exact du contrat

`contract_version = 1.0.0` identifie la génération canonique actuellement utilisée.
Ce champ seul **ne garantit pas l'identité exacte du JSON Schema** entre deux
révisions de développement. Des champs optionnels ont été ajoutés, notamment lors
de l'intégration EIGRP et des corrections de fidélité Cisco.

Les règles de consommation sont les suivantes :

- Le schéma fourni dans la même révision que le normaliseur fait autorité.
- Un consommateur doit épingler la révision Git et l'empreinte du fichier de schéma.
- L'acceptation d'un ancien document par les nouveaux modèles ne prouve pas que
  l'ancien schéma accepte les nouveaux documents. Avec `additionalProperties: false`,
  les champs supplémentaires peuvent être rejetés par un ancien validateur.
- Les champs absents d'un ancien document peuvent être restaurés à `null` par les
  modèles actuels. Ce comportement ne prouve pas leur absence dans la configuration.
- Les schémas des futures versions publiées devront être figés et toute nouvelle
  publication devra annoncer ses changements et sa version de contrat. Le maintien
  de `1.0.0` pendant ces correctifs ne doit pas être présenté comme une garantie de
  compatibilité descendante pour tous les validateurs stricts.

Depuis PowerShell à la racine :

```powershell
Get-FileHash -LiteralPath .\schemas\router_contract_v1.schema.json -Algorithm SHA256
git --no-pager log -1 --format=%H
git status --short
```

Un arbre de travail modifié n'est pas identifié complètement par son seul commit :
conserver aussi l'empreinte du schéma effectivement utilisé. Le schéma est régénéré
avec `tools/build_router_contract_v1_schema.py`. Aucun nouveau champ diagnostique
ni export métier parallèle n'est ajouté à `normalized.json` par cette convention.
