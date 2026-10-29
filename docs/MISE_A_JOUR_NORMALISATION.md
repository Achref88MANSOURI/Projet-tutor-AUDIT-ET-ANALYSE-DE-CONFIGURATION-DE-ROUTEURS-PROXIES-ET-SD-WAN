# Synchronisation du normaliseur et de sa distribution

Mise à jour : 29 octobre 2026.

Cette distribution contient les sources corrigées du dépôt principal : parser,
templates personnalisés et amont, mappings métier, moteur, validation, contrat
Pydantic, JSON Schema et backend Web. Le programme d'installation hors ligne,
les dépendances d'exécution et les guides propres à cette copie sont conservés.

## Correctifs inclus

- Route-maps avec conditions de communauté, combinaison avec prefix-list et actions.
- ACL TCP `established`, distinct des options `log` et `log-input`.
- QoS `match precedence` et `match ip precedence`, avec portée IPv4/IPv6 conservée.
- Version explicite et PID matériel, sans publication du numéro de série.
- Images locales de boot ordonnées, paramètres de caches NetFlow séparés des réglages globaux, persistance SNMP ifIndex et contact Call Home.
- Aires OSPF cohérentes, AFI des networks BGP et présence de texte de bannière sans son contenu.
- Service password-encryption positif/négatif, déclaration IS-IS nommée ou non nommée, paramètres QFP et punt explicitement configurés.
- Contrôle des définitions connues retirées comme incomplètes mais encore référencées : refus d'export, sans politique partielle publiée ni référence supprimée pour cacher une perte.

Une référence à un objet absent du fichier fourni reste littérale. Une commande
absente ne devient pas `false` ou `[]`. Le pipeline reste unique, sans convertisseur
historique ni export métier parallèle.

## Exemples et résultats conservés

Les **25 configurations CFG** sont inchangées : 20 configurations de corpus,
trois exemples EIGRP et deux cas adaptés sous `Test/`.

Les deux JSON de `Test/` ont été **régénérés avec le moteur distribué**, après
validation. Le cas IOS-XE conserve désormais explicitement `IsisProcess.declared`
à `true`. Le rapport de comparaison initial reste présent avec une note datée :
les 233 assertions qu'il annonce ne sont pas présentées comme une nouvelle
campagne réexécutée.

Les sources des tests automatisés, leurs traces, les caches, environnements Python
et sorties de développement ne sont pas inclus dans cette copie.

## Vérifications de cette synchronisation

La copie a été exécutée avec un interpréteur isolé disposant uniquement des
dépendances d'exécution, en vérifiant que les modules importés provenaient de
cette distribution :

| Contrôle | Résultat |
|---|---|
| Deux cas de `Test/` | CLI et backend Web, Pydantic/JSON Schema : réussis ; 10 interfaces et respectivement une/trois VRF conservées. |
| Trois exemples EIGRP | CLI et validation : réussis. |
| Scénario synthétique combinant les correctifs | Backend Web et validation : réussis ; conditions de communauté, ACL, QoS, service, IS-IS et paramètres de plateforme vérifiés. |
| Confidentialité du scénario synthétique | Credential témoin absent de la sortie et des captures intermédiaires. |
| Schéma généré | Identique au schéma produit par les modèles distribués. |

Ces vérifications ciblées ne constituent pas un rejeu exhaustif des configurations,
ni une qualification des commandes sur du matériel réel.

## Schéma, périmètre et utilisation

Le contrat reste `RouterContractV1` / `1.0.0`, avec les champs typés ajoutés lors des
correctifs. Le [JSON Schema fourni](../schemas/router_contract_v1.schema.json)
doit accompagner les nouveaux résultats. La [convention de compatibilité](../schemas/COMPATIBILITE.md)
précise l'identification du schéma par révision Git et empreinte SHA-256 ; un ancien
validateur fermé n'est pas automatiquement compatible.

Les fonctionnalités L2, bridge-domains, service-instances et EVPN/L2VPN L2 restent
hors périmètre. Les modèles matériels, rôles, technologies de tunnel implicites et
héritages effectifs ne sont pas inventés. PKI reste déclarative.

Après installation avec `setup.ps1`, lancer `run_ui.ps1`. Après une mise à jour,
arrêter l'ancien serveur avec Ctrl+C et le relancer avant d'actualiser le navigateur.
Voir le [guide complet](../GUIDE_DEMONSTRATION_WEB.md) pour les commandes de clonage,
d'installation et d'essai.

Cette synchronisation locale ne publie aucun commit et ne met pas automatiquement
à jour le clone `normaliseur-publication` ni le dépôt GitHub.
