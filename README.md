# La Course aux Nombres (*The Number Race*) — Packaging RPM Fedora

## Objectif du projet

Ce dépôt a pour but de **packager [La Course aux Nombres](http://thenumberrace.com) (*The Number Race*, v3.1.1 — édition française) sous forme de paquet RPM Fedora** (`noarch` et `SRPM`).

À l'origine, le logiciel est distribué sous la forme d'un ancien installeur graphique Java IzPack (`numberrace-installer-3.1.1-fr.jar`). Ce projet automatise l'extraction et l'empaquetage de l'application afin d'offrir une **installation système propre, reproductible et intégrée au bureau Linux** (notamment GNOME sur Fedora) :

- **Extraction sans installeur graphique** : lecture directe des flux `PackFile` sérialisés de l'archive IzPack en Python (`extract-izpack.py`).
- **Intégration bureau** : lanceur `/usr/bin/numberrace`, fichier `.desktop` (incluant une action de lancement en mode fenêtré), icônes `hicolor` générées aux formats `48x48` à `256x256` et métadonnées AppStream.
- **Compatibilité COPR** : génération d'un `.src.rpm` autonome prêt à être compilé localement ou sur Fedora COPR.

## À propos du logiciel empaqueté

**La Course aux Nombres** est un jeu éducatif adaptatif conçu par l'**Unité INSERM-CEA de Neuroimagerie Cognitive** pour les enfants de **4 à 8 ans**. Il permet de découvrir et de pratiquer les concepts numériques et arithmétiques de base et d'aider à la remédiation de la dyscalculie.

- **Version empaquetée** : `3.1.1` (édition française)
- **Licence** : `GPL-2.0-only`
- **Site officiel** : http://thenumberrace.com

## Contenu du dépôt

- [`numberrace.spec`](numberrace.spec) — Fichier spec RPM (`noarch`).
- [`build-rpm.sh`](build-rpm.sh) — Script de construction du `.noarch.rpm` et du `.src.rpm` dans `./dist/`.
- [`extract-izpack.py`](extract-izpack.py) — Extracteur Python pour lire les packs IzPack de l'installeur `.jar` sans dépendance Java au build.
- [`make-icons.py`](make-icons.py) — Génération des icônes `hicolor` arrondies (`48x48` à `256x256`) à partir de l'icône 64×64 d'origine.
- [`numberrace.sh`](numberrace.sh) — Script lanceur installé dans `/usr/bin/numberrace`.
- [`numberrace.desktop`](numberrace.desktop) — Entrée desktop (avec action de lancement en mode fenêtré `in-window`).
- [`org.unicog.numberrace.metainfo.xml`](org.unicog.numberrace.metainfo.xml) — Métadonnées AppStream pour les gestionnaires de logiciels.
- `numberrace-installer-3.1.1-fr.jar` — Archive d'installation IzPack amont.

## Prérequis (Fedora)

Outils nécessaires pour construire le paquet :

```bash
sudo dnf install rpm-build appstream desktop-file-utils python3 python3-pillow rpmlint
```

Dépendance requise pour exécuter le jeu après installation :

- `java >= 1:1.8.0` (OpenJDK)

## Construction du RPM

Construire le RPM binaire (`.noarch.rpm`) et le SRPM (`.src.rpm`) dans `./dist/` :

```bash
./build-rpm.sh
```

Options disponibles :

```bash
./build-rpm.sh --srpm-only   # Construit uniquement le .src.rpm (utile pour Fedora COPR)
./build-rpm.sh --clean       # Supprime les dossiers générés ./rpmbuild/ et ./dist/
```

## Installation et utilisation

```bash
sudo dnf install ./dist/numberrace-*.noarch.rpm
```

Le jeu est ensuite accessible depuis le menu d'applications (*La Course aux Nombres*) ou en ligne de commande :

```bash
numberrace
numberrace in-window   # Pour lancer en mode fenêtré
```
