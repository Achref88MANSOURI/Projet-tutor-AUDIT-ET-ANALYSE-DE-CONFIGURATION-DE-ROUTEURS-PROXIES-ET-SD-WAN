# Guide complet — cloner, préparer et tester Config Studio

[README principal](README.md) · [API Web](web/README.md) · [Exemples](resources/README.md) · [EIGRP](docs/eigrp/README.md)

Ce guide accompagne une première utilisation, depuis la récupération du dépôt
GitHub jusqu'au téléchargement d'un JSON validé. Les commandes sont prévues pour
**PowerShell sous Windows x64, avec Python 3.12**.

La distribution contient le normaliseur, son interface Web, les dépendances hors
ligne et **23 configurations de démonstration**, dont trois exemples EIGRP.

## 1. Vérifier les prérequis

Ouvrir PowerShell et exécuter :

```powershell
git --version
py -3.12 --version
```

La première commande doit afficher une version de Git. La seconde doit afficher
Python 3.12.x. Si une commande est introuvable, installer Git pour Windows ou Python
3.12 x64, puis rouvrir PowerShell. Le clonage GitHub nécessite une connexion réseau ;
une fois le code et Python disponibles, l'installation des dépendances fournie est
hors ligne. Les archives binaires incluses ciblent cette plateforme.

## 2. Cloner le dépôt GitHub

Le dépôt GitHub du projet peut être récupéré avec les commandes suivantes :

```powershell
$DepotGitHub = 'https://github.com/Achref88MANSOURI/-Projet-tutor-AUDIT-ET-ANALYSE-DE-CONFIGURATION-DE-ROUTEURS-PROXIES-ET-SD-WAN.git'
$DossierTravail = Join-Path $env:USERPROFILE 'Documents\Projets'

New-Item -ItemType Directory -Path $DossierTravail -Force | Out-Null
Set-Location -LiteralPath $DossierTravail
git clone $DepotGitHub normaliseur-routeurs
Set-Location -LiteralPath '.\normaliseur-routeurs'
```

Choisir un autre nom local si `normaliseur-routeurs` existe déjà. Pour un dépôt
privé, le compte utilisé pour le clonage doit disposer d'un accès au dépôt.

Vérifier que la racine contient les fichiers nécessaires :

```powershell
Get-ChildItem
Test-Path .\setup.ps1
Test-Path .\webapp.py
Test-Path .\resources\eigrp\named_dualstack.cfg
```

Les trois dernières commandes doivent renvoyer `True`. Le contenu du dossier
préparé `à exporter` doit être la racine du nouveau dépôt GitHub. Un clone doit
donc contenir directement `setup.ps1`, `parser/`, `normalizer/`, `web/`, etc.

Alternative : télécharger le ZIP du dépôt, l'extraire puis ouvrir PowerShell dans
le dossier contenant ces fichiers. Préférer un chemin court, notamment pour
l'installation des bibliothèques TTP sous Windows.

## 3. Préparer l'environnement Python

Depuis la racine du clone :

```powershell
.\setup.ps1
```

Le script sélectionne Python 3.12, vérifie Windows x64, crée `.venv` et installe les
versions de `requirements.lock` depuis `wheelhouse/`. Il termine par un message
indiquant que l'environnement est prêt.

Si plusieurs versions de Python sont installées, préciser l'interpréteur :

```powershell
.\setup.ps1 -Python C:\Python312\python.exe
```

Adapter le chemin à l'installation réelle. Vérifier ensuite :

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip check
```

La version doit être 3.12.x et `pip check` ne doit pas signaler de dépendance cassée.
Il n'est pas nécessaire d'activer l'environnement : les commandes utilisent son
interpréteur explicitement.

### Si PowerShell bloque les fichiers `.ps1`

La même préparation peut être réalisée avec les commandes Python suivantes,
sans changer la politique d'exécution PowerShell :

```powershell
py -3.12 -m venv --copies .venv
.\.venv\Scripts\python.exe -m pip install --no-index --find-links .\wheelhouse -r .\requirements.lock
```

Conserver les versions fournies : le parser compare les quatre templates amont
installés à leurs snapshots locaux.

## 4. Configurer le port et lancer le Web

Le port par défaut est **8000** :

```powershell
.\run_ui.ps1
```

Ouvrir alors **http://127.0.0.1:8000**.

Si le dépôt original ou une autre application utilise déjà ce port, réserver par
exemple **8001** à cette copie :

```powershell
$env:CONFIG_STUDIO_PORT = '8001'
.\run_ui.ps1
```

Ouvrir alors **http://127.0.0.1:8001**. La variable est définie dans la session
PowerShell actuelle. Conserver la fenêtre du serveur ouverte pendant les essais.

Si les scripts PowerShell sont bloqués, lancer le même backend directement :

```powershell
$env:CONFIG_STUDIO_PORT = '8001'
.\.venv\Scripts\python.exe .\webapp.py
```

Le terminal affiche l'adresse à ouvrir. La page HTML et l'API doivent être servies
par ce backend ; ouvrir directement `web/index.html` depuis le disque ne suffit pas.
Le serveur reste local à la machine.

Les paramètres d'utilisation à choisir sont le port HTTP et la famille IOS/IOS-XE
de chaque normalisation. L'application analyse des configurations statiques : les
adresses et identifiants présents dans les exemples sont des données à interpréter.

## 5. Vérifier la connexion au serveur

La page doit afficher **Serveur local connecté** et le résultat doit être identifié
comme **RouterContractV1**.

Dans une seconde fenêtre PowerShell :

```powershell
$PortDemo = 8001
Invoke-RestMethod "http://127.0.0.1:$PortDemo/api/health"
```

Utiliser 8000 si ce port a été choisi. La réponse attendue contient :

```json
{"status":"ok","engine":"cli.normalize","contract":"RouterContractV1","ready":true}
```

Cette route identifie le backend ; le test de normalisation suivant vérifie le
pipeline complet.

## 6. Premier essai dans l'interface

1. Cliquer sur **Charger un exemple** : la zone de texte reçoit un exemple synthétique.
2. Choisir **Cisco IOS** ou **Cisco IOS-XE**.
3. Cliquer sur **Normaliser la configuration**, ou utiliser Ctrl+Entrée.
4. Attendre le message de réussite et la durée du traitement.
5. Consulter la vue **Code**, puis la vue **Arborescence**.
6. Utiliser **Copier** ou **Télécharger** pour récupérer `normalized.json`.

L'exemple intégré couvre notamment interfaces, routes statiques, OSPF, AAA et SSH.
Les fichiers importés doivent être des textes UTF-8 jusqu'à 2 Mio. Le serveur
traite une normalisation à la fois, avec un délai maximal de 120 secondes.

## 7. Essayer EIGRP

Utiliser le bouton d'import ou le glisser-déposer et choisir un fichier dans
`resources/eigrp/` :

| Fichier | Ce qu'il permet de vérifier |
|---|---|
| `classic_ipv4.cfg` | Processus AS 100, réseaux/wildcards, passivité, paramètres d'interface et AF VRF BLUE avec AS 200 |
| `classic_ipv6.cfg` | Processus IPv6 AS 20, activation d'interface et référence AS 99 conservée sans processus inventé |
| `named_dualstack.cfg` | Processus CAMPUS, trois AF, VRF BLUE, blocs d'interface, topologies et authentification |

Sélectionner IOS-XE pour la démonstration nommée et lancer la normalisation. Dans
l'arborescence, ouvrir `configuration`, puis `routing`, `eigrp`, puis l'élément `0`.

Pour `named_dualstack.cfg`, on doit retrouver :

- `mode: named` et `name: CAMPUS` ;
- l'AF IPv4 unicast de BLUE avec AS 100 ;
- l'AF IPv6 avec AS 200 et son `enabled: false` explicitement configuré ;
- une troisième AF IPv4 avec AS 300 ;
- la topologie `base` de BLUE avec `variance: 3` ;
- un bloc `interface: default` distinct de `GigabitEthernet0/0` ;
- les méthodes/références d'authentification reconnues, sans valeur secrète brute.

L'AS du processus nommé est porté par ses AF : un `autonomous_system: null` au
niveau du processus n'est pas une erreur. Les credentials des fichiers distribués
ont été remplacés par des marqueurs ; ces exemples sont destinés à la normalisation.

## 8. Interpréter les valeurs correctement

| Valeur | Signification |
|---|---|
| `true` | Activation ou propriété établie |
| `false` | Désactivation ou négation établie |
| `null` | Information indéterminée |
| `[]` | Collection confirmée vide |

Une commande absente n'établit pas automatiquement une désactivation. Une référence
à une VRF ou à une key chain ne crée pas une cible fictive. Un champ non renseigné
peut aussi correspondre à une commande non prise en charge.

La [documentation EIGRP](docs/eigrp/README.md) décrit les syntaxes couvertes et les
limites. Les fonctions L2 exclues, paramètres opérationnels et résultats d'audit
ne sont pas ajoutés au contrat.

## 9. Tester aussi en ligne de commande

Dans une autre fenêtre PowerShell, revenir à la racine du clone :

```powershell
Set-Location -LiteralPath (Join-Path $env:USERPROFILE 'Documents\Projets\normaliseur-routeurs')
.\.venv\Scripts\python.exe cli.py .\resources\eigrp\named_dualstack.cfg --output .\outputs\eigrp-nomme --os-family iosxe
```

Adapter ce chemin si un autre dossier de clonage ou une extraction ZIP a été choisi.

Le terminal affiche le chemin de `outputs/eigrp-nomme/normalized.json`. Pour examiner
le processus sans imprimer tout le document :

```powershell
$Resultat = Get-Content .\outputs\eigrp-nomme\normalized.json -Raw -Encoding UTF8 | ConvertFrom-Json
$Resultat.contract_version
$Resultat.routing.eigrp[0].name
$Resultat.routing.eigrp[0].address_families.Count
$Resultat.routing.eigrp[0].address_families[0].topologies[0].variance
```

Les valeurs attendues sont respectivement `1.0.0`, `CAMPUS`, `3` et `3`.

La sortie officielle est uniquement `normalized.json`. Le CLI et le Web utilisent
le même pipeline et le même contrat ; la mise en forme du texte JSON peut différer.

## 10. Vérifier Pydantic et JSON Schema

Après le test CLI précédent, exécuter ce bloc à la racine :

```powershell
@'
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from schemas.router_contract_v1 import RouterContractV1, router_contract_v1_schema

payload = json.loads(Path('outputs/eigrp-nomme/normalized.json').read_text(encoding='utf-8'))
model = RouterContractV1.model_validate(payload)
Draft202012Validator(router_contract_v1_schema(), format_checker=FormatChecker()).validate(payload)
assert model.routing.eigrp[0].name == 'CAMPUS'
assert len(model.routing.eigrp[0].address_families) == 3
print('Validation Pydantic et JSON Schema : OK')
'@ | .\.venv\Scripts\python.exe -
```

Les bibliothèques nécessaires sont incluses dans l'installation ; pytest n'est pas
requis pour ce contrôle. Une validation réussie garantit la cohérence structurelle,
sans prouver que toutes les commandes du fichier ont été reconnues.

## 11. Tester l'API Web directement

Dans une seconde fenêtre PowerShell, depuis la racine :

```powershell
Set-Location -LiteralPath (Join-Path $env:USERPROFILE 'Documents\Projets\normaliseur-routeurs')
$PortDemo = 8001
$Configuration = Get-Content .\resources\eigrp\named_dualstack.cfg -Raw -Encoding UTF8
$Corps = @{ configuration = $Configuration; os_family = 'iosxe' } | ConvertTo-Json
$Reponse = Invoke-RestMethod -Uri "http://127.0.0.1:$PortDemo/api/normalize" -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($Corps))
$Reponse.normalized.routing.eigrp[0].name
$Reponse.duration_ms
```

Le premier résultat doit être `CAMPUS`. Le second est une durée variable en
millisecondes. Adapter le port à celui du serveur réellement lancé.

## 12. Arrêter et mettre à jour

Dans la fenêtre du serveur, Ctrl+C arrête le service. Pour appliquer une mise à jour
GitHub, depuis la racine d'un clone Git :

```powershell
git pull --ff-only
.\setup.ps1
.\run_ui.ps1
```

Arrêter le serveur avant la mise à jour, puis le relancer : les modèles Python
déjà chargés ne sont pas remplacés par un simple rafraîchissement du navigateur.
Conserver le même port, ou adapter l'adresse ouverte, et recharger la page.

## 13. Dépannage rapide

| Problème | Action |
|---|---|
| `git` ou Python introuvable | Installer le programme requis et rouvrir PowerShell |
| Erreur d'accès au clone privé | Vérifier les droits d'accès au dépôt GitHub |
| Fichiers `setup.ps1`/`webapp.py` absents | Se placer dans la véritable racine de la distribution |
| Mauvaise version/architecture Python | Utiliser Python 3.12 x64, éventuellement via `-Python` |
| Installation échouée | Vérifier les archives et raccourcir un chemin d'installation trop long |
| Script PowerShell bloqué | Utiliser les commandes Python équivalentes de ce guide |
| Port occupé | Choisir un autre `CONFIG_STUDIO_PORT` ou arrêter le serveur concerné |
| Badge non connecté | Vérifier l'adresse, le port et la version du backend |
| HTTP 413 | Réduire la taille du fichier, limitée à 2 Mio de configuration |
| HTTP 422 | Utiliser une configuration d'une plateforme prise en charge |
| HTTP 429 | Attendre la fin du traitement déjà en cours |
| HTTP 500 | Reproduire l'entrée avec le CLI pour diagnostiquer la validation |
| HTTP 504 | Le délai de 120 secondes a été dépassé |
| Champ `null` ou objet absent | Consulter la couverture et vérifier le contexte, sans inventer de valeur |

## Validation de la copie fournie

Les sources d'exécution sont synchronisées avec le dépôt original incluant EIGRP.
La préparation est vérifiée dans une copie isolée, avec installation hors ligne,
parcours CLI, backend Web et validation du contrat. Les tests de développement et
leurs sorties ne sont pas inclus dans cette distribution ; les essais ci-dessus
utilisent les exemples livrés.
