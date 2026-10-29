# Domaines métier — répartition des mappings

[Moteur](../README.md) · [Routage](routing/README.md) · [Contrat](../../schemas/README.md)

## Principe

Un domaine reçoit des captures validées du parser et alimente directement les
sous-modèles `RouterContractV1` correspondants. Il interprète une commande dans
son contexte, convertit ses paramètres et conserve ses références.

La répartition du code ne reproduit pas nécessairement les sections du JSON.
Un module peut alimenter plusieurs sections canoniques cohérentes. Inversement,
plusieurs modules spécialisés peuvent participer à une même section.

## Aiguillage

`__init__.py` expose `handler_for` : une règle possède un handler propriétaire.
L'aiguillage tient compte de sa famille et de certains identifiants particuliers.
Les déclarations reconnues sont recensées dans `DECLARATIONS`.

Les fonctions utilisées selon les besoins sont :

- `declare` : établir une identité structurante ;
- `handle` : appliquer les captures ordinaires ;
- `resolve` : effectuer les traitements différés.

Tous les modules n'ont pas besoin d'exposer ces trois fonctions. Les helpers AAA
et d'authentification sont appelés par leurs domaines propriétaires.

## Modules et responsabilités

| Module | Responsabilité principale | Destination canonique |
|---|---|---|
| `interfaces.py` | Interfaces physiques, sous-interfaces, adresses, négations, VRF, agrégations et options L3 reconnues | `interfaces`, `interface_aggregations` et bindings associés |
| `acl.py` | Identité/famille, ordre, actions, adresses, ports, log et log-input | `security.acls` |
| `policies.py` | Statements, conditions et actions de route-maps ; qualification des objets partiels | `routing_policies.route_maps` et protections transverses |
| `services.py` | Identité, lignes administratives, services et supervision | Principalement `system`, avec certains objets de politiques |
| `aaa_administration.py` | Method-lists, groupes/serveurs, métadonnées de clés et paramètres SSH | `system.aaa`, `system.management` |
| `nat.py` | NAT statique reconnu | `nat` |
| `vpn.py` | Paramètres de tunnels et références source/destination reconnues | `vpn` |
| `qos.py` | Class-maps, policy-maps et affectations | `qos` |
| `pki.py` | Trustpoints et références de certificats reconnues | `pki` |
| `cisco_features.py` | IS-IS, MPLS, multicast, archive, Call Home et paramètres complémentaires | Sections métier correspondantes et `extensions.cisco` |
| `routing/` | BGP, OSPF, RIP, routes statiques, VRF, prefix-lists et authentification | `routing`, `network_instances`, `routing_policies` |

Ce tableau décrit l'organisation des mappings, pas une promesse d'exhaustivité
des commandes possibles dans chaque technologie.

## Exemple de transformation

```text
interface GigabitEthernet0/0
 shutdown
```

Le parser reconnaît `if_header`, puis `if_shutdown` avec `enabled=False`.
Le domaine interfaces retrouve l'objet concerné et alimente `admin_enabled=False`.
Le moteur enregistre la liaison avec la capture et conserve cette négation dans
le résultat. Aucun état de liaison réellement observé sur l'équipement n'est déduit.

## Ordre, références et portées

L'ordre des méthodes AAA, entrées ACL et statements de politiques est conservé.
Les paramètres globaux, par processus, par famille et par VRF ne doivent pas être
fusionnés. Une référence connue est conservée comme telle ; elle ne justifie pas
la création d'une cible fictive.

Les métadonnées de credentials ne contiennent ni mot de passe ni clé brute. Une
référence de key chain ne prouve pas toujours le mécanisme d'authentification utilisé.

## Protection des objets partiels

`policies.blocked_objects` examine les objets ordonnés dont les sources ne sont pas
entièrement qualifiées. Il peut bloquer la publication d'ACL, route-maps, prefix-lists,
class-maps ou policy-maps concernées, puis certaines dépendances connues.

Cette protection évite de présenter une politique partielle comme une politique
complète. Elle ne résout pas arbitrairement toutes les références absentes.

## Faire évoluer un mapping

Vérifier conjointement la capture, son contexte, les champs réellement validés et
la structure du contrat. Utiliser les opérations communes du moteur pour affecter
et lier les champs. Une nouvelle liste de travail ne doit pas devenir implicitement
une preuve d'absence. Les validations et tests de développement sont à réaliser
dans le dépôt de travail, distinct de cette copie de distribution.

## Mapping EIGRP

`routing/eigrp.py` est le propriétaire des règles `eigrp_*`. Les objets sont écrits
dans `routing.eigrp`, `routing.eigrp_interfaces` et les paramètres communs
d'interface bandwidth/delay. Le module `policies.py` traite la nouvelle action
vectorielle `eigrp_metric` sans remplacer l'action scalaire `metric`.
[Portées, commandes et limites](../../docs/eigrp/README.md).
