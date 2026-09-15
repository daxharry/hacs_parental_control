# Parental Control pour Home Assistant

<p align="center">
  <img src="icon.png" alt="Parental Control" width="128" height="128">
</p>

Planning hebdomadaire pour **désactiver automatiquement un switch de contrôle parental** pendant une plage horaire définie pour chaque jour de la semaine.

Créé à l'origine pour les switchs de contrôle parental **GL.iNet** de l'intégration [ha-glinet-router](https://github.com/vithurshanselvarajah/ha-glinet-router). Fonctionne avec n'importe quel switch Home Assistant.

Cette intégration HACS s'installe directement depuis le contenu du dépôt, sans release GitHub.

## Entités créées

- 🗓️ **Planification** *(switch)* — active ou suspend le planning
- ⏰ **Plage autorisée** *(binary sensor)*
- ⏭️ **Prochain changement**
- ℹ️ **Statut**

## Icône

- HACS et Home Assistant utilisent `custom_components/parental_control/brand/icon.png` et `custom_components/parental_control/brand/logo.png`.
- `icon.png` à la racine sert uniquement à l'affichage de cette page.
