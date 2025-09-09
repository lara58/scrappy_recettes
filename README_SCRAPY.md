# Scrapy Recettes - Extraction de Recettes de Cuisine

## Description
Projet Scrapy pour extraire automatiquement des recettes de cuisine depuis PtitChef.com avec paramètre pour choisir le nombre de recettes.

## Installation
```bash
pip install scrapy
```

## Utilisation

### Important : Navigation vers le dossier du projet
```bash
# D'abord, aller dans le dossier du projet Scrapy
cd recettes_scrapy

# Puis exécuter les commandes
```

### Commandes de base
```bash
# Extraire avec nombre personnalisé (RECOMMANDÉ)
scrapy crawl recettes_optimisee -a nombre=5

# Extraire 10 recettes
scrapy crawl recettes_optimisee -a nombre=10

# Extraire sans limite (par défaut)
scrapy crawl recettes_optimisee
```

## Structure du Projet
```
recettes_scrapy/
├── scrapy.cfg
├── recettes_scrapy/
│   ├── items.py           # Définition des données
│   ├── settings.py        # Configuration
│   └── spiders/
│       └── recettes_optimisee.py  # Spider principal
```

## Sortie
Les recettes extraites sont sauvegardées dans `recettes_optimisees.json` avec :
- Titre de la recette
- Liste des ingrédients
- Étapes de préparation
- Temps de préparation/cuisson
- Difficulté
- Nombre de personnes

## Commandes Utiles
```bash
# IMPORTANT : Toujours être dans le dossier recettes_scrapy/
cd recettes_scrapy

# Extraire un nombre spécifique de recettes
scrapy crawl recettes_optimisee -a nombre=4

# Sortie personnalisée avec nombre
scrapy crawl recettes_optimisee -a nombre=20 -o mes_recettes.json

# Mode debug
scrapy crawl recettes_optimisee -a nombre=3 -L DEBUG
```

## Exemple complet
```bash
# Depuis le dossier racine du projet
PS C:\Users\narim\OneDrive\Documents\TP_SOLO_scrappy_Tahir> cd recettes_scrapy
PS C:\Users\narim\OneDrive\Documents\TP_SOLO_scrappy_Tahir\recettes_scrapy> scrapy crawl recettes_optimisee -a nombre=4
