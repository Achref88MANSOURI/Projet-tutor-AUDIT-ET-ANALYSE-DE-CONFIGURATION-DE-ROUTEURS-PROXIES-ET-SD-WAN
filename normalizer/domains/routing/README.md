# Routage — processus, contextes et relations

[Domaines métier](../README.md) · [Moteur](../../README.md) · [Templates](../../../templates/README.md)

## Organisation

| Module | Rôle |
|---|---|
| `static_routes.py` | Routes IPv4/IPv6, next-hop, interface de sortie, VRF et attributs reconnus |
| `bgp.py` | Processus BGP, ASN, voisins, peer-groups, AF et options reconnues |
| `ospf.py` | Processus OSPFv2/v3, aires, network statements et paramètres associés |
| `rip.py` | Processus RIP, networks, contextes AF/VRF et redistributions reconnues |
| `vrf.py` | Network instances, RD, route targets et contextes de familles |
| `prefix_lists.py` | Prefix-lists IPv4/IPv6, séquences, préfixes et bornes |
| `authentication.py` | Authentification BGP, OSPFv2, IS-IS et RIP selon la portée |
| `key_chains.py` | Key chains, identifiants de clés et métadonnées reconnues |

Le mapping ordinaire IS-IS se trouve dans `cisco_features.py`, au niveau supérieur.
Son authentification utilise le helper commun de ce dossier. La présence d'un
protocole dans le contrat ne signifie pas que toutes ses commandes sont extraites.

## Préservation des contextes

### BGP

Le processus conserve son ASN local et ses paramètres propres. Les voisins et
peer-groups restent distincts. Les address-families conservent l'AFI, le SAFI
lorsqu'il est établi et la VRF éventuelle.

Un même voisin peut avoir des paramètres différents au niveau global et dans
plusieurs familles. Ces réglages ne sont pas regroupés dans un unique objet sans
portée. Les références d'héritage sont conservées ; le normaliseur ne calcule pas
automatiquement une configuration effective héritée.

Les route-maps d'entrée/sortie restent des références de politiques. Networks,
agrégats, redistributions et options sont conservés selon les captures reconnues.

### OSPF

Les identités des processus distinguent version, identifiant et contexte réseau.
Les network statements préservent l'adresse et le wildcard natifs ainsi que l'aire.
Un préfixe canonique n'est établi que lorsque la conversion est cohérente.

Les aires, virtual links, paramètres reconnus et relations d'interfaces conservent
leur portée. La définition d'un processus OSPF ne signifie pas que ses interfaces
ou voisins opérationnels sont connus.

### IS-IS et RIP

IS-IS conserve les identifiants ou déclarations de processus, NET et paramètres
reconnus. Les réglages d'authentification peuvent être distingués par niveau.
RIP conserve les networks et redistributions dans le contexte reconnu, avec les
familles/VRF lorsqu'elles sont présentes.

## Authentification

Le mapping traite les commandes couvertes de mots de passe BGP, authentification
d'aire/interface OSPFv2, modes/références IS-IS, authentification RIP et key chains.
Les valeurs secrètes ont déjà été masquées par le parser.

Les objets peuvent préserver la méthode, l'algorithme, un format de credential,
un identifiant ou une référence de clé et les marqueurs de réglage local. Ils
distinguent une configuration locale, sa suppression et certaines désactivations
explicites. Une suppression locale ne prouve pas l'absence d'héritage.

Les paramètres restent indéterminés si la syntaxe capturée ne suffit pas à établir
le mécanisme. L'authentification 802.1X/PPP d'interface est hors de ce contrat.

## Routes et références

Les routes statiques distinguent le préfixe de destination, le next-hop et l'interface
de sortie. Une référence d'interface ne doit pas être remplacée par une adresse
supposée. Les familles IP et les contextes réseau sont validés.

Les VRF et politiques référencées ne sont pas inventées. Les identités des prefix-lists
incluent leur famille, et l'ordre de leurs entrées est significatif.

## Valeurs inconnues et erreurs

Une commande absente ne produit ni défaut Cisco supposé ni booléen `false` automatique.
Une erreur canonique Pydantic empêche l'export. Une syntaxe non couverte reste une
limite de reconnaissance ; elle ne doit pas être transformée en donnée de routage
inventée. Les contrôles internes ne sont pas exportés comme résultats d'audit.

## EIGRP

`eigrp.py` conserve les processus classiques IPv4/IPv6 et nommés. Les AS d'un
processus nommé restent dans ses familles d'adresses. Les topologies et blocs
d'interface conservent leur portée ; les défauts et exceptions ne sont pas fusionnés
en une configuration effective supposée. Les resets sont distingués d'une négation
booléenne et les références non résolues sont conservées sans objet fictif.
Voir [le guide EIGRP](../../../docs/eigrp/README.md) et les
[exemples à importer](../../../resources/eigrp/README.md).
