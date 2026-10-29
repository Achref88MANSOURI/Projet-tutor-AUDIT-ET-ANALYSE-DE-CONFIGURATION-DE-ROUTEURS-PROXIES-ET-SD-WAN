# Exemples EIGRP synthétiques

[Guide Web complet](../../GUIDE_DEMONSTRATION_WEB.md) · [Couverture EIGRP](../../docs/eigrp/README.md)

Ces trois configurations complètent les 20 exemples du dossier parent. Elles
servent à exercer le parser, les mappings et le contrat V1. Les credentials ont été
remplacés par des marqueurs constants ; les configurations ne servent pas à établir
des sessions réelles avec ces marqueurs.

| Fichier | Couverture principale |
|---|---|
| `classic_ipv4.cfg` | AS classique 100, réseaux/wildcards, passivité, métriques, distances, redistribution, filtrage, interfaces et AF VRF BLUE/AS 200 |
| `classic_ipv6.cfg` | AS IPv6 20, activation explicite, timers, split horizon, références de clés, résumé IPv6 et référence d'interface AS 99 non résolue |
| `named_dualstack.cfg` | Processus CAMPUS, AF IPv4/IPv6, VRF BLUE, défauts et exceptions d'interface, topologies base/VOICE et authentification |

Dans le Web, importer le fichier, choisir IOS ou IOS-XE selon l'essai, puis lancer
la normalisation. Exemple CLI depuis la racine :

```powershell
.\.venv\Scripts\python.exe cli.py resources/eigrp/named_dualstack.cfg --output outputs/eigrp-demo --os-family iosxe
```

Le résultat nommé doit conserver trois familles d'adresses. L'AF IPv4 BLUE/AS 100
contient une topologie base de variance 3 et une topologie VOICE de variance 4.
Les réglages du bloc d'interface default restent distincts des exceptions locales.
La référence AS 99 du fichier IPv6 ne crée pas de processus fictif.
