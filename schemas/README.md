# Schémas — contrat canonique RouterContractV1

[Guide général](../README.md) · [Normalisation](../normalizer/README.md)

## Rôle

Ce dossier définit la représentation métier commune du système. Les modules du
normaliseur construisent directement les classes Pydantic de ce contrat.

| Fichier | Fonction |
|---|---|
| `router_contract_v1.py` | Types, sous-modèles, contraintes et modèle racine |
| `router_contract_v1.schema.json` | JSON Schema généré à partir des modèles |
| `__init__.py` | Déclaration du package Python |

Le contrat est conçu pour les routeurs multi-constructeurs ; le pipeline fourni
alimente les commandes Cisco IOS/IOS-XE reconnues. Le schéma définit des possibilités
structurelles, sans prouver que chaque champ est effectivement extrait.

## Structure racine

```text
RouterContractV1
├── contract_version : "1.0.0"
├── device
├── system
├── interfaces
├── interface_aggregations
├── network_instances
├── routing
├── routing_policies
├── security
├── nat
├── vpn
├── qos
├── mpls
├── multicast
├── pki
└── extensions
```

Les objets racines sont conservés même lorsque leurs propriétés sont indéterminées.
Les collections racines d'interfaces, d'agrégations et de network instances peuvent
être `null`.

## Typage et contraintes

Le modèle utilise notamment des booléens, chaînes et entiers stricts, des adresses
IPv4/IPv6, des préfixes réseau, des listes typées et des valeurs fermées. Les ASN
sont bornés de 1 à 4294967295 ; le type de port générique couvre 0 à 65535. Certaines
contraintes propres à une commande sont également contrôlées dans le parsing ou
le mapping.

La classe commune `Contract` interdit les champs inconnus et valide les affectations.
Des contrôles complémentaires évitent certaines conversions implicites de listes
ou de littéraux. Les validations croisées vérifient, selon les objets, les familles
IP, plages, combinaisons de paramètres et certaines identités dupliquées.

Le contrat ne valide pas à lui seul la véracité d'une configuration source ni
l'existence de toutes les cibles référencées. Une référence littérale non résolue
peut rester une information métier valide.

## Sémantique des valeurs

| Valeur | Sens |
|---|---|
| `true` | Activation ou propriété établie |
| `false` | Désactivation ou négation établie |
| `null` | Information indéterminée |
| `[]` | Collection confirmée vide |
| Liste non vide | Éléments connus sans exhaustivité implicite |

Pydantic vérifie la structure, mais une valeur par défaut ou une liste vide ne
prouve pas une absence dans la source. Cette preuve appartient au normaliseur,
notamment à `AbsenceResolver` et à la sélection des faits configurés.

Les méthodes de sérialisation du pipeline conservent les `null`. Ne pas utiliser
`exclude_none` ou `exclude_unset` pour produire la sortie officielle, car cela
modifierait la topologie prévue du contrat.

## Valider un document existant

Depuis la racine du projet, dans un programme Python :

```python
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from schemas.router_contract_v1 import RouterContractV1, router_contract_v1_schema

payload = json.loads(Path('outputs/routeur/normalized.json').read_text(encoding='utf-8'))
model = RouterContractV1.model_validate(payload)
Draft202012Validator(
    router_contract_v1_schema(), format_checker=FormatChecker()
).validate(payload)
```

Cette vérification contrôle le contrat ; elle ne mesure pas l'exhaustivité du parsing.

## Régénérer le JSON Schema

Le modèle Python est la source de génération du schéma. Depuis PowerShell, à la
racine du dépôt :

```powershell
@'
import json
from pathlib import Path
from schemas.router_contract_v1 import router_contract_v1_schema

Path('schemas/router_contract_v1.schema.json').write_text(
    json.dumps(router_contract_v1_schema(), indent=2, ensure_ascii=False) + '\n',
    encoding='utf-8',
)
'@ | .\.venv\Scripts\python.exe -
```

Le schéma déclare le dialecte JSON Schema 2020-12 et un identifiant de contrat.
Après une modification de modèles, vérifier la cohérence des mappings et du
schéma généré. Ne pas modifier uniquement le fichier JSON pour contourner une erreur.

## Périmètre

Le contrat représente une configuration, avec ses paramètres et relations. Il
n'intègre ni états opérationnels observés, ni secrets bruts, ni résultats d'audit.
Les fonctions de commutation L2 exclues et l'authentification 802.1X/PPP d'interface
ne font pas partie du contrat cible. Les extensions Cisco retenues restent séparées
des domaines communs.

## Extension EIGRP distribuée

`routing.eigrp` et `routing.eigrp_interfaces` représentent les processus et réglages
d'interfaces classiques. Les types distinguent AF/VRF, topologies, paramètres
d'af-interface, métriques composites, filtres et authentification sans secrets.
Les ASN EIGRP sont limités à 1–65535. Les paramètres communs d'interface
`bandwidth_kbps` et `delay_tens_of_microseconds` sont des valeurs configurées.

L'action de politique `eigrp_metric` conserve les cinq composantes ; `metric` garde
sa sémantique scalaire. Les nouveaux champs sont facultatifs et peuvent rester
null. Le contrat reste RouterContractV1 / 1.0.0, mais les consommateurs utilisant
un ancien schéma fermé doivent adopter le JSON Schema synchronisé.
Voir [les décisions de modélisation](../docs/eigrp/README.md).

## Champs synchronisés des correctifs Cisco

Les modèles incluent `tcp_established`, `exact_match`, `QoSMatch.address_family`,
les images de boot locales ordonnées, les paramètres propres aux caches NetFlow,
la persistance ifIndex et les options natives Cisco typées (scheduler, CDP, FPD,
IOAM, format de communautés, QFP et punt). `password_encryption_service` et
`IsisProcess.declared` sont alimentés par les déclarations reconnues.

La [convention de compatibilité](COMPATIBILITE.md) explique pourquoi le numéro
`1.0.0` ne suffit pas à identifier un schéma exact ; épingler la révision et
l’empreinte du JSON Schema. Le fichier fourni est régénéré depuis ces modèles.
