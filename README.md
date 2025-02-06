# **Projet Crossroad**
---
## **But du projet**

Ce projet en langage Python a pour but de simuler le traffic routier sur un carrefour à 4 axes, avec des feux bicolores et des véhicules prioritaires ou non, apparaissant de manière aléatoire.

---
## **Comment lancer la simulation ?**

Il faut ouvrir 2 terminaux différents et lancer sur chaque terminal les commandes suivantes :
```bash
python3 main.py
python3 display.py
```
---
## **Comment stopper la simulation ?**

Il faut d'abord faire le raccourci "Ctrl+C" sur le terminal qui lance le main.py et ensuite le faire sur le terminal qui lance le display.py.

---

## **Fichiers/dossier**
| Fichiers                    | Description |
|-------------------------|-------------|
| `main.py`               | Lance tout les processus sauf display |
| `coordinator.py`        | Gestion des véhicules |
| `lights.py`             | Gestion des feux de circulation |
| `display.py`           | Génère l'affichage en direct l'évolution des voitures et communique en TCP |
| `normal_traffic_gen.py` | Génère les véhicules |
| `priority_traffic_gen.py` | Génère les véhicules prioritaires |
| `sysv_ipc-1.1.0`         | Dossier comprenant la bibliothèque sysv_ipc |
| `Beta`     | Ancienne version du programme |
