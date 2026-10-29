# Interface Web locale — Config Studio

[Guide général](../README.md) · [Contrat](../schemas/README.md) · [Exemples](../resources/README.md)

## Composants

`index.html` contient l'interface HTML, les styles CSS et le JavaScript. Le serveur
Python se trouve dans `webapp.py`, à la racine du dépôt. Aucun framework frontend
ou serveur Web externe n'est requis.

Le frontend gère la saisie et l'affichage. Le backend appelle `cli.normalize` ; il
ne possède pas de règles de normalisation métier distinctes.

## Lancement

Exécuter à la racine après l'installation :

```powershell
.\run_ui.ps1
```

Ouvrir http://127.0.0.1:8000. La page et l'API doivent utiliser la même origine.
Le chargement direct du fichier HTML depuis le disque ne fournit pas le backend.
Ctrl+C dans la fenêtre du serveur l'arrête.

Pour un autre port :

```powershell
$env:CONFIG_STUDIO_PORT = '8001'
.\run_ui.ps1
```

## Utilisation

1. Charger l'exemple intégré, importer un fichier ou coller la configuration.
2. Choisir IOS ou IOS-XE.
3. Lancer le traitement avec le bouton ou Ctrl+Entrée.
4. Consulter **Code** ou **Arborescence**.
5. Copier le résultat ou télécharger `normalized.json`.

Le bouton de téléchargement produit une version formatée du même objet JSON que
celui affiché. Les valeurs `null`, `false`, zéro et collections vides sont conservées.
Modifier la source ou la famille invalide le résultat affiché précédent.

Une configuration dont aucune donnée métier n'est normalisée peut produire un
contrat valide composé de propriétés indéterminées. La page présente alors un
avertissement plutôt que d'assimiler les seules sections racines à des faits reconnus.

## Fonctionnement du backend

```text
Navigateur → POST /api/normalize
           → validation de l'entrée
           → processus Python isolé appelant cli.normalize
           → revalidation RouterContractV1
           → réponse JSON
```

La configuration et le résultat transitent par les flux mémoire du processus.
Le Web ne crée pas de fichiers de configuration ou de résultats temporaires.
L'isolation du processus permet de conserver un délai maximal de 120 secondes.
Un verrou limite le serveur à une normalisation en cours ; les autres demandes
de normalisation reçoivent un statut 429.

Les sorties et erreurs internes du processus ne sont pas renvoyées au navigateur
ni affichées comme diagnostics contenant des valeurs de configuration.

## Routes HTTP

| Route | Fonction |
|---|---|
| `GET /` ou `GET /index.html` | Page Config Studio |
| `GET /api/health` | Disponibilité et identification du contrat |
| `POST /api/normalize` | Normalisation d'une configuration |

Les autres fichiers du dépôt ne sont pas servis comme un répertoire Web public.

### État du serveur

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Réponse attendue :

```json
{"status":"ok","engine":"cli.normalize","contract":"RouterContractV1","ready":true}
```

`ready` vérifie la présence du point d'entrée CLI ; cette route n'exécute pas une
normalisation de contrôle complète.

### Demande de normalisation

Le contenu doit être `application/json` :

```json
{"configuration":"hostname WEB-DEMO\n","os_family":"iosxe"}
```

`os_family` est facultatif et vaut `ios` par défaut. Une réponse réussie comporte
`normalized`, le document canonique, et `duration_ms`, la durée de traitement.

Exemple PowerShell :

```powershell
$payload = @{ configuration = "hostname WEB-DEMO`n"; os_family = 'iosxe' } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/normalize -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($payload))
```

## Limites et codes de réponse

L'interface accepte un texte UTF-8 non vide, sans octet nul, jusqu'à 2 Mio de
configuration. Le backend limite aussi la taille de la requête JSON à 12 Mio.
Le serveur écoute uniquement sur `127.0.0.1` et contrôle l'hôte ainsi que l'origine
des requêtes de normalisation.

| Statut | Signification |
|---|---|
| 200 | Traitement réussi |
| 400 | Entrée ou JSON invalide |
| 403 | Hôte ou origine de requête non autorisé |
| 404 | Route inconnue |
| 413 | Taille excessive ou corps de requête vide |
| 415 | Type de contenu incorrect |
| 422 | Signature de plateforme non prise en charge |
| 429 | Normaliseur déjà occupé |
| 500 | Échec interne ou document invalide |
| 504 | Délai maximal dépassé |

Une commande individuelle non reconnue ne produit pas nécessairement une erreur
HTTP. Sa couverture est traitée par le pipeline ; ses valeurs inconnues ne doivent
pas être inventées. Pour diagnostiquer une erreur du moteur, utiliser le CLI décrit
dans le guide général.

## Préparation et essais EIGRP

Le [guide pas à pas](../GUIDE_DEMONSTRATION_WEB.md) fournit les commandes de clonage
GitHub, création de l'environnement, installation hors ligne et lancement. Il
décrit aussi les contrôles CLI/API et les résultats attendus.

Les fichiers [EIGRP distribués](../resources/eigrp/README.md) s'importent avec le même
sélecteur que les autres configurations. Ouvrir `routing`, puis `eigrp` dans
l'arborescence pour examiner les processus et leurs AF/topologies. Le frontend
affiche le contrat synchronisé et utilise le même backend que le CLI.
