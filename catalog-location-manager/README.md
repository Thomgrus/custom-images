# Catalog Location Manager

Le Catalog Location Manager est un outil en ligne de commande conçu pour faciliter la gestion des entrées dans la section `spec.targets` de fichiers YAML, typiquement utilisés dans des configurations comme `catalog-info.yaml`. Cet outil permet d'ajouter ou de supprimer des références à des catalogues de manière simple et efficace, tout en préservant la structure et les commentaires du fichier YAML original.

## Fonctionnalités

- **Ajout d'éléments** : Permet d'ajouter une nouvelle référence de catalogue dans `spec.targets` si elle n'existe pas déjà.
- **Suppression d'éléments** : Supprime une référence de catalogue existante dans `spec.targets` et, si le fichier cible existe, le supprime également.

## Prérequis

Avant d'utiliser le Catalog Location Manager, assurez-vous que vous avez les éléments suivants installés sur votre système :
- Python 3.6 ou version ultérieure
- pip (gestionnaire de paquets Python)

## Installation

**Installation des dépendances** : Installez les dépendances nécessaires en exécutant la commande suivante dans le répertoire contenant le fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

## Utilisation

Le Catalog Location Manager est utilisé via la ligne de commande en suivant la syntaxe ci-dessous :

```bash
python catalog-location-manager.py <action> <nom_du_catalogue>
```

- `<action>` : spécifie l'action à effectuer. Utilisez `add` pour ajouter un élément ou `remove` pour supprimer un élément.
- `<nom_du_catalogue>` : le nom du catalogue à ajouter ou à supprimer dans `spec.targets`.

### Exemples

- **Ajouter un catalogue** : Pour ajouter un catalogue nommé `example-catalog` :

    ```bash
    python catalog-location-manager.py add example-catalog
    ```

- **Supprimer un catalogue** : Pour supprimer un catalogue nommé `example-catalog` :

    ```bash
    python catalog-location-manager.py remove example-catalog
    ```
