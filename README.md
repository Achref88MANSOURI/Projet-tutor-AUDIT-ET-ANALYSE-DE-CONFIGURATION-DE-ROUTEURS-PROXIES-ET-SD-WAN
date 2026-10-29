# Network Config Normalizer — RouterContractV1

Normaliseur de configurations de routeurs Cisco IOS/IOS-XE, avec une interface
Web locale et une interface en ligne de commande.

```text
Configuration CLI → parsing TTP → normalisation métier
                 → RouterContractV1 → normalized.json
```

Un seul moteur et un seul contrat métier sont utilisés. Le modèle canonique est
conçu pour les routeurs multi-constructeurs ; les templates fournis couvrent
actuellement Cisco IOS/IOS-XE. La présence d'un champ dans le contrat ne prouve
pas que toutes ses commandes sont reconnues.

## Première utilisation depuis GitHub

Le [guide complet de préparation et de démonstration Web](GUIDE_DEMONSTRATION_WEB.md)
détaille chaque étape, les valeurs attendues et le dépannage. Après installation
de Git et Python 3.12 x64, utiliser les commandes suivantes :

```powershell
$DepotGitHub = 'https://github.com/Achref88MANSOURI/-Projet-tutor-AUDIT-ET-ANALYSE-DE-CONFIGURATION-DE-ROUTEURS-PROXIES-ET-SD-WAN.git'
git clone $DepotGitHub normaliseur-routeurs
Set-Location -LiteralPath '.\normaliseur-routeurs'
.\setup.ps1
$env:CONFIG_STUDIO_PORT = '8001'
.\run_ui.ps1
```

Ouvrir **http://127.0.0.1:8001**. Ce port permet de distinguer cette copie du dépôt
original si celui-ci utilise déjà 8000. Le guide fournit aussi les commandes Python
directes si PowerShell bloque les scripts `.ps1`.

## Guide de lecture

| Documentation | Contenu |
|---|---|
| [Démonstration Web complète](GUIDE_DEMONSTRATION_WEB.md) | Clonage GitHub, préparation, configuration, essais Web/CLI/API |
| [EIGRP](docs/eigrp/README.md) | Sources Cisco, couverture et matrice des règles |
| [Parser](parser/README.md) | Inventaire, contextes, extraction et confidentialité |
| [Templates TTP](templates/README.md) | Règles de reconnaissance et snapshots amont |
| [Normalisation](normalizer/README.md) | Moteur unique et construction du contrat |
| [Utilitaires communs](normalizer/common/README.md) | Sélection des faits et preuves de collection vide |
| [Domaines métier](normalizer/domains/README.md) | Répartition et responsabilités des mappings |
| [Routage](normalizer/domains/routing/README.md) | Processus, AF/VRF, politiques et authentification |
| [Schémas](schemas/README.md) | Contraintes Pydantic, JSON Schema et validation |
| [Web](web/README.md) | Interface utilisateur et API HTTP locale |
| [Resources](resources/README.md) | Inventaire des 23 configurations, dont 3 exemples EIGRP |
| [Test : rapport des deux cas adaptés](Test/Rapport_conformite_deux_CFG_adaptes_epure.md) | Deux couples CFG/JSON et analyse ciblée de fidélité de transformation |
| [Dépendances](wheelhouse/README.md) | Installation reproductible hors ligne |

## Installation

L'installation fournie fonctionne sur **Windows 64 bits avec Python 3.12**.
Elle ne nécessite ni Codex, ni le dépôt de développement, ni un accès Internet :
les dépendances d'exécution aux versions utilisées sont incluses dans `wheelhouse/`.

Depuis la racine de cette copie, dans PowerShell :

```powershell
.\setup.ps1
```

Pour choisir explicitement l'interpréteur Python :

```powershell
.\setup.ps1 -Python C:\Python312\python.exe
```

Les fichiers binaires de dépendances fournis ciblent Python 3.12 / Windows x64.
Ne pas remplacer arbitrairement `ttp_templates` : les quatre templates amont
sont figés et vérifiés à l'exécution par rapport à la version installée.

## Tester dans l'interface Web

```powershell
.\run_ui.ps1
```

Ouvrir **http://127.0.0.1:8000**, puis cliquer sur **Charger un exemple** ou importer
une configuration texte UTF-8 de moins de 2 Mio. Choisir IOS ou IOS-XE et lancer
la normalisation. Les boutons permettent de copier ou télécharger `normalized.json`.

La vue Code et la vue Arborescence présentent le même contrat V1. L'exemple
intégré contient des interfaces, des routes statiques, OSPF, AAA et SSH.

- `true` : activation ou propriété établie ;
- `null` : information indéterminée ;
- `false` : désactivation ou négation établie ;
- `[]` : collection confirmée vide.

Une commande non reconnue ne justifie pas une valeur `false` ou une collection
vide. Les sections racines et les valeurs indéterminées sont conservées.

Le serveur écoute uniquement sur l'interface locale. Les configurations transitent
en mémoire vers `cli.normalize`, dans un processus isolé ; elles ne sont pas
enregistrées comme fichiers par le Web. Les détails internes d'erreur ne sont pas
retournés au navigateur. Le délai maximal est de 120 secondes.

Pour arrêter le serveur, appuyer sur Ctrl+C dans la fenêtre PowerShell.
Si le port 8000 est déjà utilisé, on peut choisir un autre port :

```powershell
$env:CONFIG_STUDIO_PORT = '8001'
.\run_ui.ps1
```

Ouvrir alors http://127.0.0.1:8001.

## Utiliser la ligne de commande

```powershell
.\.venv\Scripts\python.exe cli.py .\resources\C0031_CE1.cfg --output .\outputs\routeur --os-family iosxe
```

La sortie officielle est uniquement `outputs/routeur/normalized.json`.
Elle est validée avec Pydantic et le JSON Schema du contrat. Une erreur de
validation n'est pas masquée pour forcer l'export.

## Architecture et circulation des données

```text
Texte de configuration Cisco
   │
   ├── Masquage des credentials reconnus
   ├── Inventaire des lignes et des blocs
   └── TTP + contrôles de contexte et de commande complète
                │
                ▼
       Captures intermédiaires
                │
                ▼
        NormalizationEngine
       ├── validation des captures
       ├── déclarations des objets structurants
       ├── dispatch vers les domaines métier
       ├── résolution des traitements différés
       └── sélection des faits et protection des politiques partielles
                │
                ▼
         RouterContractV1
       ├── validation Pydantic
       └── validation JSON Schema
                │
                ▼
       Sérialisation → normalized.json
```

Les templates reconnaissent la syntaxe ; les domaines interprètent les captures ;
le contrat fixe leur représentation. Une capture TTP ne prouve donc pas, à elle
seule, qu'un objet métier peut être publié comme complet.

Les contextes permettent de distinguer une commande globale, une commande sous
interface et une commande de processus ou de famille d'adresses. Le moteur conserve
également les références littérales, sans inventer un objet cible absent.

### Sections du contrat

| Section | Contenu prévu |
|---|---|
| `contract_version` | Version du contrat : `1.0.0` |
| `device` | Identité de plateforme lorsqu'elle est établie |
| `system` | Identité logique, administration, AAA et services |
| `interfaces`, `interface_aggregations` | Interfaces L3, adressage et agrégations |
| `network_instances` | Contextes réseau et VRF |
| `routing` | Routes, protocoles et authentification de routage |
| `routing_policies`, `security` | Politiques de routage et ACL |
| `nat`, `vpn`, `qos` | Objets des fonctions correspondantes |
| `mpls`, `multicast`, `pki` | Fonctions avancées |
| `extensions` | Paramètres spécifiques au constructeur retenus dans le contrat |

Ces sections décrivent les capacités structurelles du modèle. Leur alimentation
réelle dépend des commandes reconnues. Les informations internes de parsing,
numéros de ligne et états de validation ne sont pas ajoutés au JSON métier.

## API Python et validation d'un résultat

Depuis un programme exécuté à la racine du dépôt :

```python
from pathlib import Path
from cli import normalize, convert_file

text = Path('resources/C0031_CE1.cfg').read_text(encoding='utf-8-sig')
document = normalize(text, os_family='iosxe')  # Dictionnaire JSON-compatible

document = convert_file(
    'resources/C0031_CE1.cfg',
    'outputs/routeur',
    os_family='iosxe',
)  # Écrit également normalized.json
```

Les templates amont sont activés par défaut. Le CLI permet les mêmes choix :

```powershell
.\.venv\Scripts\python.exe cli.py --help
```

L'entrée est un chemin de fichier ; `--output` désigne le dossier de sortie ;
`--os-family` accepte `ios` ou `iosxe`, avec `ios` par défaut. Ce choix ne convertit
pas une configuration d'une autre plateforme en configuration IOS.

Si `normalized.json` existe déjà dans la destination, il est remplacé. Choisir un
répertoire de sortie distinct des fichiers sources. Le CLI protège contre certaines
destinations pouvant remplacer l'entrée.

Pour vérifier un document existant dans un programme Python :

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

## Hiérarchie du projet

```text
racine/
├── README.md                       # Présentation et utilisation du système
├── GUIDE_DEMONSTRATION_WEB.md       # Préparation et démonstration pas à pas
├── cli.py                          # Point d’entrée CLI et API Python commune
├── webapp.py                       # Backend HTTP local appelant le pipeline
├── setup.ps1                       # Installation Windows/Python 3.12 x64
├── run_ui.ps1                      # Démarrage de l’interface Web
├── requirements.lock               # Versions des dépendances
├── parser/                         # Inventaire, contextes et extraction TTP
├── templates/
│   ├── cisco_ios/                  # Règles personnalisées par domaine
│   ├── upstream/                   # Quatre templates amont figés
│   └── rule_metadata.json          # Métadonnées et restrictions des règles
├── normalizer/
│   ├── engine.py                   # Coordination du moteur métier unique
│   ├── serialization.py            # Préparation de la sortie canonique
│   ├── common/                     # Utilitaires et gestion des faits reconnus
│   └── domains/                    # Mappings interfaces, ACL, services, etc.
│       └── routing/                # BGP, OSPF, RIP, EIGRP, routes et VRF
├── schemas/
│   ├── router_contract_v1.py        # Contrat Pydantic typé et contraintes
│   └── router_contract_v1.schema.json
├── web/
│   └── index.html                  # Interface HTML/CSS/JavaScript
├── resources/                      # 20 configurations de corpus choisies
│   └── eigrp/                      # 3 configurations EIGRP synthétiques
├── Test/                           # 2 démonstrations documentées CFG → JSON
│   ├── 01_IOS15_EDGE_MULTIPROTOCOL_adapte.cfg
│   ├── 01_IOS15_EDGE_MULTIPROTOCOL_adapte.json
│   ├── 02_IOSXE17_PE_L3VPN_QOS_adapte.cfg
│   ├── 02_IOSXE17_PE_L3VPN_QOS_adapte.json
│   └── Rapport_conformite_deux_CFG_adaptes_epure.md
├── docs/                           # Architecture, EIGRP et supports du rapport
├── wheelhouse/                     # Archives des dépendances hors ligne
└── licenses/                       # Licences des éléments tiers concernés
```

Le parser reconnaît les commandes et leurs contextes ; les modules de
`normalizer/domains/` les interprètent et alimentent directement les sous-modèles
Pydantic ; le contrat contrôle la représentation finale. IS-IS et certaines
fonctions Cisco complémentaires sont traités dans `domains/cisco_features.py`.
Les README de chaque composant détaillent cette répartition.

## Contenu du dépôt

| Chemin | Rôle |
|---|---|
| `cli.py` | Points d'entrée du pipeline : API Python et CLI |
| `parser/` | Inventaire, extraction TTP, contextes et masquage des secrets |
| `normalizer/` | Moteur unique, domaines métier et sérialisation |
| `schemas/` | Modèles RouterContractV1 et JSON Schema généré |
| `templates/cisco_ios/` | Templates TTP du projet |
| `templates/upstream/` | Quatre templates amont figés nécessaires à l'exécution |
| `templates/rule_metadata.json` | Restrictions de contexte et valeurs autorisées |
| `webapp.py`, `web/` | Serveur et interface Web locale |
| `resources/` | 23 configurations de démonstration, dont 3 EIGRP ; credentials masqués |
| `Test/` | Deux CFG synthétiques adaptés, leurs JSON fournis et un rapport de fidélité ciblé |
| `setup.ps1`, `run_ui.ps1` | Installation et lancement sous Windows |
| `requirements.lock`, `wheelhouse/` | Dépendances d'exécution reproductibles |
| `licenses/`, `THIRD_PARTY_NOTICES.md` | Attribution des templates amont |

La suite de tests Python du dépôt de développement, ses caches, anciens modèles,
environnements locaux et historique Git ne sont pas inclus. Le dossier **`Test/`**
(avec cette casse) est distinct d’une suite `tests/` : il contient des démonstrations
et leurs résultats JSON conservés pour lecture et comparaison. Les fichiers de
`resources/` et les deux CFG adaptés de `Test/` sont explicitement autorisés dans
`.gitignore`. Les sorties générées sous `outputs/` restent exclues de Git.

## Configurations sélectionnées pour les démonstrations

Le dépôt fournit **25 fichiers CFG** : les **20 configurations de corpus** choisies
précédemment, **3 exemples EIGRP** dans `resources/`, et **2 configurations adaptées**
dans `Test/`. Les deux JSON fournis dans `Test/` sont des résultats de référence à
consulter ; ils ne constituent pas deux configurations supplémentaires.

### Les 20 configurations de corpus

Le tableau indique les fonctions observées dans les fichiers, sans garantir que
chaque commande du domaine est prise en charge. L’inventaire et les précautions
sur les credentials figurent dans [resources/README.md](resources/README.md).

| Configuration | Fonctions observées dans la source |
|---|---|
| [C0031_CE1.cfg](resources/C0031_CE1.cfg) | Interfaces L3, VRF, Routes statiques, SSH, Négations explicites |
| [C0044_CE-1A.cfg](resources/C0044_CE-1A.cfg) | Interfaces L3, VRF, Routes statiques, Négations explicites |
| [C0019_R1.cfg](resources/C0019_R1.cfg) | Interfaces L3, IPv6, VRF, BGP, OSPF, ACL, Négations explicites |
| [C0021_R3.cfg](resources/C0021_R3.cfg) | Interfaces L3, IPv6, BGP, OSPF, Politiques, Négations explicites |
| [C0014_ASBR-2122.cfg](resources/C0014_ASBR-2122.cfg) | Interfaces L3, IPv6, BGP, Négations explicites |
| [C0017_CE-HQ.cfg](resources/C0017_CE-HQ.cfg) | Interfaces L3, BGP, Négations explicites |
| [C0025_R-PrivateASN100.cfg](resources/C0025_R-PrivateASN100.cfg) | Interfaces L3, BGP, Politiques, Négations explicites |
| [C0026_R-PublicASN111.cfg](resources/C0026_R-PublicASN111.cfg) | Interfaces L3, BGP, Politiques, Négations explicites |
| [C0016_CE-BR.cfg](resources/C0016_CE-BR.cfg) | Interfaces L3, RIP, Négations explicites |
| [C0064_PE-1.cfg](resources/C0064_PE-1.cfg) | Interfaces L3, IS-IS, Négations explicites |
| [C0106_CE-1A.cfg](resources/C0106_CE-1A.cfg) | Interfaces L3, VRF, OSPF, Négations explicites |
| [C0148_R1.cfg](resources/C0148_R1.cfg) | Interfaces L3, OSPF, Négations explicites |
| [C0001_as1border1.cfg](resources/C0001_as1border1.cfg) | Interfaces L3, BGP, OSPF, ACL, Politiques, Négations explicites |
| [C0007_as2dept1.cfg](resources/C0007_as2dept1.cfg) | Interfaces L3, BGP, ACL, Politiques, Négations explicites |
| [C0010_as3border1.cfg](resources/C0010_as3border1.cfg) | Interfaces L3, BGP, OSPF, ACL, Politiques, Négations explicites |
| [C0004_as2border1.cfg](resources/C0004_as2border1.cfg) | Interfaces L3, BGP, OSPF, ACL, Politiques, Négations explicites |
| [C0032_CE2.cfg](resources/C0032_CE2.cfg) | Interfaces L3, Routes statiques, BGP, SSH, Négations explicites |
| [C0033_CE3.cfg](resources/C0033_CE3.cfg) | Interfaces L3, Routes statiques, BGP, SSH, Négations explicites |
| [C0042_rt1.bsqmk.cfg](resources/C0042_rt1.bsqmk.cfg) | Interfaces L3, IPv6, VRF, Routes statiques, BGP, OSPF, ACL, Politiques, SSH, Négations explicites |
| [C0123_PE-1.cfg](resources/C0123_PE-1.cfg) | Interfaces L3, VRF, BGP, OSPF, IS-IS, ACL, Négations explicites |

### Les trois exemples EIGRP

| Configuration | Fonctions principales |
|---|---|
| [classic_ipv4.cfg](resources/eigrp/classic_ipv4.cfg) | AS classique 100, networks/wildcards, passivité, métriques, redistribution, filtres et AF VRF BLUE/AS 200. |
| [classic_ipv6.cfg](resources/eigrp/classic_ipv6.cfg) | AS IPv6 20, activation d’interface, timers, authentification et résumé ; référence AS 99 non résolue conservée. |
| [named_dualstack.cfg](resources/eigrp/named_dualstack.cfg) | Processus CAMPUS, IPv4/IPv6, VRF BLUE, af-interface default et exceptions, topologies base/VOICE. |

Les [résultats attendus EIGRP](resources/eigrp/README.md) expliquent les propriétés
à examiner. Ces fichiers se chargent dans la même interface Web que les autres CFG.

## Dossier Test : deux cas de transformation documentés

Le dossier `Test/` contient **cinq fichiers**, lus conjointement :

| Cas | Configuration | JSON fourni | Domaines présents |
|---|---|---|---|
| IOS 15 EDGE | [CFG 01](Test/01_IOS15_EDGE_MULTIPROTOCOL_adapte.cfg) | [JSON 01](Test/01_IOS15_EDGE_MULTIPROTOCOL_adapte.json) | 10 interfaces, sous-interfaces L3, IPv4/IPv6, VRF MGMT, BGP, OSPFv2/v3, routes statiques, ACL, politiques, multicast et administration. |
| IOS-XE 17 PE | [CFG 02](Test/02_IOSXE17_PE_L3VPN_QOS_adapte.cfg) | [JSON 02](Test/02_IOSXE17_PE_L3VPN_QOS_adapte.json) | 10 interfaces, trois VRF, BGP VPNv4, OSPF par VRF, IS-IS, MPLS/LDP, politiques AS-PATH, ACL, QoS, PKI et administration. |

Le cinquième fichier est le [rapport de comparaison CFG/JSON](Test/Rapport_conformite_deux_CFG_adaptes_epure.md).
Les sources sont des configurations **synthétiques adaptées**, marquées
**DO NOT DEPLOY** : elles servent à la démonstration de la normalisation.
Ces deux cas ne contiennent pas EIGRP ; utiliser `resources/eigrp/` pour ce protocole.

### Interprétation du rapport fourni

Le rapport annonce **129 assertions ciblées réussies pour le cas 01** et **104 pour
le cas 02**, soit **233/233**. Ces chiffres décrivent ses comparaisons des fichiers
fournis. Le vérificateur indépendant évoqué n’est pas livré dans `Test/`, qui ne
contient aucun script de tests automatisés. Le rapport précise qu’il n’a pas
réexécuté le parser ni un routeur Cisco.

La « conformité » de ce document désigne la **fidélité de transformation sur les
contrôles ciblés**, sans verdict CIS/STIG ou preuve de fonctionnement réseau.
233 assertions réussies ne prouvent pas la couverture exhaustive de toutes les
commandes. Les références, valeurs et cardinalités effectivement comparées sont
détaillées dans le rapport.

Les nuances conservées incluent `send_community = command_without_option`, une
technologie de tunnel `unknown` faute de mode explicite et `routing.isis[0].declared`
à `null` dans le JSON 02. Les champs de plateforme et l’activation SSH peuvent
également rester indéterminés. Ces distinctions ne doivent pas être effacées pour
présenter une couverture artificiellement complète.

### Rejouer les deux cas

Dans le Web : importer le CFG 01 ou 02, choisir respectivement IOS ou IOS-XE,
normaliser puis comparer les sections utiles avec le JSON fourni. Ne pas importer
le fichier JSON dans la zone de configuration CLI.

Depuis PowerShell, à la racine et après `setup.ps1` :

```powershell
.\.venv\Scripts\python.exe cli.py .\Test\01_IOS15_EDGE_MULTIPROTOCOL_adapte.cfg --output .\outputs\test01 --os-family ios
.\.venv\Scripts\python.exe cli.py .\Test\02_IOSXE17_PE_L3VPN_QOS_adapte.cfg --output .\outputs\test02 --os-family iosxe
```

Les résultats sont écrits dans `outputs/test01/normalized.json` et
`outputs/test02/normalized.json`. Ces commandes conservent les JSON fournis dans
`Test/`. Chaque conversion utilise la validation du pipeline. Une comparaison
métier doit examiner les valeurs, références et contextes ; un simple changement
de mise en forme JSON n’est pas une régression fonctionnelle.

## Périmètre et limites

Les domaines alimentés comprennent les interfaces L3, VRF, routes statiques,
BGP, OSPF, IS-IS, RIP, EIGRP, ACL, politiques de routage, services administratifs, AAA,
SSH et les fonctions avancées déjà reconnues par les templates. L'authentification
des protocoles de routage conserve les méthodes et références utiles sans exporter
les secrets. La couverture dépend des commandes effectivement reconnues.

Les fonctionnalités de commutation L2 exclues ne sont pas produites dans le
contrat V1. Des règles de parsing historiques sont conservées pour préserver
la reconnaissance des contextes et leur exclusion du modèle métier. NAT/VPN
conservent leur couverture existante ; les fonctions non extraites restent
indéterminées. Le projet ne produit ni verdict d'audit ni score de conformité.

## Dépannage

| Situation | Vérification ou action |
|---|---|
| Python absent ou mauvaise version | Utiliser Python 3.12 x64 et préciser `-Python` si nécessaire |
| Échec d'installation | Vérifier les archives ; éviter un chemin excessivement long sous Windows |
| `.venv` absent | Exécuter `setup.ps1` avant de lancer l'application |
| Port déjà utilisé | Arrêter le serveur concerné ou changer `CONFIG_STUDIO_PORT` |
| Serveur non connecté dans la page | Utiliser l'adresse HTTP locale et vérifier que le serveur exécute le code courant |
| HTTP 400 / 413 / 415 | Vérifier le texte UTF-8, la taille et le format de requête |
| HTTP 422 | Une signature de plateforme non prise en charge a été détectée |
| HTTP 429 | Attendre la fin de la normalisation en cours |
| HTTP 500 | Reproduire avec le CLI pour diagnostiquer l'entrée ou la validation |
| HTTP 504 | Le traitement a dépassé 120 secondes |
| Champ à `null` | Vérifier la commande, son contexte et sa couverture ; ne pas conclure à une désactivation |
| Politique absente du résultat | Une reconnaissance partielle peut empêcher sa publication complète |
| `OfficialTemplateError` | Vérifier les dépendances figées et les quatre snapshots amont |

Vérification simple du serveur :

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

La réponse attendue contient `status: ok`, `ready: true` et
`contract: RouterContractV1`.

## Publication sur GitHub

Utiliser **le contenu de ce dossier comme racine du nouveau dépôt**. Aucun dépôt
Git ni accès GitHub n'est configuré par cette préparation. Ne pas copier le dépôt
de développement, ses sorties ou ses configurations réelles dans cette racine.

## Synchronisation EIGRP et démonstration

Cette copie contient les dernières sources du dépôt original, y compris les modes
EIGRP classique IPv4/IPv6 et nommé, leurs AF/VRF, topologies, interfaces et paramètres
reconnus. Les 3 exemples de `resources/eigrp/` peuvent être importés directement dans
le Web. La [couverture EIGRP](docs/eigrp/README.md) détaille les limites ; elle ne
prétend pas couvrir toutes les syntaxes de toutes les images Cisco.

Les modèles et le JSON Schema ont été synchronisés. Les nouvelles propriétés
peuvent être null en l'absence de commandes reconnues. Le serveur Web doit être
redémarré après une mise à jour des modèles Python.
