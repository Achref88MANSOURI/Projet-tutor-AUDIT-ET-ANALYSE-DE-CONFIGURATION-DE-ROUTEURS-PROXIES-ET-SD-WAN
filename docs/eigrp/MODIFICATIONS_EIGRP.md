# Bilan des modifications pour l’intégration d’EIGRP

## 1. Objectif et périmètre

L’intervention a ajouté la reconnaissance et la normalisation de configurations EIGRP Cisco IOS/IOS-XE au système existant. Elle couvre le parsing TTP, les contrôles de contexte et de valeurs, les mappings métier, le contrat Pydantic, le JSON Schema, les tests et la documentation.

Le pipeline reste unique :

```text
Configuration Cisco
    → préparation et masquage des secrets reconnus
    → inventaire des blocs
    → parsing TTP et validation des captures
    → mapping EIGRP
    → RouterContractV1
    → validation et sérialisation
    → normalized.json
```

L’intégration utilise directement le contrat canonique. Aucun adaptateur historique, moteur supplémentaire ou export parallèle n’a été créé.

Ce bilan distingue l’implémentation initiale dans le dépôt de travail et la synchronisation ultérieure du dossier « à exporter ». Les résultats de tests cités proviennent des contrôles enregistrés lors de ces interventions ; ils ne correspondent pas à une nouvelle exécution pour la rédaction de ce document.

## 2. Recherche des syntaxes Cisco

Les références officielles Cisco ont servi à identifier les modes de configuration, les paramètres, les unités et les portées autorisées. La recherche a distingué les syntaxes IOS/IOS-XE des autres systèmes Cisco et les formes classiques des formes nommées.

Les références et la couverture détaillée sont conservées dans le [guide EIGRP](README.md). La [matrice des commandes](matrice_commandes.csv) associe chaque règle à son template, son motif et sa destination canonique.

Les principales références comprennent les command references EIGRP A–H, I–R et S–V, le guide EIGRP IOS-XE, les commandes IPv6, les distribute-lists et les paramètres d’interface bandwidth/delay. La disponibilité réelle d’une syntaxe peut varier selon l’image et la plateforme.

## 3. Templates TTP : règles ajoutées

Le lot comprend **129 règles supplémentaires** : **128 règles EIGRP** et **une règle de métrique composite pour les route-maps**.

| Fichier | Modification et rôle |
|---|---|
| `templates/cisco_ios/routing/eigrp.ttp` | Nouveau template : déclarations de processus, address-families, af-interface, topologies et paramètres de routage. |
| `templates/cisco_ios/interfaces/eigrp.ttp` | Nouveau template : réglages EIGRP classiques IPv4/IPv6 sous les interfaces et paramètres bandwidth/delay associés. |
| `templates/cisco_ios/policies.ttp` | Ajout du `set metric` à cinq composantes, distinct de la métrique scalaire existante. |
| `templates/rule_metadata.json` | Ajout des métadonnées nécessaires au traitement des nouvelles règles. |

### Formes de configuration reconnues

| Domaine | Couverture ajoutée |
|---|---|
| Processus classique IPv4 | `router eigrp <AS>`. |
| Processus classique IPv6 | `ipv6 router eigrp <AS>`. |
| Processus nommé | `router eigrp <nom>`, avec familles d’adresses et AS explicites. |
| Familles d’adresses | IPv4/IPv6, VRF et SAFI dans les combinaisons reconnues et autorisées. |
| Sous-contextes nommés | `af-interface default`, af-interface spécifique, `topology base` et topologies nommées avec identifiant. |
| Networks | Adresse IPv4 et wildcard lorsqu’elle est fournie. |
| Identité et passivité | Router-ID, passive-interface default, interfaces passives et exceptions, réglages locaux en af-interface. |
| Activation | Shutdown/no shutdown dans les portées reconnues et activation IPv6 explicite par interface. |
| Paramètres de routage | Variance, maximum-paths, maximum-hops, metric weights, default-metric, active-time et distances interne/externe. |
| Stub | Options annoncées, receive-only et référence leak-map selon les formes reconnues. |
| Redistribution | Protocole source, identifiant éventuel, métrique composite et référence de route-map. |
| Filtres | Distribute-lists avec ACL, prefix-list ou route-map, direction et interface selon le mode. |
| Voisins | Voisins statiques et référence d’interface explicitement configurés. |
| Interfaces | Hello, hold, bandwidth-percent, split-horizon, next-hop-self, bandwidth et delay. |
| Résumés | Résumés IPv4 classiques et nommés ; résumés IPv6 classiques par interface. |
| Authentification | MD5 et références de key chains ; HMAC-SHA-256 en mode nommé avec formats reconnus 0/7 et présence du secret uniquement. |
| Politiques | Métrique vectorielle `set metric <bandwidth> <delay> <reliability> <load> <mtu>`. |

Ce tableau décrit les catégories implémentées. Les combinaisons et variantes exactes restent celles des templates, de leurs validateurs et de la matrice ; elles ne sont pas interchangeables entre tous les modes.

## 4. Parser : identification et validation des contextes

| Fichier | Modification |
|---|---|
| `parser/eigrp_context.py` | Nouveau contrôle des portées : processus, AF, topologie, af-interface et interface classique. |
| `parser/eigrp_commands.py` | Nouveau contrôle des opérandes et des formes complètes : métriques, redistributions, stub, résumés et autres paramètres. |
| `parser/inventory.py` | Identification de la famille EIGRP pour les blocs `router eigrp` et `ipv6 router eigrp`. |
| `parser/run_ttp.py` | Intégration de la famille et contrôle des contextes avant admission des captures EIGRP. |
| `parser/validation.py` | Appel des validations EIGRP pour qualifier les valeurs extraites. |
| `parser/routing_secrets.py` | Extension du masquage aux credentials HMAC-SHA-256 avant inventaire et parsing. |

Ces contrôles empêchent notamment une commande de topologie d’être appliquée au mauvais niveau ou un bloc af-interface invalide d’être publié comme une configuration reconnue.

Les options non reconnues de certaines commandes complexes provoquent leur rejet complet. Le système évite ainsi de retenir seulement le début d’une redistribution, d’un stub ou d’un résumé en perdant un suffixe significatif.

Un identifiant de processus entièrement numérique est interprété comme un AS classique. Un AS invalide ne doit pas être réinterprété comme un nom de processus pour contourner les contraintes.

## 5. Normalisation : mapping direct vers le contrat

### Module dédié

Le nouveau fichier `normalizer/domains/routing/eigrp.py` réalise le mapping des captures vers les modèles EIGRP. Il déclare les processus, retrouve les contextes et conserve les réglages dans leur portée d’origine.

Le fichier `normalizer/domains/__init__.py` a été adapté pour enregistrer la famille EIGRP, ses déclarations et l’aiguillage des règles `eigrp_*` vers ce propriétaire unique.

### Organisation des données produites

```text
RouterContractV1
├── interfaces
│   ├── bandwidth_kbps
│   ├── delay_tens_of_microseconds
│   └── removed_metric_settings
├── routing
│   ├── eigrp
│   │   └── processus classiques ou nommés
│   │       ├── paramètres du processus
│   │       ├── address_families
│   │       ├── topologies
│   │       └── interface_settings, selon la portée
│   └── eigrp_interfaces
│       └── paramètres classiques par interface, AFI et AS
└── routing_policies
    └── route_maps
        └── action eigrp_metric
```

Un processus classique conserve son AS et sa famille IP. Un processus nommé conserve son nom ; les familles portent leurs AS et VRF explicites. Les paramètres de topologie, d’AF et d’interface ne sont pas fusionnés.

L’entrée `interface: default` représente un bloc af-interface de défaut. Elle ne crée pas une interface réseau fictive. Le système conserve les réglages locaux et leurs exceptions sans calculer une configuration héritée effective.

Les réglages classiques d’interface peuvent être représentés sans déclaration de processus correspondante. Aucune VRF ou aucun processus fictif n’est créé pour résoudre une référence.

### Politiques de routage

`normalizer/domains/policies.py` traite la nouvelle action typée `eigrp_metric`. L’action scalaire `metric` reste distincte. Les protections contre la publication de politiques partiellement reconnues sont conservées.

## 6. Contrat Pydantic et JSON Schema

Le fichier `schemas/router_contract_v1.py` a été étendu avec les modèles suivants :

| Ensemble | Modèles |
|---|---|
| Métriques | `EIGRPMetric`, `EIGRPMetricPolicyAction`, `EIGRPMetricWeights`. |
| Réseaux et passivité | `EIGRPNetworkStatement`, `EIGRPPassiveInterface`. |
| Options de protocole | `EIGRPStub`, `EIGRPAuthentication`, `EIGRPSummary`. |
| Interfaces | `EIGRPInterfaceSettings`, `EIGRPClassicInterface`. |
| Voisins et échanges de routes | `EIGRPNeighbor`, `EIGRPFilter`, `EIGRPRedistribution`. |
| Contextes et processus | `EIGRPTopologySettings`, `EIGRPTopology`, `EIGRPInstanceSettings`, `EIGRPAddressFamily`, `EIGRPProcess`. |

Les sections `routing.eigrp` et `routing.eigrp_interfaces` ont été ajoutées. Les interfaces ont reçu les paramètres de métrique configurée bandwidth/delay et leurs marqueurs de suppression. Le modèle des actions de politique accepte la métrique EIGRP structurée.

Les modèles contrôlent notamment les plages numériques, les familles d’adresses, les paramètres liés et l’unicité des identités de processus et de contextes. Les paramètres de bande passante et de délai indiquent des valeurs configurées, avec unités explicites ; ils ne représentent pas des mesures physiques.

Le fichier `schemas/router_contract_v1.schema.json` a été régénéré à partir des modèles. Le nom du contrat reste `RouterContractV1`, avec la version `1.0.0`. Un consommateur utilisant un ancien JSON Schema fermé doit adopter le schéma actualisé, car les nouvelles propriétés peuvent apparaître à `null`.

## 7. Valeurs, suppressions et confidentialité

Les choix de représentation sont les suivants :

- Une absence de commande reconnue reste indéterminée : `null`.
- Une négation explicite d’un booléen conserve `false` lorsque sa sémantique l’établit.
- La suppression d’un réglage local est distinguée d’une désactivation, à l’aide des marqueurs prévus.
- Une remise à zéro de timer ne conduit pas à inventer une valeur par défaut Cisco.
- Une wildcard absente n’est pas remplacée par un masque présumé.
- Une collection n’est pas publiée à `[]` uniquement parce qu’aucune capture n’a été obtenue.
- Une référence de key chain ne suffit pas à déduire le mécanisme d’authentification.

Le masquage HMAC-SHA-256 intervient avant les captures TTP, y compris pour les syntaxes ou contextes non reconnus par le mapping. Seules les métadonnées utiles, telles que la présence et l’étiquette de format, sont conservées. Aucun secret ou dérivé de secret n’est ajouté au contrat.

## 8. Tests ajoutés et adaptations des contrôles existants

### Nouveaux fichiers

- `tests/test_eigrp.py` : tests ciblés de bout en bout et validations des structures.
- `tests/fixtures/eigrp/classic_ipv4.cfg` : processus classique IPv4, VRF et réglages associés.
- `tests/fixtures/eigrp/classic_ipv6.cfg` : processus classique IPv6 et activation par interface.
- `tests/fixtures/eigrp/named_dualstack.cfg` : mode nommé, familles IPv4/IPv6, VRF et topologies.

### Vérifications couvertes

Les tests portent sur les contextes classiques et nommés, la séparation AF/VRF/topologie, les interfaces, réseaux et wildcards, les resets, les négations, les limites numériques, les références non résolues et le rejet des commandes partielles ou placées dans un mauvais contexte.

Ils contrôlent aussi la coexistence des métriques scalaire et vectorielle, la confidentialité avant les templates personnalisés et amont, l’export CLI, la validation JSON Schema et le chemin Web utilisant le même contrat.

`tests/test_ttp_loading.py` a été adapté à l’inventaire actualisé des templates. `tests/fixtures/normalization_reference.json` a été complété pour les nouveaux champs optionnels et pour les valeurs bandwidth/delay explicitement présentes dans les sources. Les assertions métier existantes ont été conservées.

### Résultats enregistrés lors de l’implémentation

| Vérification | Résultat enregistré |
|---|---|
| Tests EIGRP | 40 cas réussis. |
| Tests existants sélectionnés | 34 cas réussis. |
| Total ciblé | **74 réussites, 0 échec final**. |
| HTTP local réel | Processus nommé, trois AF, variance et confidentialité vérifiés. |
| Autres contrôles | Syntaxe Python, cohérence du JSON Schema, inventaire des templates et contrôle ciblé des différences satisfaits. |

La suite globale et les 105 configurations du catalogue n’ont pas été exécutées pour cet ajout. Le relevé de cette intervention est conservé dans `docs/eigrp/validation.json`.

Les corrections apportées pendant les essais comprennent le remplacement d’un nom de capture réservé par TTP, la séparation de la métrique composite, le rejet des contextes invalides et l’actualisation de la référence historique pour les nouveaux champs.

## 9. Documentation et copie de distribution

Dans le dépôt original, les documents suivants ont été créés ou actualisés :

- `docs/eigrp/README.md` : sources, couverture, décisions et limites.
- `docs/eigrp/matrice_commandes.csv` : traçabilité des règles et destinations.
- `docs/eigrp/validation.json` : résultats enregistrés du lot initial.
- `README.md`, `schemas/README.md`, `templates/README.md` et `docs/SORTIES_METIER.md` : présentation de la nouvelle couverture.

Après l’implémentation initiale, le dossier « à exporter » a été synchronisé séparément : runtime EIGRP, modèles et schéma actualisés, templates, métadonnées et interface Web existante. Les trois configurations EIGRP ont été ajoutées sous `resources/eigrp/`, après masquage des credentials synthétiques. La distribution contient ainsi **23 configurations de démonstration**, au lieu de 20.

Les guides de la distribution ont été actualisés, notamment `GUIDE_DEMONSTRATION_WEB.md`, les README du parser, des templates, du normaliseur, des domaines, du routage, des schémas, du Web et des ressources. Le fichier `.gitignore` de cette copie autorise l’inclusion des nouveaux exemples EIGRP.

La synchronisation a été vérifiée dans une copie isolée : installation hors ligne, cohérence des dépendances, trois exemples via CLI et backend Web, validation Pydantic/JSON Schema et contrôle HTTP réel. Les tests de développement ne sont pas inclus dans la distribution.

Les mentions « export inchangé » des traces du lot initial décrivent uniquement cette première intervention ; elles précèdent la synchronisation demandée ultérieurement.

## 10. Architecture conservée et limites restantes

L’ajout EIGRP s’insère dans les points d’extension existants. Le moteur central et la sérialisation n’ont pas nécessité de nouveau mécanisme dédié. Le Web bénéficie de l’ajout par son appel existant au CLI ; aucune règle métier EIGRP n’est implémentée dans le frontend.

Limites documentées :

- Pas de garantie de couverture de toutes les commandes et versions IOS/IOS-XE.
- Service-family/sf-interface, FRR, BFD, NSF avancé, offset-list, gateway filters, summary-metric et variantes complexes de redistribution hors de ce lot.
- Résumés IPv6 en mode nommé non activés, faute de syntaxe suffisamment univoque dans les références retenues.
- Suppressions complètes de processus/AF et variantes négatives non retenues non interprétées comme une suppression du graphe d’objets.
- Pas de calcul de voisinage opérationnel, de routes effectives, de métriques effectives ou de résultat d’audit.

L’implémentation conserve les informations explicitement reconnues et laisse les autres indéterminées, sans introduire de paramètres Cisco supposés.

## 11. Formulation réutilisable dans le rapport

> L’intégration d’EIGRP a étendu le pipeline de normalisation existant à travers des règles TTP, des contrôles de contexte et un mapping métier dédié. Le contrat RouterContractV1 représente désormais les processus classiques et nommés, leurs familles d’adresses, leurs contextes VRF, leurs topologies et les paramètres d’interface reconnus. Les métriques composites sont modélisées séparément des métriques scalaires, et les métadonnées d’authentification sont conservées sans exposer les secrets. L’implémentation a été validée par 74 tests ciblés, dont 40 cas EIGRP, ainsi que par un contrôle HTTP réel. La couverture reste limitée aux syntaxes documentées et effectivement implémentées.
