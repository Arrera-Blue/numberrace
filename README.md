# La Course aux Nombres (The Number Race) — Packaging RPM Fedora

Packaging RPM Fedora pour **La Course aux Nombres** (*The Number Race*) v3.1.1 (édition française), un jeu éducatif adaptatif conçu par l'Unité INSERM-CEA de Neuroimagerie Cognitive.

## Contenu du dépôt

- [`numberrace.spec`](numberrace.spec) — Fichier spec RPM (`noarch`).
- [`build-rpm.sh`](build-rpm.sh) — Script de construction du `.noarch.rpm` et du `.src.rpm` dans `./dist/`.
- [`extract-izpack.py`](extract-izpack.py) — Extracteur Python sans dépendance Java pour lire les packs IzPack de l'installeur `.jar`.
- [`make-icons.py`](make-icons.py) — Génération des icônes hicolor arrondies (`48x48` à `256x256`) pour l'intégration GNOME.
- [`numberrace.sh`](numberrace.sh) — Script lanceur installé dans `/usr/bin/numberrace`.
- [`numberrace.desktop`](numberrace.desktop) — Entrée desktop (avec action de lancement en mode fenêtré).
- [`org.unicog.numberrace.metainfo.xml`](org.unicog.numberrace.metainfo.xml) — Métadonnées AppStream.
- `numberrace-installer-3.1.1-fr.jar` — Installeur IzPack amont (licence GPL-2.0-only).

## Prérequis de build (Fedora)

```bash
sudo dnf install rpm-build appstream desktop-file-utils python3 python3-pillow rpmlint
```

Dépendance à l'exécution : `java >= 1:1.8.0` (ex. `java-latest-openjdk` ou `java-21-openjdk`).

## Construction du RPM

Construire le RPM binaire (`.noarch.rpm`) et le SRPM (`.src.rpm`) dans `./dist/` :

```bash
./build-rpm.sh
```

Autres options :

```bash
./build-rpm.sh --srpm-only   # Construit uniquement le .src.rpm (ex. pour Fedora COPR)
./build-rpm.sh --clean       # Supprime ./rpmbuild/ et ./dist/
```

## Installation locale

```bash
sudo dnf install ./dist/numberrace-*.noarch.rpm
```
