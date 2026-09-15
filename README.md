# Parental Control – Intégration Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Intégration HACS pour Home Assistant qui applique un **planning hebdomadaire** à un switch de contrôle parental : pour chaque jour de la semaine, vous définissez une plage horaire pendant laquelle le switch est **éteint automatiquement**. En dehors de cette plage, le switch est **rallumé**.

Cette intégration a été créée à l'origine pour piloter les **switchs de contrôle parental GL.iNet** exposés par [ha-glinet-router](https://github.com/vithurshanselvarajah/ha-glinet-router). Elle fonctionne avec n'importe quel switch Home Assistant.

---

## Objectif

Sur un routeur GL.iNet, le contrôle parental se présente souvent comme un switch Home Assistant (un groupe, un profil ou un accès internet enfant). Ce module sert à **ouvrir l'accès pendant des horaires précis** et à **remettre le contrôle parental en place le reste du temps**, sans écrire d'automations YAML.

Vous pouvez ajouter plusieurs instances, par exemple une par enfant ou par groupe GL.iNet.

---

## Fonctionnement

| Moment | Action par défaut sur le switch |
|--------|----------------------------------|
| Pendant la plage du jour | `switch.turn_off` — le contrôle parental est désactivé |
| En dehors de la plage | `switch.turn_on` — le contrôle parental est réactivé |
| Jour non activé dans le planning | le switch reste allumé toute la journée |

- Si l'heure de début est **postérieure** à l'heure de fin (exemple : 21:00 → 07:00), la plage **passe minuit**.
- Le planning est réévalué **toutes les minutes** et aussi au démarrage de Home Assistant.
- Un switch **Planification** permet de suspendre l'application automatique sans supprimer le planning.
- L'option **Inverser la logique du switch** inverse on/off si votre switch GL.iNet (ou un autre) a un sens opposé.

---

## Entités créées

Pour chaque instance (par exemple `Enfants`) :

| Entité | Type | Description |
|--------|------|-------------|
| `switch.enfants_planification` | Switch | Active ou suspend le planning automatique |
| `binary_sensor.enfants_plage_autorisee` | Binary sensor | `on` pendant la plage autorisée |
| `sensor.enfants_prochain_changement` | Sensor | Horodatage du prochain allumage/extinction |
| `sensor.enfants_statut` | Sensor | `allowed` / `restricted` / `disabled` / `unavailable` |

Les identifiants d'entités dépendent du nom que vous donnez à l'instance.

---

## Installation via HACS

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur **Intégrations** → ⋮ → **Dépôts personnalisés**
3. Ajoutez l'URL : `https://github.com/daxharry/hacs_parental_control`
4. Catégorie : **Intégration**
5. Cliquez sur **Télécharger**
6. Redémarrez Home Assistant

Cette intégration HACS s'installe depuis le contenu de la branche du dépôt, sans archive de release GitHub. Le fichier `hacs.json` définit donc `zip_release: false`.

## Installation manuelle

1. Copiez le dossier `custom_components/parental_control/` dans `/config/custom_components/`
2. Redémarrez Home Assistant

---

## Configuration

1. Allez dans **Paramètres → Appareils & services → Ajouter une intégration**
2. Recherchez **Parental Control**
3. Donnez un nom (par exemple le prénom de l'enfant)
4. Sélectionnez le switch de contrôle parental (switch GL.iNet issu de ha-glinet-router, ou tout autre switch)
5. Pour chaque jour, activez éventuellement une plage et renseignez l'heure de début et de fin

Le planning se modifie ensuite via **Configurer** sur l'entrée d'intégration.

### Exemple

| Jour | Plage |
|------|--------|
| Lundi – vendredi | 16:00 – 20:00 |
| Samedi – dimanche | 10:00 – 21:00 |

Pendant ces horaires, le switch GL.iNet de contrôle parental est éteint (accès autorisé). Le reste du temps, il est rallumé.

---

## Prérequis

- Home Assistant ≥ 2024.1.0
- Un switch existant dans Home Assistant, typiquement un switch de contrôle parental de [ha-glinet-router](https://github.com/vithurshanselvarajah/ha-glinet-router)

---

## Icône

- HACS et Home Assistant utilisent `custom_components/parental_control/brand/icon.png` et `custom_components/parental_control/brand/logo.png`
- `icon.png` à la racine sert à l'affichage GitHub
- Les entités utilisent des icônes `mdi:*`

---

## Licence

MIT License
