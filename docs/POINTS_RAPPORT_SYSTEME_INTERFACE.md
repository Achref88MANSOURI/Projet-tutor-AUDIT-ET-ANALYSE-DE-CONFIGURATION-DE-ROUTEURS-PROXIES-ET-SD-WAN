# Points à présenter dans le rapport : système et interface graphique

Ce document propose un plan et des descriptions réutilisables dans le rapport du projet. Il décrit le système livré dans le dossier « à exporter ». Pour les commandes complètes de préparation et de test, consulter le [guide de démonstration](../GUIDE_DEMONSTRATION_WEB.md).

## 1. Présentation et objectif du système

Le projet transforme une configuration textuelle de routeur Cisco IOS/IOS-XE en un document JSON structuré, typé et validé. Les commandes propres au constructeur sont interprétées pour alimenter un contrat canonique nommé `RouterContractV1`.

Les principaux objectifs à mentionner sont :

- Centraliser les paramètres reconnus dans une représentation cohérente.
- Préserver les contextes : interface, processus de routage, famille d’adresses, VRF, voisin et niveau de protocole.
- Distinguer les valeurs établies des informations indéterminées.
- Faciliter la consultation, l’échange et une exploitation ultérieure des configurations.
- Proposer une utilisation en ligne de commande et dans une interface graphique locale, avec le même moteur.

Le contrat vise une représentation multi-constructeur, tandis que la couverture de parsing livrée concerne actuellement Cisco IOS/IOS-XE. Le système normalise des configurations ; il ne mesure pas l’état réel d’un routeur et ne produit pas de verdict d’audit.

## 2. Architecture générale et circulation des données

```text
                  Utilisateur
                       |
           +-----------+-----------+
           |                       |
     Navigateur Web           Ligne de commande
     web/index.html               cli.py
           |
        webapp.py
           |
           +-----------+-----------+
                       |
              Point d’entrée commun
                       |
           Préparation et parsing TTP
                       |
             Captures contextualisées
                       |
              NormalizationEngine
                       |
             Mappings par domaine
                       |
                RouterContractV1
                       |
        Validation et sérialisation JSON
                       |
       Affichage Web / normalized.json
```

Les trois responsabilités essentielles sont distinctes : les **templates** reconnaissent la syntaxe, les **mappings métier** interprètent les captures, et le **contrat** définit les objets et contraintes de sortie. L’interface Web ajoute un moyen d’interaction ; elle n’introduit pas un deuxième normaliseur.

## 3. Hiérarchie du projet et rôle des composants

Arborescence simplifiée des principaux éléments distribués :

```text
racine/
├── cli.py
├── webapp.py
├── setup.ps1
├── run_ui.ps1
├── requirements.lock
├── README.md
├── GUIDE_DEMONSTRATION_WEB.md
├── parser/
├── templates/
│   ├── cisco_ios/
│   ├── upstream/
│   └── rule_metadata.json
├── normalizer/
│   ├── engine.py
│   ├── serialization.py
│   ├── common/
│   └── domains/
│       └── routing/
├── schemas/
│   ├── router_contract_v1.py
│   └── router_contract_v1.schema.json
├── web/
│   └── index.html
├── resources/
│   └── eigrp/
├── docs/
├── licenses/
└── wheelhouse/
```

| Élément | Rôle à expliquer dans le rapport |
|---|---|
| `cli.py` | Point d’entrée du traitement, utilisable en ligne de commande et appelé par le backend Web. |
| `webapp.py` | Serveur HTTP local : sert la page, contrôle les requêtes et appelle le pipeline dans un processus isolé. |
| `web/index.html` | Interface du navigateur, avec HTML, CSS et JavaScript pour la saisie, l’envoi et l’exploration du JSON. |
| `parser/` | Préparation du texte, inventaire des lignes et contextes, masquage des secrets reconnus, exécution TTP et contrôle des captures. |
| `templates/cisco_ios/` | Règles TTP personnalisées organisées par domaines et protocoles. |
| `templates/upstream/` | Copies figées de templates amont utilisées avec la version correspondante de `ttp_templates`. |
| `templates/rule_metadata.json` | Métadonnées des règles utilisées pour leur traitement et leur qualification. |
| `normalizer/engine.py` | Coordination des déclarations d’objets, du dispatch métier, des traitements différés et de la sélection des faits publiables. |
| `normalizer/common/` | Fonctions partagées de normalisation, gestion des faits et des preuves nécessaires à certaines absences. |
| `normalizer/domains/` | Mappings spécialisés qui alimentent directement les sous-modèles du contrat. |
| `normalizer/serialization.py` | Préparation de la sortie officielle et respect des conventions de sérialisation. |
| `schemas/router_contract_v1.py` | Modèles Pydantic, types, références et contraintes de cohérence du contrat. |
| `schemas/router_contract_v1.schema.json` | JSON Schema généré à partir des modèles pour contrôler la structure des documents exportés. |
| `resources/` | 23 configurations de démonstration, dont trois exemples EIGRP. |
| `wheelhouse/` et `requirements.lock` | Dépendances et versions pour l’installation hors ligne fournie. |
| `setup.ps1` | Préparation de l’environnement Python et installation des dépendances. |
| `run_ui.ps1` | Lancement du serveur de l’interface graphique. |
| `docs/`, README et `licenses/` | Documentation d’utilisation, couverture documentée et informations de licences. |

## 4. Templates TTP et parser

TTP permet d’extraire des valeurs à partir de motifs correspondant aux commandes de configuration. Un template définit les formes reconnues et les captures associées. Les templates sont répartis par domaine afin de faciliter leur lecture et leur maintenance.

Le parser ne se limite pas à rechercher des mots : il tient compte des blocs de configuration et des portées. Une commande située sous une interface ne doit pas être associée à un processus de routage global. Des contrôles spécifiques préservent aussi les contextes imbriqués, notamment pour EIGRP.

Points importants à présenter :

- L’inventaire distingue les lignes et les blocs avant leur interprétation métier.
- Les contrôles de contexte et de commande complète limitent les associations incorrectes.
- Les mécanismes de masquage protègent les secrets reconnus avant leur exploitation par le parsing.
- Les captures sont une représentation intermédiaire ; elles ne constituent pas encore le JSON canonique.
- Une commande non reconnue ne donne pas automatiquement une valeur désactivée ou une collection vide.

## 5. Mappings et domaines métier

Un mapping transforme une capture technique en un objet métier : conversion des types, choix du champ canonique, conservation de l’ordre et association au bon contexte. Les modules écrivent directement dans `RouterContractV1`.

| Module ou groupe | Responsabilité principale |
|---|---|
| `interfaces.py` | Interfaces L3, sous-interfaces, adressage, état administratif, VRF, encapsulations routées et agrégations. |
| `routing/` | Routes statiques, BGP, OSPF, RIP, EIGRP, contextes réseau et fonctions associées selon les règles reconnues. |
| `cisco_features.py` | Notamment IS-IS, MPLS, multicast et certains paramètres Cisco complémentaires. |
| `acl.py` | ACL typées, règles ordonnées, actions, adresses, ports et options reconnues. |
| `policies.py` | Politiques de routage et protection contre la publication trompeuse d’objets partiellement reconnus. |
| `services.py` et `aaa_administration.py` | Administration, AAA, SSH, lignes et services de supervision reconnus. |
| `nat.py`, `vpn.py`, `qos.py`, `pki.py` | Fonctions correspondantes dans les limites de la couverture existante. |

La répartition des fichiers ne correspond pas strictement aux sections JSON : plusieurs modules peuvent contribuer à une section. L’ordre des règles ACL et des méthodes AAA, les références et la séparation des paramètres globaux et locaux ont une signification métier à préserver.

Exemple simple : la commande `shutdown` sous une interface conduit à `admin_enabled: false` pour cette interface. Elle ne permet pas de déduire son état opérationnel réel.

## 6. Contrat canonique et validation

Le contrat comporte notamment les sections `device`, `system`, `interfaces`, `interface_aggregations`, `network_instances`, `routing`, `routing_policies`, `security`, `nat`, `vpn`, `qos`, `mpls`, `multicast`, `pki` et `extensions`, ainsi que sa version.

Pydantic contrôle les types et la cohérence des objets. Le JSON Schema représente les contraintes structurelles exportables. La validation d’un document confirme sa conformité au contrat ; elle ne prouve pas que toutes les commandes de la configuration source ont été couvertes.

| Valeur | Signification à retenir |
|---|---|
| `true` | Activation ou propriété établie. |
| `false` | Désactivation ou négation établie. |
| `null` | Information indéterminée. |
| `[]` | Collection dont le caractère vide est établi. |
| Liste renseignée | Éléments connus, sans garantie automatique d’exhaustivité. |

Ces conventions évitent de présenter une information absente comme une absence démontrée. Les fonctionnalités L2 exclues du contrat cible ne doivent pas être présentées comme couvertes. Les fonctions prévues dans le modèle mais non alimentées restent indéterminées.

## 7. Interface graphique : présentation et choix techniques

L’interface porte le nom **Config Studio**. Elle fonctionne dans un navigateur connecté à un serveur Python local. Le frontend utilise HTML, CSS et JavaScript, sans framework frontend ni serveur Web externe requis.

La page est organisée autour de deux espaces :

- **Configuration source** : import du fichier, glisser-déposer, choix Cisco IOS ou IOS-XE et zone de texte modifiable.
- **Résultat normalisé** : consultation en vue Code ou Arborescence, copie et téléchargement du JSON.

Les éléments à commenter dans le rapport sont le bouton **Charger un exemple**, l’indicateur de disponibilité du serveur, le bouton **Normaliser la configuration**, le raccourci **Ctrl + Entrée**, les deux modes de consultation et les actions **Copier** et **Télécharger**.

La vue Code expose la représentation JSON textuelle. La vue Arborescence facilite l’exploration des sections imbriquées, par exemple `routing` puis `eigrp`. Les deux vues présentent le même document. Modifier la source ou le système sélectionné invalide le résultat précédent.

## 8. Utilisation : de la préparation au résultat

### Préparer et lancer

L’environnement fourni cible **Windows x64 avec Python 3.12**. Après récupération du dépôt, ouvrir PowerShell dans le dossier contenant `setup.ps1` :

```powershell
.\setup.ps1
.\run_ui.ps1
```

Ouvrir ensuite `http://127.0.0.1:8000`. Si ce port est occupé, définir un autre port avant le lancement :

```powershell
$env:CONFIG_STUDIO_PORT = '8001'
.\run_ui.ps1
```

Dans ce cas, ouvrir `http://127.0.0.1:8001`. Le [guide complet](../GUIDE_DEMONSTRATION_WEB.md) fournit les commandes de clonage Git, les alternatives d’installation et les contrôles CLI/API. L’ouverture directe de `web/index.html` depuis le disque ne remplace pas le serveur.

### Réaliser une démonstration

1. Vérifier que le serveur est disponible dans l’interface.
2. Cliquer sur **Charger un exemple**, importer une configuration de `resources/` ou coller un texte de configuration.
3. Choisir la famille Cisco IOS ou Cisco IOS-XE correspondant au fichier.
4. Examiner et, si nécessaire, modifier le texte source.
5. Cliquer sur **Normaliser la configuration** ou utiliser **Ctrl + Entrée**.
6. Consulter le JSON en vue **Code**, puis ouvrir les sections dans **Arborescence**.
7. Expliquer une valeur reconnue et une valeur `null`, en les reliant à la configuration.
8. Utiliser **Copier** ou **Télécharger** pour récupérer `normalized.json`.
9. Arrêter le serveur avec **Ctrl+C** dans PowerShell après la démonstration.

Pour illustrer le routage avancé, importer `resources/eigrp/named_dualstack.cfg` et explorer les processus, familles d’adresses et topologies dans `routing.eigrp`. Présenter uniquement les paramètres effectivement reconnus.

## 9. Communication frontend/backend et limites d’utilisation

| Route HTTP | Rôle |
|---|---|
| `GET /` | Fournit l’interface graphique. |
| `GET /api/health` | Indique la disponibilité du service et le contrat utilisé ; ne réalise pas une normalisation complète. |
| `POST /api/normalize` | Reçoit la configuration et sa famille, puis retourne le document normalisé et la durée du traitement. |

Le backend contrôle l’entrée, appelle le même pipeline que le CLI dans un processus isolé et revalide le résultat avec le contrat. Le traitement Web utilise les flux mémoire sans créer de fichiers temporaires de configuration ou de résultat. Le téléchargement est déclenché par l’utilisateur dans son navigateur.

Limites à indiquer :

- Texte UTF-8 non vide, jusqu’à **2 Mio** de configuration.
- Délai maximal de traitement de **120 secondes**.
- Une normalisation à la fois ; une demande concurrente peut recevoir le statut HTTP 429.
- Écoute sur `127.0.0.1` : l’interface livrée est destinée à l’utilisation locale.
- Les erreurs internes ne sont pas renvoyées comme diagnostics détaillés contenant la configuration.
- La présence d’un JSON valide ne constitue ni une preuve de couverture exhaustive ni une preuve de conformité de l’équipement.

Le masquage porte sur les formes de secrets reconnues. Il convient de présenter cette protection selon sa couverture réelle, sans affirmer que toute syntaxe possible d’un constructeur est traitée.

## 10. Illustrations conseillées pour le rapport

Prévoir des captures réalisées avec des configurations synthétiques ou anonymisées :

1. **Vue générale de Config Studio** : les deux panneaux et l’indicateur du serveur.
2. **Configuration importée** : fichier choisi, famille et commandes visibles sans données sensibles.
3. **Résultat en vue Code** : quelques champs et leurs valeurs `null` ou `false` expliquées.
4. **Résultat en Arborescence** : développement d’une interface ou d’un processus de routage.
5. **Export** : bouton de téléchargement et ouverture du document produit.

Associer à chaque figure une légende qui explique l’action et le résultat observé. Pour la partie technique, reprendre le schéma de circulation des données et le tableau des composants plutôt qu’une capture de toute l’arborescence de développement.

## 11. Plan proposé pour la rédaction

1. Contexte, problème traité et objectifs.
2. Architecture générale et choix techniques.
3. Organisation des fichiers et responsabilités des composants.
4. Parsing TTP, gestion des contextes et captures intermédiaires.
5. Mappings métier et construction de `RouterContractV1`.
6. Validation, sérialisation et conventions de valeurs.
7. Présentation de l’interface et parcours utilisateur illustré.
8. Exemple de démonstration avec confrontation source/résultat.
9. Limites actuelles et perspectives distinctes des fonctionnalités déjà réalisées.

Pour les résultats expérimentaux, utiliser les rapports et essais réellement exécutés. Distinguer une erreur technique, une commande non prise en charge, une information légitimement indéterminée et une fonction volontairement hors périmètre.
