# Guide d'Utilisation - Projet Scrapy Recettes

## Vue d'ensemble

Ce projet utilise **Scrapy** pour extraire des recettes de cuisine depuis **PtitChef.com**. Le spider peut extraire un nombre variable de recettes selon vos besoins.

## Commandes Essentielles

### Utilisation avec paramètre (Recommandé)
```bash
cd recettes_scrapy

# Extraire 5 recettes
scrapy crawl recettes_optimisee -a nombre=5

# Extraire 10 recettes
scrapy crawl recettes_optimisee -a nombre=10

# Extraire 40 recettes avec fichier personnalisé
scrapy crawl recettes_optimisee -a nombre=40 -o recettes_40.json
```

### Utilisation sans paramètre
```bash
cd recettes_scrapy
scrapy crawl recettes_optimisee
```

## Structure du Projet

```
recettes_scrapy/
├── scrapy.cfg              # Configuration Scrapy
├── recettes_scrapy/
│   ├── settings.py        # Configuration globale
│   └── spiders/
│       └── recettes_optimisee.py   # Spider principal
```

## Données Extraites

Chaque recette contient :
- **Titre** de la recette
- **Ingrédients** (liste complète)
- **Étapes de préparation** (détaillées)
- **Temps de préparation et cuisson**
- **Difficulté et nombre de personnes**
- **URL source**

## Difficultés Rencontrées et Solutions

### 1. Problème d'encodage des caractères
**Difficulté** : Les caractères accentués (é, è, à) s'affichaient mal dans les fichiers JSON.
**Solution** : Configuration UTF-8 dans `settings.py` :
```python
FEEDS = {
    'recettes_{nombre}_extraites.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 2,
    }
}
```

### 2. Extraction incomplète des données
**Difficulté** : Certaines recettes n'avaient pas toutes les informations.
**Solution** : Implémentation de sélecteurs CSS avec fallbacks multiples :
```python
# Plusieurs tentatives d'extraction
titre = response.css('h1.recipe-title::text').get()
if not titre:
    titre = response.css('.title::text').get()
```

### 3. Gestion du nombre de recettes variable
**Difficulté** : Besoin de pouvoir choisir le nombre de recettes depuis le terminal.
**Solution** : Paramètre dynamique dans le spider :
```python
def __init__(self, nombre=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if nombre:
        self.custom_settings['CLOSESPIDER_ITEMCOUNT'] = int(nombre)
```

### 4. Navigation entre pages de liste et recettes individuelles
**Difficulté** : Le site organise les recettes en pages de liste, puis pages individuelles.
**Solution** : Architecture à deux niveaux :
- `parse()` : Extrait les URLs depuis les pages de liste
- `parse_recipe()` : Extrait les données depuis chaque recette

### 5. Respect des bonnes pratiques web scraping
**Difficulté** : Éviter d'être bloqué par le site web.
**Solution** : Configuration  :
```python
DOWNLOAD_DELAY = 2          # Délai entre requêtes
ROBOTSTXT_OBEY = True       # Respect du robots.txt
CONCURRENT_REQUESTS = 1     # Une requête à la fois
```

## Dépannage Courant

### Le spider ne trouve aucune recette
```bash
# Tester en mode debug
scrapy crawl recettes_optimisee -L DEBUG
```

### Erreurs d'encodage dans le JSON
```bash
# Forcer l'encodage UTF-8
scrapy crawl recettes_optimisee -s FEED_EXPORT_ENCODING=utf8
```

### Le spider va trop vite
```bash
# Augmenter le délai entre requêtes
scrapy crawl recettes_optimisee -s DOWNLOAD_DELAY=3
```

## Exemples de Résultats

### Test avec 5 recettes
```json
{
  "titre": "Roulé de pommes de terre à la raclette",
  "ingredients": ["5 œufs", "450 gr de pommes de terre", "300 gr de Raclette"],
  "etapes_preparation": ["Pelez les pommes de terre...", "Disposez ce mélange..."],
  "temps_preparation": "30 min",
  "temps_cuisson": "30 min",
  "nb_personnes": "1 personnes",
  "url": "https://www.ptitchef.com/recettes/plat/...",
  "site_source": "ptitchef.com"
}
```

## Conclusion

Le projet permet d'extraire facilement des recettes de PtitChef.com avec un système paramétrable. Les principales difficultés (encodage, extraction incomplète, navigation multi-pages) ont été résolues pour garantir un fonctionnement fiable.

**Commande de test rapide** :
```bash
cd recettes_scrapy
scrapy crawl recettes_optimisee -a nombre=5
```

