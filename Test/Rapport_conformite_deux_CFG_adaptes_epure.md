# Rapport de conformité de normalisation — deux configurations Cisco adaptées

> **Actualisation de la distribution — 29 octobre 2026.** Ce rapport conserve
> les résultats de comparaison initiaux. Les deux JSON du dossier ont depuis été
> régénérés avec le moteur corrigé, à partir des mêmes CFG. L’indicateur IS-IS nommé
> est désormais `declared: true`. Les 233 assertions annoncées ci-dessous n’ont pas
> été réexécutées comme une nouvelle campagne indépendante. Voir le
> [bilan de synchronisation](../docs/MISE_A_JOUR_NORMALISATION.md).

> **Portée du rapport.** La « conformité » signifie ici **fidélité de transformation CFG → JSON**, et non conformité CIS/STIG, sécurisation de la configuration ou fonctionnement d'un routeur réel. Les configurations sont des fixtures synthétiques et portent l'avertissement `DO NOT DEPLOY`. Cette analyse utilise les deux CFG adaptés et les deux JSON renvoyés ; elle ne réexécute pas le parseur ni un routeur Cisco.

## 1. Synthèse comparative

| Indicateur vérifié | Test 01 — IOS 15 EDGE | Test 02 — IOS-XE 17 PE |
|---|---:|---:|
| Lignes du CFG adapté | 284 | 229 |
| Commandes significatives (hors commentaires, séparateurs, `end`, `exit-address-family`) | 224 | 167 |
| Assertions de comparaison ciblées | **129 / 129 réussies** | **104 / 104 réussies** |
| Interfaces | **10 / 10** | **10 / 10** |
| VRF | **1 / 1** | **3 / 3** |
| Processus OSPF | **2 / 2** (v2 et v3) | **2 / 2** (v2 dans deux VRF) |
| IS-IS | Non configuré | **1 / 1** |
| Voisins BGP | **3 / 3** | **2 / 2** |
| Familles BGP | **3 / 3** | **4 / 4** |
| Route-maps (et séquences) | **4 / 4** (**9 / 9**) | **1 / 1** (**3 / 3**) |
| Prefix-lists | **5 / 5** | **3 / 3** |
| ACL (et règles) | **5 / 5** (**11 / 11**) | **2 / 2** (**4 / 4**) |
| Attachements ACL | **2 / 2** | Aucun configuré |
| Class-maps / policy-maps QoS | Non configurées | **5 / 5** et **1 / 1** |
| Attachements QoS | Non configurés | **1 / 1** |
| Trustpoints PKI | Non configurés | **2 / 2** |
| Références croisées testées sur la sortie | **19 / 19 valides** | **13 / 13 valides** |

**Verdict :** les deux couples sont **conformes aux contrôles ciblés effectués** et constituent désormais de bons exemples de transformation CFG → JSON pour les domaines effectivement vérifiés. **Le ratio 233/233 représente le succès des assertions ciblées, et non une preuve de couverture de 391/391 commandes, ni une précision statistique universelle.**

## 2. Test 01 — Cisco IOS 15 multiprotocole

**Fichiers comparés :** `01_IOS15_EDGE_MULTIPROTOCOL_adapte.cfg` et `01_IOS15_EDGE_MULTIPROTOCOL_adapte.json`.

| Fonction | Preuve dans le CFG | Représentation JSON vérifiée | Constat |
|---|---|---|---|
| Identité | `hostname LAB-IOS15-EDGE` | `system.identity.hostname` | Identique |
| Interfaces, IPv4 et IPv6 | 10 blocs `interface`, dont deux sous-interfaces 802.1Q et un tunnel | `interfaces[]`, adresses CIDR, `encapsulation`, états administratifs | 10/10 ; masques et VLAN corrects |
| VRF de gestion | `ip vrf MGMT`, `rd 65000:99`, `ip vrf forwarding MGMT` | `network_instances[]` et liaison sur `FastEthernet0/2` | Correct |
| OSPFv2 / v3 | `router ospf 1`, `ipv6 router ospf 1`, interfaces liées aux aires | `routing.ospf[]` et `interfaces[].ospf_bindings` | 2 processus et paramètres vérifiés |
| BGP dual-stack | `router bgp 65000`, groupes `IBGP`, `ISP4`, `ISP6`, familles IPv4, multicast et IPv6 | `routing.bgp[]` | 3 voisins, 3 peer-groups, 3 familles corrects |
| Route-map d'import corrigée | `route-map IN-ISP4 permit 10` ; `match ip address prefix-list ALLOW-IN` ; `set local-preference 350` | `routing_policies.route_maps[name=IN-ISP4]` | Définition et action 350 conservées |
| Politiques BGP | `IN-ISP4`, `OUT-ISP4`, `IN-ISP6`, `OUT-ISP6` | `routing_policies.route_maps[]` | 4/4 route-maps, 9/9 séquences |
| ACL | ACL de gestion, SNMP, `EDGE-OUT`, `SHADOW-TEST`, `101` | `security.acls[]` ; `security.acl_attachments[]` | 5 listes, 11 entrées, 2 attachements |
| Multicast | PIM sparse-mode, BSR, RP, SSM, MSDP | `multicast` et `interfaces[].pim_mode` | Paramètres principaux conservés |
| Administration | SSHv2, VTY SSH, NTP, Syslog, SNMP, archive/hidekeys | `system.management`, `ntp`, `logging`, `snmp`, `config_archive` | Champs contrôlés conformes |
| NetFlow local | `ip flow-cache timeout active 5`, `inactive 60`, `ip flow ingress/egress` | `system.flow_monitoring.export`, `interfaces[].flow_directions` | Délais et directions corrects |
| Routage statique | IPv4, IPv6, Null0, VRF MGMT | `routing.static_routes[]` | 4/4 routes |

### Exemple de fidélité de la politique BGP entrante

**CFG :**

```cisco
neighbor ISP4 route-map IN-ISP4 in
route-map IN-ISP4 permit 10
 match ip address prefix-list ALLOW-IN
 set local-preference 350
route-map IN-ISP4 deny 999
```

**JSON :** `routing.bgp[0].address_families[afi=ipv4].peers[peer=ISP4].import_policies = ["IN-ISP4"]` ; `routing_policies.route_maps[name=IN-ISP4]` contient deux séquences, dont la séquence `10` avec la condition de prefix-list et `local_preference = 350`. La définition et son rattachement BGP sont tous deux présents.

**Nuances qui ne constituent pas des pertes de commande démontrées :** `send_community = "command_without_option"` indique la présence de la directive sans la canoniser complètement ; `Tunnel0.technology = "unknown"` alors qu'aucun `tunnel mode` explicite n'est fourni ; la règle ICMP de `SHADOW-TEST` reste présente après `deny ip any any`, conformément à l'ordre du CFG, même si elle est inatteignable dans cette ACL.

## 3. Test 02 — Cisco IOS-XE 17, PE L3VPN / QoS

**Fichiers comparés :** `02_IOSXE17_PE_L3VPN_QOS_adapte.cfg` et `02_IOSXE17_PE_L3VPN_QOS_adapte.json`.

| Fonction | Preuve dans le CFG | Représentation JSON vérifiée | Constat |
|---|---|---|---|
| Interfaces | 4 Loopback et 6 GigabitEthernet ; `ip unnumbered`, DHCP, VRF, MPLS | `interfaces[]` | 10/10, attributs vérifiés |
| L3VPN | VRF `CUSTOMER_A`, `CUSTOMER_B`, `MGMT`, RD, RT | `network_instances[]` | 3 VRF, RD et RT conservés |
| OSPF par VRF | `router ospf 1 vrf CUSTOMER_A`, `router ospf 2 vrf CUSTOMER_B` | `routing.ospf[]` | Deux processus et réseaux corrects |
| IS-IS | `router isis CORE`, NET et interface passive | `routing.isis[0]` | Instance, NET et passive-interface conservés |
| MPLS/LDP | `mpls ip` sur Gi1/Gi2 ; `mpls ldp router-id Loopback0` | `interfaces[].mpls_enabled`, `mpls.ldp` | Fidèle |
| BGP | `router bgp 500`, deux voisins, VPNv4, IPv4 global, IPv4 par VRF | `routing.bgp[]` | 2 voisins, 4 familles et redistributions |
| AS-PATH prepend | `AS-PREPEND-TEST`, séquences 10, 20, 30, prepend 65101 deux fois et 25 | `routing_policies.route_maps[]` | 3/3 séquences et actions correctes |
| ACL VoIP | `ip access-list extended SIP` et `VOIP` | `security.acls[]` | 2 ACL, 4 règles et ports exacts |
| QoS voix | 5 class-maps ; `policy-map VOICE-QOS-CUST-A` ; 3 classes, DSCP ; interface Gi3 | `qos.class_maps[]`, `policy_maps[]`, `attachments[]` | 5 class-maps, 1 policy-map, 1 attachement |
| PKI déclarative | Trustpoints `SLA-TrustPoint` et `TP-self-signed-3925927892` | `pki.trustpoints[]` | 2/2 correctement identifiés |
| Administration | AAA local, SSHv2, HTTPS, compte local, Call Home | `system.aaa`, `management`, `call_home` | Valeurs ciblées exactes |

### Exemple de fidélité QoS

**CFG :**

```cisco
class-map match-all VOIP-CUST-A
 match access-group name VOIP
policy-map VOICE-QOS-CUST-A
 class VOIP-CUST-A
  set dscp ef
interface GigabitEthernet3
 service-policy input VOICE-QOS-CUST-A
```

**JSON :** `qos.class_maps[name=VOIP-CUST-A].matches` référence `VOIP` ; `qos.policy_maps[name=VOICE-QOS-CUST-A].classes[name=VOIP-CUST-A].actions` porte `set_dscp = ef` ; `qos.attachments[]` relie `VOICE-QOS-CUST-A` à `GigabitEthernet3` en **ingress**. Les trois dépendances se résolvent.

**Nuance résiduelle :** `routing.isis[0].declared = null` malgré la déclaration explicite `router isis CORE`. L'objet et ses paramètres existent : la capacité d'extraction du protocole est établie, mais ce booléen de déclaration n'est pas explicite. Les trois class-maps `VOICE`, `SIP` et `VIDEO` sont définies sans être utilisées dans la policy-map conservée ; une définition non utilisée n'est pas une erreur de parsing.

## 4. Intégrité des références et distinction des valeurs nulles

L'intégrité a été vérifiée pour les interfaces et leurs VRF, les interfaces `ip unnumbered`, les attachements ACL, les attachements QoS, les relations entre class-maps et ACL, les `match` vers des prefix-lists et les politiques BGP import/export. Les deux JSON ne présentent **aucune référence orpheline dans ces contrôles** (19/19 et 13/13).

`device.vendor`, `device.platform` et `device.software_version` restent `null` ; les deux CFG adaptés n'ont ni commande `version` ni PID explicitement déclaré. Ces `null` ne sont donc pas comptés comme pertes de commandes explicites. Le dialecte Cisco est identifié par le contexte du test, et non matérialisé dans `device.vendor`. De même, `system.management.ssh.enabled = null` n'annule pas la bonne extraction de `ip ssh version 2` : une version configurée ne prouve pas seule la disponibilité du service en fonctionnement.

La normalisation préserve la source, elle ne corrige pas les ACL mal ordonnées, ne prouve pas le fonctionnement des adjacences OSPF/BGP et ne remplace pas un audit sur équipement réel.

## 5. Méthode des assertions et verdict

Un vérificateur indépendant a contrôlé les deux couples par des assertions d'identité, de structure, de valeur, de cardinalité, d'appartenance et de résolution de références :

| Famille de contrôles | Test 01 | Test 02 |
|---|---:|---:|
| Structure et identité | 3/3 | 3/3 |
| Interfaces | 38/38 | 32/32 |
| Références entre objets | 19/19 | 13/13 |
| Domaine système / administration | 20/20 | 12/12 |
| Routage, VRF, BGP, OSPF, IS-IS, statiques | 27/27 | 21/21 |
| Politiques, ACL, QoS, multicast, MPLS, PKI, tunnels | 22/22 | 23/23 |
| **Total** | **129/129** | **104/104** |

**Bilan consolidé : 233 assertions sur 233 réussies.** Les **391 commandes significatives** (224 + 167) forment le périmètre de lecture de la source, mais seules les **233 assertions énumérées dans le vérificateur** ont fait l'objet de comparaisons explicites : il serait donc incorrect de publier « 100 % des commandes normalisées » sur cette seule base.

**Verdict Test 01 : CONFORME AUX VÉRIFICATIONS CIBLÉES** — exemple pertinent pour BGP dual-stack, OSPFv2/v3, VRF, interfaces, ACL, multicast et administration.  
**Verdict Test 02 : CONFORME AUX VÉRIFICATIONS CIBLÉES, AVEC UNE NUANCE IS-IS** — exemple pertinent pour L3VPN, BGP VPNv4, OSPF, IS-IS, MPLS/LDP, AS-PATH prepend, ACL voix et QoS.

Les deux couples peuvent être utilisés pour démontrer la normalisation **sur ces fonctionnalités validées**. Une revendication de fidélité exhaustive exigerait de mapper **chaque commande** à un champ JSON ou à un diagnostic traçable, puis d'effectuer des tests réels de non-régression sur le parseur et éventuellement des équipements Cisco.

