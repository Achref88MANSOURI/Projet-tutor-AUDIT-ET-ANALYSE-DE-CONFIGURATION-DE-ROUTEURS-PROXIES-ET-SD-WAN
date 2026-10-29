# Templates TTP — règles de reconnaissance Cisco

[Guide général](../README.md) · [Parser](../parser/README.md) · [Mappings métier](../normalizer/domains/README.md)

## Responsabilité

Les templates décrivent les syntaxes CLI reconnues et nomment les paramètres à
extraire. Ils constituent la partie propre au langage de configuration Cisco.
L'interprétation métier et la construction des objets Pydantic appartiennent au
normaliseur.

```text
Commande CLI → règle TTP → paramètres nommés → domaine métier → champ canonique
```

## Organisation

| Fichier ou dossier | Commandes concernées |
|---|---|
| `cisco_ios/interfaces.ttp` | Interfaces, adressage, état administratif, encapsulations et options L3 |
| `cisco_ios/bgp.ttp` | Processus, voisins, peer-groups, AF et options BGP |
| `cisco_ios/ospf.ttp` | Processus OSPF, aires, networks et paramètres reconnus |
| `cisco_ios/vrf.ttp` | Déclarations et propriétés des VRF |
| `cisco_ios/routes.ttp` | Routes statiques IPv4/IPv6 |
| `cisco_ios/acl_standard.ttp`, `acl_extended.ttp` | ACL, opérandes, ports et options |
| `cisco_ios/policies.ttp`, `prefix.ttp` | Route-maps et prefix-lists |
| `cisco_ios/routing/` | RIP et key chains |
| `cisco_ios/services/` | AAA, administration, DNS, NTP, Syslog, SNMP, NetFlow et services conservés |
| `cisco_ios/advanced/` | IS-IS, MPLS, multicast, QoS, PKI et règles historiques |
| `upstream/` | Quatre snapshots des templates amont |
| `rule_metadata.json` | Portées de contexte et valeurs fermées autorisées |

La famille utilisée à l'exécution est attribuée par le loader et l'inventaire.
Elle n'est pas nécessairement identique au nom du dossier : RIP et les key chains
sont actuellement dispatchés dans la famille de parsing `services`.

## Structure d'une règle du projet

Les groupes du projet sont des tables plates identifiées par un nom unique. Par
exemple, le principe d'une règle de description d'interface est :

```xml
<group name="if_description*" method="table">
{{ source_line | DIGIT | to_int }} description {{ value | ORPHRASE }}
</group>
```

L'inventaire ajoute le numéro de ligne devant la commande avant son passage à TTP.
`DIGIT` reconnaît ce numéro, `to_int` le convertit et `ORPHRASE` capture une phrase.
Des constantes peuvent aussi être établies par les fonctions TTP du groupe : par
exemple un booléen pour une négation explicite.

Cette organisation ne confie pas à un grand template imbriqué la reconstruction
de toute la configuration : les relations entre lignes sont conservées par
l'inventaire, puis utilisées par les contrôles de contexte et les mappings.

## Métadonnées et contrôles complémentaires

Les entrées de `rule_metadata.json` peuvent contenir :

- `scope: "global"` : commande à la racine ;
- `scope: "root:..."` : commande sous un type de bloc racine ;
- `choices` : valeurs autorisées pour certains paramètres.

Le parser complète ces contraintes par la vérification de la ligne entière et
des contrôles spécifiques d'authentification, AAA ou interfaces. Ces contrôles
empêchent une capture partielle ou une mauvaise association de contexte.

## Templates amont figés

Les quatre fichiers présents dans `upstream/` concernent :

1. les interfaces ;
2. les VRF ;
3. les ASN BGP ;
4. le NAT statique reconnu.

Le pipeline charge le contenu fourni par `ttp_templates`, puis vérifie son égalité
avec le snapshot local. Les fins de ligne sont lues comme du texte. Un écart n'est
pas corrigé en adoptant automatiquement une autre version.

Les résultats amont peuvent compléter certaines lectures, notamment pour les
interfaces et VRF. Leurs défauts ne sont pas automatiquement des faits configurés.
La licence correspondante est conservée dans [licenses](../licenses/ttp_templates-MIT.txt).

## Limites et maintien

Une règle reconnue peut rester partiellement normalisée si ses paramètres ou
dépendances métier ne sont pas suffisamment établis. Les règles L2 historiques
conservées ne réintroduisent pas ces fonctionnalités dans le contrat V1.

Pour faire évoluer une règle, examiner ensemble sa syntaxe, son contexte, ses
valeurs autorisées et le mapping consommateur. Un ajout de règle doit être validé
avec une configuration synthétique non sensible dans le dépôt de développement.
Les tests de développement ne sont pas inclus dans cette distribution.

## EIGRP synchronisé

`cisco_ios/routing/eigrp.ttp` appartient à la famille de parsing `eigrp`.
`cisco_ios/interfaces/eigrp.ttp` appartient à `interfaces`. La métrique vectorielle
de route-map est reconnue dans `cisco_ios/policies.ttp`, en conservant la métrique
scalaire existante. La [matrice EIGRP](../docs/eigrp/matrice_commandes.csv) répertorie
les 129 règles ajoutées ; les limites de portée sont détaillées dans [le guide](../docs/eigrp/README.md).
