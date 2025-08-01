
import scrapy


class RecetteItem(scrapy.Item):
    """Item pour représenter une recette de cuisine"""
    titre = scrapy.Field()
    ingredients = scrapy.Field()
    etapes_preparation = scrapy.Field()
    temps_preparation = scrapy.Field()
    temps_cuisson = scrapy.Field()
    difficulte = scrapy.Field()
    nb_personnes = scrapy.Field()
    url = scrapy.Field()
    site_source = scrapy.Field()
