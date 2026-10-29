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
| `setup.ps1`, `run_ui.ps1` | Installation et lancement sous Windows |
| `requirements.lock`, `wheelhouse/` | Dépendances d'exécution reproductibles |
| `licenses/`, `THIRD_PARTY_NOTICES.md` | Attribution des templates amont |

Les tests, sorties de validation, caches, anciens modèles, environnements Python
locaux et historiques Git du dépôt de travail ne font pas partie de cette copie.
Seules les configurations de démonstration sélectionnées et adaptées dans
`resources/` sont incluses. Les autres configurations et les sorties créées lors
de l'utilisation sont exclues par `.gitignore` pour éviter de les publier par accident.

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
