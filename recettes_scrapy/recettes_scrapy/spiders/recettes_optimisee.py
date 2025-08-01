import scrapy
from recettes_scrapy.items import RecetteItem
import re
import json

class RecettesOptimiseeSpider(scrapy.Spider):
    """Spider optimisé pour extraire des recettes depuis PtitChef.com"""
    
    name = "recettes_optimisee"
    allowed_domains = ["ptitchef.com"]
    
    start_urls = [
        'https://www.ptitchef.com/recettes/plat/',
        'https://www.ptitchef.com/recettes/entree/',
        'https://www.ptitchef.com/recettes/dessert/'
    ]

    def __init__(self, nombre=None, *args, **kwargs):
        super(RecettesOptimiseeSpider, self).__init__(*args, **kwargs)
        # Paramètre pour définir le nombre de recettes à extraire
        self.nombre_recettes = int(nombre) if nombre else 40
        self.logger.info(f"Spider configuré pour extraire {self.nombre_recettes} recettes")
        
        # Configuration dynamique des settings
        self.custom_settings = {
            'DOWNLOAD_DELAY': 2,
            'CLOSESPIDER_ITEMCOUNT': self.nombre_recettes,
            'CONCURRENT_REQUESTS': 1,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
            'FEEDS': {
                f'recettes_{self.nombre_recettes}_extraites.json': {
                    'format': 'json',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'indent': 2,
                },
            }
        }

    def parse(self, response):
        """Parse les pages de listing pour extraire les URLs des recettes"""
        self.logger.info(f"Parsing listing page: {response.url}")
        
        # Sélecteurs pour les liens vers les recettes individuelles
        recipe_links = response.css('a[href*="/recettes/"]::attr(href)').getall()
        
        # Filtrer pour garder seulement les vraies recettes (avec fid-)
        recipe_urls = []
        for link in recipe_links:
            if 'fid-' in link and '/recettes/' in link:
                if not link.startswith('http'):
                    link = response.urljoin(link)
                recipe_urls.append(link)
        
        # Supprimer les doublons
        recipe_urls = list(set(recipe_urls))
        
        self.logger.info(f"Found {len(recipe_urls)} recipe URLs on page {response.url}")
        
        # Traiter chaque recette trouvée
        for url in recipe_urls[:15]:  # Limiter pour ne pas surcharger
            yield response.follow(url, self.parse_recipe)
        
        # Suivre la pagination pour trouver plus de recettes
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_recipe(self, response):
        """Parse une page de recette individuelle et extrait toutes les informations"""
        self.logger.info(f"Parsing recipe: {response.url}")
        
        item = RecetteItem()
        
        titre = self.extract_titre(response)
        item['titre'] = titre or "Titre non trouvé"
        
        ingredients = self.extract_ingredients(response)
        item['ingredients'] = ingredients
        
        etapes = self.extract_etapes(response)
        item['etapes_preparation'] = etapes
        
        temps_prep = self.extract_temps_preparation(response)
        item['temps_preparation'] = temps_prep
        
        temps_cuisson = self.extract_temps_cuisson(response)
        item['temps_cuisson'] = temps_cuisson
        
        difficulte = self.extract_difficulte(response)
        item['difficulte'] = difficulte
        
        nb_personnes = self.extract_nb_personnes(response)
        item['nb_personnes'] = nb_personnes
        
        item['url'] = response.url
        item['site_source'] = "ptitchef.com"
        
        self.logger.info(f"Successfully extracted recipe: {item['titre']}")
        yield item

    def extract_titre(self, response):
        """Extrait le titre de la recette"""
        selectors = [
            'h1.recipe-title::text',
            'h1.main-title::text',
            'h1#recipe-name::text',
            'h1::text',
            '.recipe-header h1::text',
            '[itemprop="name"]::text'
        ]
        
        for selector in selectors:
            titre = response.css(selector).get()
            if titre and titre.strip():
                return titre.strip()
        
        return None

    def extract_ingredients(self, response):
        """Extrait les ingrédients avec priorité JSON-LD"""
        ingredients_list = []
        
        json_scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in json_scripts:
            try:
                data = json.loads(script)
                
                if isinstance(data, dict) and data.get('@type') == 'Recipe':
                    recipe_ingredients = data.get('recipeIngredient', [])
                    if recipe_ingredients:
                        return recipe_ingredients
                
                elif isinstance(data, dict) and '@graph' in data:
                    for item in data['@graph']:
                        if isinstance(item, dict) and item.get('@type') == 'Recipe':
                            recipe_ingredients = item.get('recipeIngredient', [])
                            if recipe_ingredients:
                                return recipe_ingredients
                
                elif isinstance(data, list):
                    for d in data:
                        if isinstance(d, dict) and d.get('@type') == 'Recipe':
                            recipe_ingredients = d.get('recipeIngredient', [])
                            if recipe_ingredients:
                                return recipe_ingredients
                                
            except (json.JSONDecodeError, AttributeError):
                continue
        
        ingredient_selectors = [
            '.recipe-ingredients li::text',
            '.ingredients-list li::text',
            '.recipe-ingredient::text',
            'li[itemprop="recipeIngredient"]::text',
            '.ingredient-item::text',
            '.ingredients li::text'
        ]
        
        for selector in ingredient_selectors:
            elements = response.css(selector).getall()
            if elements:
                ingredients_list = [ing.strip() for ing in elements if ing.strip() and len(ing.strip()) > 2]
                if ingredients_list:
                    break
        
        if not ingredients_list:
            text_content = response.css('body').get()
            if text_content:
                patterns = [
                    r'(\d+\s*(?:gr?|grammes?|kg|kilogrammes?)\s+[^,\n\r]+)',
                    r'(\d+\s*(?:ml|cl|l|litres?)\s+[^,\n\r]+)',
                    r'(\d+\s*(?:cuillères?|c\.|càs|càc)\s+[^,\n\r]+)',
                    r'(\d+\s*[^,\n\r]+(?:oignon|carotte|tomate|pomme)s?[^,\n\r]*)'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    ingredients_list.extend(matches[:5])
                    
        return ingredients_list if ingredients_list else ["Ingrédients non trouvés"]

    def extract_etapes(self, response):
        """Extrait les étapes de préparation"""
        etapes = []
        
        json_scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in json_scripts:
            try:
                data = json.loads(script)
                instructions = self.find_instructions_in_json(data)
                if instructions:
                    return instructions
            except (json.JSONDecodeError, AttributeError):
                continue
        
        etape_selectors = [
            '.recipe-steps li',
            '.recipe-instructions li',
            '.preparation-steps li',
            '.instructions li',
            '.directions li',
            'ol li',
            '.step'
        ]
        
        for selector in etape_selectors:
            elements = response.css(selector)
            if elements:
                for element in elements:
                    text = element.css('::text').get()
                    if not text:
                        text = ''.join(element.css('*::text').getall()).strip()
                    
                    if text and len(text.strip()) > 20:
                        etapes.append(text.strip())
                
                if etapes:
                    break
        
        if not etapes:
            preparation_blocks = response.css('.preparation, .method, .recipe-method, .directions').getall()
            for block in preparation_blocks:
                sentences = re.findall(r'[A-Z][^.!?]*[.!?]', block)
                for sentence in sentences:
                    clean_sentence = re.sub(r'<[^>]+>', '', sentence).strip()
                    if len(clean_sentence) > 30:
                        etapes.append(clean_sentence)
        
        return etapes if etapes else ["Étapes non trouvées"]

    def find_instructions_in_json(self, data):
        """Recherche les instructions dans les données JSON-LD"""
        instructions = []
        
        if isinstance(data, dict):
            if data.get('@type') == 'Recipe':
                recipe_instructions = data.get('recipeInstructions', [])
                instructions = self.parse_instructions(recipe_instructions)
            elif '@graph' in data:
                for item in data['@graph']:
                    if isinstance(item, dict) and item.get('@type') == 'Recipe':
                        recipe_instructions = item.get('recipeInstructions', [])
                        instructions = self.parse_instructions(recipe_instructions)
                        if instructions:
                            break
        elif isinstance(data, list):
            for d in data:
                if isinstance(d, dict) and d.get('@type') == 'Recipe':
                    recipe_instructions = d.get('recipeInstructions', [])
                    instructions = self.parse_instructions(recipe_instructions)
                    if instructions:
                        break
        
        return instructions

    def parse_instructions(self, recipe_instructions):
        """Parse les instructions depuis JSON-LD"""
        instructions = []
        
        for instruction in recipe_instructions:
            if isinstance(instruction, dict):
                text = instruction.get('text', '')
            elif isinstance(instruction, str):
                text = instruction
            else:
                text = str(instruction)
            
            if text and len(text.strip()) > 10:
                instructions.append(text.strip())
        
        return instructions

    def extract_temps_preparation(self, response):
        """Extrait le temps de préparation"""
        selectors = [
            '[itemprop="prepTime"]::text',
            '.prep-time::text',
            '.preparation-time::text',
            '.recipe-time .prep::text',
            '.time-prep::text'
        ]
        
        for selector in selectors:
            temps = response.css(selector).get()
            if temps and temps.strip():
                return temps.strip()
        
        time_pattern = re.search(r'(?:préparation|prep).*?(\d+)\s*(?:min|minutes|h|heures?)', response.text, re.IGNORECASE)
        if time_pattern:
            return time_pattern.group(1) + " min"
        
        return "Non spécifié"

    def extract_temps_cuisson(self, response):
        """Extrait le temps de cuisson"""
        selectors = [
            '[itemprop="cookTime"]::text',
            '.cook-time::text',
            '.cooking-time::text',
            '.recipe-time .cook::text'
        ]
        
        for selector in selectors:
            temps = response.css(selector).get()
            if temps and temps.strip():
                return temps.strip()
        
        time_pattern = re.search(r'(?:cuisson|cook).*?(\d+)\s*(?:min|minutes|h|heures?)', response.text, re.IGNORECASE)
        if time_pattern:
            return time_pattern.group(1) + " min"
        
        return "Non spécifié"

    def extract_difficulte(self, response):
        """Extrait la difficulté"""
        selectors = [
            '.difficulty::text',
            '.recipe-difficulty::text',
            '[itemprop="difficulty"]::text',
            '.level::text'
        ]
        
        for selector in selectors:
            difficulte = response.css(selector).get()
            if difficulte and difficulte.strip():
                return difficulte.strip()
        
        return "Non spécifiée"

    def extract_nb_personnes(self, response):
        """Extrait le nombre de personnes"""
        selectors = [
            '[itemprop="recipeYield"]::text',
            '.servings::text',
            '.recipe-yield::text',
            '.nb-personnes::text',
            '.portions::text'
        ]
        
        for selector in selectors:
            nb = response.css(selector).get()
            if nb and nb.strip():
                return nb.strip()
        
        persons_pattern = re.search(r'(\d+)\s*(?:personnes?|parts?|portions?)', response.text, re.IGNORECASE)
        if persons_pattern:
            return persons_pattern.group(1) + " personnes"
        
        return "Non spécifié"
