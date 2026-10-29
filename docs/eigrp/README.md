# EIGRP Cisco IOS/IOS-XE — reconnaissance et contrat canonique

## Recherche et sources

L'implémentation s'appuie sur les références officielles Cisco IOS/IOS-XE ci-dessous,
consultées le 29 octobre 2026. Les résultats concernant IOS XR, NX-OS ou ASA n'ont
pas été transposés dans les règles IOS. Une syntaxe documentée peut dépendre de
l'image, de la version ou de la plateforme ; cette liste ne qualifie pas tous les équipements.

| Référence | Utilisation |
|---|---|
| [Command Reference A–H](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/command/ire-cr-book/ire-a1.html) | AF, af-interface, authentification, AS, métriques, distances, stub, timers |
| [Command Reference I–R](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/command/ire-cr-book/ire-i1.html) | Commandes d'interfaces IPv4/IPv6, réseaux, voisins, passivité et processus |
| [Command Reference S–V](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/command/ire-cr-book/ire-s1.html) | Topologies, résumés, variance, shutdown et métrique de route-map |
| [Guide EIGRP IOS-XE](https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m_ire-enhanced-igrp.pdf) | Organisation des configurations classiques et nommées |
| [Fonctions indépendantes des protocoles](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-routing/b-ip-routing/m_iri-ip-prot-indep-0.html) | Redistribution et métriques composites |
| [Référence distribute-list](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_pi/command/iri-cr-book/iri-cr-a1.html) | Références ACL, prefix-lists, route-maps et directions |
| [Filtrage EIGRP par route-map](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-routing/b-ip-routing/m_eigrp-route-map.html) | Placement du filtrage dans les topologies nommées et cas IPv6 |
| [Référence IPv6](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipv6/command/ipv6-cr-book/ipv6-i5.html) | Résumés IPv6 classiques et enveloppe de maximum-paths |
| [Bandwidth d'interface](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/interface/command/ir-cr-book/ir-a1.html) | Paramètre de bande passante configurée, distinct du débit physique |
| [Delay d'interface](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/interface/command/ir-cr-book/ir-d1.html) | Délai configuré exprimé en dizaines de microsecondes |

## Couverture effectivement ajoutée

Le lot comprend **129 règles supplémentaires** : 128 règles EIGRP et une règle
de métrique composite pour les route-maps. La [matrice des règles](matrice_commandes.csv)
énumère les identifiants, templates, patterns et destinations. Les portées exactes
sont vérifiées dans `parser/eigrp_context.py` ; la matrice n'est pas une liste de
commandes acceptables dans n'importe quel mode.

Notation : les paramètres entre `<...>` sont variables ; les éléments entre
crochets sont facultatifs. Les variantes effectivement reconnues sont dans les templates.

| Ensemble | Formes prises en charge |
|---|---|
| Processus | `router eigrp <AS>` classique IPv4, `router eigrp <nom>` nommé, `ipv6 router eigrp <AS>` classique IPv6 |
| AF | IPv4/IPv6, SAFI unicast ou multicast lorsqu'autorisé, VRF et AS explicite ; AF IPv4 classique et `autonomous-system` local |
| Blocs nommés | `af-interface default`, `af-interface <interface>`, `topology base`, `topology <nom> tid <id>` et sorties de contexte |
| Réseaux | `network <IPv4> [wildcard]`, sans fabrication de masque lorsqu'il est absent |
| Identité et passivité | `eigrp router-id`, passive-interface default/interfaces et exceptions ; passivité locale en af-interface |
| État configuré | shutdown/no shutdown dans les portées reconnues ; activation IPv6 explicite par interface |
| Métriques de routage | variance, maximum-paths, metric maximum-hops, metric weights K1–K5 et K6 nommé, default-metric et timers active-time |
| Distances et stub | distance eigrp interne/externe ; stub, types annoncés, receive-only exclusif et référence leak-map |
| Redistribution | connected/static/BGP/OSPF/IS-IS/EIGRP/RIP selon les opérandes reconnus, identifiant de source, métrique à cinq composantes et route-map |
| Filtrage | distribute-list ACL, prefix/prefix-list ou route-map selon la famille et le mode ; directions et références d'interface autorisées |
| Voisins | Voisins statiques explicitement configurés avec leur interface, sans voisins opérationnels déduits |
| Interfaces | Hello, hold, bandwidth-percent, split-horizon, next-hop-self ; paramètres communs bandwidth et delay |
| Authentification | MD5 et références de key chains classiques IPv4/IPv6 et nommées ; HMAC-SHA-256 nommé avec format 0/7 et présence de secret uniquement |
| Résumés | IPv4 classiques/nommés avec distance et leak-map reconnus ; IPv6 classiques par interface |
| Politiques | `set metric <bandwidth> <delay> <reliability> <load> <mtu>` distinct du set metric scalaire existant |

Les formes négatives retenues conservent leur sémantique : une désactivation
explicite d'un booléen produit false ; une suppression de réglage scalaire produit
une valeur indéterminée accompagnée d'un marqueur de suppression. Les resets de
timers ne publient pas de valeur Cisco supposée.

## Chemin d'exécution

```text
Configuration → inventaire (famille eigrp ou interfaces)
              → templates EIGRP + vérification des contextes/opérandes
              → normalizer.domains.routing.eigrp
              → RouterContractV1 → validation → sérialisation officielle
```

Fichiers principaux :

- `templates/cisco_ios/routing/eigrp.ttp` : processus, AF, topologies et af-interface ;
- `templates/cisco_ios/interfaces/eigrp.ttp` : commandes d'interfaces classiques ;
- `templates/cisco_ios/policies.ttp` : ajout de la métrique vectorielle ;
- `parser/eigrp_context.py` et `parser/eigrp_commands.py` : portée et opérandes ;
- `normalizer/domains/routing/eigrp.py` : mapping direct ;
- `schemas/router_contract_v1.py` : sous-modèles et contraintes ;
- `resources/eigrp/` : configurations synthétiques de démonstration distribuées.

Aucun nouveau moteur, adaptateur historique ou chemin de sérialisation n'est ajouté.
Le Web affiche le même contrat par son appel existant au CLI.

## Organisation canonique et décisions

`routing.eigrp` contient les processus. Un processus classique possède son AS et
son AFI. Un processus nommé conserve son nom ; ses AS et familles sont portés par
`address_families`. Les familles conservent la VRF et le SAFI explicitement fourni.

Les réglages de topologie restent dans `topologies`, ceux des af-interface dans
`interface_settings`. L'entrée `interface: default` représente le bloc de défaut,
pas une interface fictive. Les exceptions restent distinctes ; leur résultat hérité
effectif n'est pas calculé.

`routing.eigrp_interfaces` conserve les réglages classiques identifiés par interface,
AFI, AS et VRF lorsqu'elle est connue. Ils peuvent exister sans déclaration de
processus : le normaliseur ne crée pas de processus ou de VRF pour résoudre une référence.

Les interfaces possèdent `bandwidth_kbps`, `delay_tens_of_microseconds` et les marqueurs
de suppression correspondants. Ils expriment des paramètres de configuration,
pas une mesure de capacité ou de latence.

Les métriques composites sont des objets typés avec unités explicites. Les route-maps
utilisent l'action `eigrp_metric` ; les métriques scalaires existantes conservent
leur action `metric`. Ces concepts ne sont pas fusionnés.

Les réseaux préservent adresse et wildcard natifs. L'absence de wildcard n'est pas
remplacée par un masque présumé. Les voisins, politiques et key chains restent des
références ou configurations explicites, sans calcul de tables de routage.

Le contrat reste `RouterContractV1` / `1.0.0`, comme les extensions précédentes.
Le JSON Schema a été régénéré. Les consommateurs validant contre un ancien schéma
fermé doivent adopter le nouveau schéma : les nouvelles clés peuvent être présentes
à null même sans commande EIGRP. Il n'existe pas d'export d'ancien format parallèle.

## Confidentialité et valeurs

Les mots de passe HMAC-SHA-256 sont masqués avant inventaire, captures et templates
amont, y compris lorsque le contexte ou le format n'est pas reconnu. Seules la
présence et l'étiquette de format sont conservées, sans secret ni dérivé de secret.
Une key chain seule ne permet pas de conclure au mode réellement configuré.

Les suppressions locales d'authentification restent distinctes de l'héritage
éventuel. Les paramètres absents restent null ; les nouvelles collections ne
deviennent pas [] par défaut. Les listes ordonnées de politiques et les protections
contre les publications partielles restent actives.

Les limites numériques sont structurelles et issues des commandes documentées.
Les capacités maximum-paths varient suivant les plateformes : une borne de modèle
ne constitue pas une qualification de toutes les valeurs sur tous les équipements.
Les références Cisco consultées indiquent aussi des défauts parfois divergents
pour les résumés IPv6 ; aucun de ces défauts n'est injecté dans le JSON.

## Limites volontairement explicites

- Pas d'assertion de couverture de toutes les commandes EIGRP ou de toutes les images Cisco.
- Service-family/sf-interface, FRR, BFD, NSF avancé, offset-list, gateway filters,
  summary-metric et variantes complexes de redistribution restent hors de ce lot.
- Les options non reconnues d'une redistribution, d'un stub ou d'un résumé sont
  rejetées entièrement plutôt que publiées en perdant le suffixe.
- Les résumés IPv6 en mode nommé ne sont pas activés : les références retenues
  ne donnent pas une syntaxe IPv6 univoque pour ce sous-mode.
- Les suppressions complètes de processus/AF et les nombreuses variantes négatives
  non retenues ne sont pas interprétées comme des commandes de suppression du graphe.
- Les syntaxes de noms virtuels entièrement numériques sont interprétées comme
  des AS classiques ; l'AS-dot BGP n'est pas un AS EIGRP valide.
- Aucune résolution de voisinage opérationnel, de métrique effective ou de conformité.

## Vérification de la distribution

Cette copie inclut l'extension EIGRP du dépôt original, où 74 tests ciblés ont
validé le contrat et les mappings, dont 40 cas EIGRP. Les tests du dépôt de travail
ne sont pas distribués ici. Le guide de démonstration explique les contrôles par
CLI et API disponibles sans pytest.

```powershell
.\.venv\Scripts\python.exe cli.py resources/eigrp/named_dualstack.cfg --output outputs/eigrp-demo --os-family iosxe
```

Les trois exemples sont décrits dans [resources/eigrp](../../resources/eigrp/README.md).
Le [guide Web complet](../../GUIDE_DEMONSTRATION_WEB.md) explique le clonage,
l'installation et les essais de bout en bout.
