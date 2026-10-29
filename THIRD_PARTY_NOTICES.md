# Templates et dépendances tierces

Les quatre fichiers de `templates/upstream/` correspondent aux templates du paquet
`ttp_templates` 0.6.18 utilisé par le projet. Ils sont conservés pour la vérification
de cohérence à l'exécution. La licence MIT du projet amont est reproduite dans
`licenses/ttp_templates-MIT.txt`.

Projet amont : https://github.com/dmulyalin/ttp_templates

Les distributions Python présentes dans `wheelhouse/` sont les dépendances
d'exécution figées par `requirements.lock`. Chaque archive conserve ses métadonnées
et les fichiers de licence fournis par son auteur. Ces archives sont nécessaires
à l'installation reproductible hors ligne sous Windows x64 / Python 3.12 ; elles
ne contiennent pas le corpus de développement ni les tests de ce projet.
