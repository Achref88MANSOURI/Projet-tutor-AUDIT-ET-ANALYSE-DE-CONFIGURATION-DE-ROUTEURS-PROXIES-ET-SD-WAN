# Configurations de démonstration

[Guide d'utilisation](../README.md) · [Interface Web](../web/README.md) · [Contrat V1](../schemas/README.md)

Ce dossier contient 23 configurations : les 20 fichiers de corpus décrits ci-dessous et 3 exemples EIGRP synthétiques dans le sous-dossier `eigrp/`. Les valeurs des credentials reconnus ont été remplacées par des marqueurs constants. Les sources originales du dépôt de développement sont préservées.

Ces fichiers servent à tester le parsing et la normalisation ; les marqueurs de remplacement ne sont pas des clés utilisables sur un équipement. Les autres identifiants, adresses et paramètres métier sont conservés.

Dans le Web, importer un des fichiers `.cfg`. En CLI, depuis la racine du dépôt :

```powershell
.\.venv\Scripts\python.exe cli.py .\resources\C0031_CE1.cfg --output .\outputs\demo --os-family iosxe
```

| Fichier | Fonctions observées |
|---|---|
| C0031_CE1.cfg | Interfaces L3, VRF, Routes statiques, SSH, Négations explicites |
| C0044_CE-1A.cfg | Interfaces L3, VRF, Routes statiques, Négations explicites |
| C0019_R1.cfg | Interfaces L3, IPv6, VRF, BGP, OSPF, ACL, Négations explicites |
| C0021_R3.cfg | Interfaces L3, IPv6, BGP, OSPF, Politiques, Négations explicites |
| C0014_ASBR-2122.cfg | Interfaces L3, IPv6, BGP, Négations explicites |
| C0017_CE-HQ.cfg | Interfaces L3, BGP, Négations explicites |
| C0025_R-PrivateASN100.cfg | Interfaces L3, BGP, Politiques, Négations explicites |
| C0026_R-PublicASN111.cfg | Interfaces L3, BGP, Politiques, Négations explicites |
| C0016_CE-BR.cfg | Interfaces L3, RIP, Négations explicites |
| C0064_PE-1.cfg | Interfaces L3, IS-IS, Négations explicites |
| C0106_CE-1A.cfg | Interfaces L3, VRF, OSPF, Négations explicites |
| C0148_R1.cfg | Interfaces L3, OSPF, Négations explicites |
| C0001_as1border1.cfg | Interfaces L3, BGP, OSPF, ACL, Politiques, Négations explicites |
| C0007_as2dept1.cfg | Interfaces L3, BGP, ACL, Politiques, Négations explicites |
| C0010_as3border1.cfg | Interfaces L3, BGP, OSPF, ACL, Politiques, Négations explicites |
| C0004_as2border1.cfg | Interfaces L3, BGP, OSPF, ACL, Politiques, Négations explicites |
| C0032_CE2.cfg | Interfaces L3, Routes statiques, BGP, SSH, Négations explicites |
| C0033_CE3.cfg | Interfaces L3, Routes statiques, BGP, SSH, Négations explicites |
| C0042_rt1.bsqmk.cfg | Interfaces L3, IPv6, VRF, Routes statiques, BGP, OSPF, ACL, Politiques, SSH, Négations explicites |
| C0123_PE-1.cfg | Interfaces L3, VRF, BGP, OSPF, IS-IS, ACL, Négations explicites |

Les commandes AAA présentes concernent principalement l’activation ou la désactivation de AAA. Ces fichiers ne couvrent pas à eux seuls toutes les commandes d’authentification de routage ou tous les groupes/serveurs AAA du contrat. Certaines commandes peuvent rester non prises en charge ; les fonctions L2 hors périmètre ne sont pas ajoutées au JSON canonique.

## Exemples EIGRP supplémentaires

Voir [l'inventaire EIGRP](eigrp/README.md) pour les trois fichiers classique IPv4,
classique IPv6 et nommé double pile/VRF. Le [guide de démonstration Web](../GUIDE_DEMONSTRATION_WEB.md)
explique comment les importer et quelles propriétés examiner.
