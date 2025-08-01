# Rapport ### 1. Préparation de l'environnement de travail
- Python installé et fonctionnel
- Scrapy installé via pip
- Structure de projet correctement configurée

### 2. Création d'un projet Scrapyaux Pratiques : Extraction des Recettes de Cuisine avec Scrapy

## Informations du projet
- **Nom du projet** : `recettes_scrapy`
- **Site web cible** : PtitChef.com
- **Nombre de recettes extraites** : 3 recettes (mode test)

## Objectifs accomplis

### 1. Préparation de l'environnement de travail
- Python installé et fonctionnel
- Scrapy installé via pip
- Structure de projet correctement configurée

### 2. Création d'un projet Scrapy
```bash
scrapy startproject recettes_scrapy
cd recettes_scrapy
```

### 3. Définition de l'item
**Fichier : `recettes_scrapy/items.py`**

L'item `RecetteItem` a été défini avec les champs suivants :
- `titre` : Titre de la recette
- `ingredients` : Liste des ingrédients
- `etapes_preparation` : Étapes de préparation
- `temps_preparation` : Temps de préparation
- `temps_cuisson` : Temps de cuisson (optionnel)
- `difficulte` : Difficulté (optionnel)
- `nb_personnes` : Nombre de personnes (optionnel)
- `url` : URL de la recette
- `site_source` : Site source

### 4. Création d'un spider
**Fichier principal : `recettes_scrapy/spiders/recettes_finales.py`**

- **Nom du spider** : `recettes_finales`
- **Domaines autorisés** : `["ptitchef.com"]`
- **URLs de test** : 3 URLs de recettes individuelles pour validation

### 5. Extraction des données
Le spider extrait avec succès :
- Titre des recettes
- Liste des ingrédients
- Étapes de préparation
- Temps de préparation
- URL et métadonnées

### 6. Enregistrement des données
**Fichier : `settings.py`**
- Format de sortie : JSON
- Fichier de sortie : `recettes.json` et `test_recettes.json`
- Encodage : UTF-8

## Démarche technique

### Sélection des sélecteurs CSS et XPath

#### **1. Titre de la recette**
```python
titre_selectors = [
    'h1.recipe-title::text',
    'h1.main-title::text', 
    'h1#recipe-name::text',
    'h1::text',
    '.recipe-header h1::text'
]
```
**Rationale** : Approche progressive du sélecteur le plus spécifique au plus général.

#### **2. Ingrédients**
```python
ingredient_selectors = [
    '.recipe-ingredients li::text',
    '.ingredients-list li::text',
    '.recipe-ingredient::text',
    'li[itemprop="recipeIngredient"]::text',
    '.ingredient::text'
]
```
**Méthodes de fallback** :
- Extraction depuis JSON-LD (données structurées)
- Recherche par expressions régulières dans le texte

#### **3. Étapes de préparation**
```python
etape_selectors = [
    '.recipe-steps li::text',
    '.recipe-instructions li::text',
    '.preparation-steps li::text', 
    'ol li::text',
    '.step::text',
    'li[itemprop="recipeInstructions"]::text'
]
```

#### **4. Temps de préparation**
```python
temps_selectors = [
    '[itemprop="prepTime"]::text',
    '.prep-time::text',
    '.preparation-time::text',
    '.recipe-time .prep::text'
]
```

## Résultats obtenus

### Exemple de recette extraite avec succès :

```json
{
  "titre": "Souris d'agneau confites au miel et au thym",
  "ingredients": [
    "2 souris d'agneau",
    "1 oignon", 
    "10 cl d'eau",
    "1 c. à soupe de miel",
    "1 c. à soupe de thym",
    "1 c. à café de romarin",
    "huile d'olive",
    "sel",
    "poivre"
  ],
  "etapes_preparation": [
    "Faites chauffer de l'huile d'olive dans une grosse casserole. Faites-y revenir l'oignon préalablement émincé.",
    "Ajoutez les souris d'agneau et faites les cuire sur toutes leurs faces.",
    "Ajoutez l'eau, le miel, le thym et le romarin, salez, poivrez, et portez à ébullition. Couvrez et laissez cuire à feu très doux pendant 1 heure et 45 minutes.",
    "Passé ce temps, ôtez le couvercle, et laissez cuire 10 minutes de plus afin que la sauce réduise légèrement.",
    "Et voilà, vos souris d'agneau confites sont prêtes !"
  ],
  "temps_preparation": "2H",
  "url": "https://www.ptitchef.com/recettes/plat/souris-d-agneau-confites-au-miel-et-au-thym-fid-1570847",
  "site_source": "ptitchef.com"
}
```

## Difficultés rencontrées et solutions apportées

### **1. Problème : Sélecteurs CSS variables**
**Difficulté** : Les sites web utilisent des structures HTML différentes selon les recettes
**Solution** : Implémentation d'une approche en cascade avec multiple sélecteurs de fallback

### **2. Problème : Extraction de données JavaScript**
**Difficulté** : Certaines données étaient chargées dynamiquement
**Solution** : Extraction depuis les données JSON-LD structurées présentes dans le HTML

### **3. Problème : Formatage inconsistant**
**Difficulté** : Les étapes de préparation peuvent être fragmentées en caractères individuels
**Solution** : Mise en place de filtres de longueur minimum et validation du contenu

```python
for etape in etapes_elements:
    text = etape.get().strip() if etape.get() else ""
    if text and len(text) > 10:  # Filtre minimum
        etapes.append(text)
```

### **4. Problème : Respect des robots.txt**
**Difficulté** : Nécessité de respecter les politiques du site
**Solution** : Configuration `ROBOTSTXT_OBEY = True` et délais respectueux

```python
custom_settings = {
    'DOWNLOAD_DELAY': 1,
    'CONCURRENT_REQUESTS': 1,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 1
}
```

## Configuration technique

### **Fichier settings.py**
```python
FEEDS = {
    'recettes.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'indent': 2,
    },
}

CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2
ROBOTSTXT_OBEY = True
```

## Statistiques d'exécution

```
2025-08-01 14:51:51 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
- Requêtes totales : 4
- Réponses reçues : 4  
- Items extraits : 3
- Temps d'exécution : 6.39 secondes
- Vitesse : 30 items/minute
- Respect robots.txt : Oui
```

## Améliorations possibles

### **1. Gestion d'erreurs améliorée**
- Validation plus stricte des données extraites
- Logging détaillé des échecs d'extraction

### **2. Extension du scope**
- Ajout de pagination pour extraire plus de recettes
- Support de sites web supplémentaires

### **3. Enrichissement des données**
- Extraction d'images de recettes
- Récupération des notes et commentaires
- Calcul automatique des valeurs nutritionnelles

## Conclusion

Le projet Scrapy a été un succès technique avec :
- **Extraction réussie** de 3 recettes complètes
- **Architecture robuste** avec gestion des cas d'erreur
- **Respect des bonnes pratiques** web scraping
- **Code maintenable** et extensible

Le spider `recettes_optimisee` démontre une approche professionnelle du web scraping avec des stratégies de fallback efficaces et une gestion d'erreurs appropriée.

## Commandes d'exécution

```bash
# Lancer le spider principal
cd recettes_scrapy
scrapy crawl recettes_optimisee -o recettes_optimisee.json

# Lancer avec limite d'items
scrapy crawl recettes_optimisee -s CLOSESPIDER_ITEMCOUNT=10

# Debug mode
scrapy crawl recettes_optimisee -L DEBUG
```


